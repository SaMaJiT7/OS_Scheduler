# AGENTS.md

## Project Status
**Phase 1 complete** — OS Memory Simulator built and verified. Phases 2–7 not started.
See `PROJECT_CONTEXT.md` for full roadmap and design decisions.

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

## Python Environment
- Venv at `.env/` (Python 3.14)
- Use `.env/bin/python` for all commands
- No `requirements.txt` yet (Phase 7)

## Source Layout
```
simulator/
├── page.py              # Page(page_id, timestamp)
├── frame_manager.py     # FrameManager(n_frames) — slots, get_free/load/evict
├── page_table.py        # PageTable — dict page_id→Page
├── simulate.py          # simulate(trace, algorithm, n_frames, next_occurrence=None)
├── belady_helper.py     # build_next_occurrence(trace)
└── replacement/
    ├── base.py          # BaseReplacement (ABC)
    ├── fifo.py          # min by loaded_at
    ├── lru.py           # min by last_accessed
    └── belady.py        # furthest next_occurrence
```

## Next Phase (Phase 2)
Build `trace/generator.py` (synthetic patterns) and `trace/dataset.py` (sliding window X/Y for LSTM). Skip `loader.py` (Valgrind) and `producer.py` (RabbitMQ) for now.
