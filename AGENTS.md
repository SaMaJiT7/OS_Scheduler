# AGENTS.md

## Project Status
**Phase 1 complete** — OS Memory Simulator built and verified.
**Phase 2 complete** — Dataset `lstm_ready_dataset.npz` provided (4.4M samples, window=50, vocab=395,859).
**Phase 3 in progress** — LSTM model in `ml/`, training script in `notebooks/train_lstm.ipynb` (Colab).
See `PROJECT_CONTEXT.md` for full roadmap.

## Architecture Rules (Do Not Break)
- `simulate()` handles ALL bookkeeping — hits, faults, timestamps, loading, evicting
- Algorithm classes ONLY implement `select_victim(page_table, **kwargs)` — nothing else
- `select_victim()` called ONLY when fault occurs AND all frames are full
- Timestamp = integer access counter (not real clock time)
- `Page` objects created dynamically on first access
- `loaded_at` never changes; `last_accessed` updates on every hit
- All algorithms use the same `simulate()` — only the algorithm object differs

## Verification Test
```bash
.env/bin/python -c "
from simulator.simulate import simulate
from simulator.replacement.fifo import FIFO
from simulator.replacement.lru import LRU
from simulator.replacement.belady import Belady
trace = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
frames = 3
for algo, name in [(FIFO(), 'FIFO'), (LRU(), 'LRU'), (Belady(), 'Belady')]:
    result = simulate(trace, algo, frames)
    print(f'{name}: {result[\"faults\"]} faults')
"
```
**Expected:** FIFO=9, LRU=10, Belady=7

## Belady Optimization
Precomputes `next_occurrence[pid][i]` via single right-to-left sweep (`belady_helper.py`). Avoids O(T) slice per fault. `simulate()` auto-builds it if `next_occurrence=None` is passed and algorithm is Belady. Passes `(trace, current_index, next_occurrence)` to `select_victim` via `**kwargs`.

## Colab Training Workflow
- **Drive for Desktop SKIPPED** — in Mirror mode, mid-initial-download, mount is read-only for shell operations.
- **Code path:** Colab clones the repo directly from GitHub (`github.com/SaMaJiT7/OS_Scheduler`).
- **Data path:** upload `lstm_ready_dataset.npz` via Colab's file picker each session, or use `google.colab.files.upload()` in a cell.
- **Artifacts path:** `best_model.pt` + `vocab.json` are saved to the cloned repo in Colab, then committed + pushed from Colab back to GitHub. You `git pull` in the local repo to get them.

## Python Environment
- Venv at `.env/` (Python 3.14)
- Use `.env/bin/python` for all commands
- Installed: `numpy` (only). PyTorch only needed in Colab.
- No `requirements.txt` yet (Phase 7)

## Source Layout
```
simulator/                       # Phase 1 (done)
├── page.py
├── frame_manager.py
├── page_table.py
├── simulate.py
├── belady_helper.py
└── replacement/{base,fifo,lru,belady}.py

ml/                              # Phase 3 (in progress)
├── __init__.py
├── model.py                     # MIRROR of LSTM class in notebook — keep in sync
├── vocab.py                     # vocab load + page_id ↔ idx helpers
└── predict.py                   # load checkpoint + run inference

notebooks/
└── train_lstm.ipynb             # CANONICAL LSTM class + training script

ml/checkpoints/                  # best_model.pt (downloaded from Colab)
vocab.json                       # vocab mapping (downloaded from Colab)
```

## Phase 3 Build Plan
- **Vocab:** top-50k + 1 `<unk>` = 50,001 classes (~98% coverage)
- **Train/val split:** 80/20, seed=42
- **Epochs:** 3 + early stop (patience=2 on val loss)
- **Architecture:** Embedding(50_001, 64) → LSTM(64, 128, 2, dropout=0.2) → Linear(128, 50_001), last-step output
- **Optimizer:** Adam, lr=1e-3
- **Batch size:** 64

## Next Phase (Phase 4)
After Phase 3 trains successfully: build `simulator/replacement/neural.py` (uses `ml.predict`) to plug the trained model into the simulator. Then compare fault counts vs LRU/FIFO/Belady.
