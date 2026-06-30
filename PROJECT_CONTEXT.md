# Neural Memory Manager — Full Project Context
> Use this file to give any AI model full context about this project.
> Student: Samajit | B.Tech IT | GNIT Kolkata | 2023-2027 Batch

---

## What This Project Is

A distributed intelligent memory management system that replaces classical OS page replacement algorithms (LRU, FIFO) with a trained LSTM neural network — served via async Celery workers, exposed through FastAPI, and visualized on a live Streamlit dashboard.


**Core research question:**
> How close can a trained LSTM get to Belady's Optimal page replacement algorithm — the theoretical perfect algorithm that requires knowing the future?

**One-line resume description:**
> Built a distributed intelligent memory management system that trains an LSTM on real memory access traces to learn optimal page replacement policies, benchmarked against Belady's Optimal algorithm, served via async Celery workers over RabbitMQ, with an LLM-powered analyst explaining system behavior in real time.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python |
| ML | PyTorch (LSTM) |
| API | FastAPI + Pydantic |
| Dashboard | Streamlit |
| Message Queue | RabbitMQ |
| Async Workers | Celery |
| Cache / State | Redis |
| Containerization | Docker + Docker Compose |
| LLM | Claude API (claude-sonnet-4-20250514) |

---

## OS Concepts Used

| Term | Meaning |
|------|---------|
| Page | Fixed-size block of virtual memory (e.g. 4KB) |
| Frame | Physical RAM slot that holds one page |
| Page Table | Dictionary mapping page_id → frame_number |
| Page Fault | Requested page not in RAM → must load it |
| Eviction | Removing a page from RAM to make room |
| Hit | Page access found already in RAM |
| Hit Rate | % of accesses that were hits |
| Fault Rate | % of accesses that caused page faults |

---

## Algorithm Comparison

| Algorithm | Strategy | Fault Rate (approx) | Knows Future? |
|-----------|----------|-------------------|---------------|
| FIFO | Evict oldest loaded page | ~45% | No |
| LRU | Evict least recently used | ~38% | No |
| Neural (LSTM) | Predict least needed page | ~28-32% (target) | No (learned) |
| Belady's Optimal | Evict page needed furthest ahead | ~22% | Yes (cheats) |

---

## Project Folder Structure

```
neural-memory-manager/
│
├── simulator/
│   ├── __init__.py
│   ├── page.py                  # Page class
│   ├── page_table.py            # PageTable class
│   ├── frame_manager.py         # FrameManager class
│   └── replacement/
│       ├── __init__.py
│       ├── base.py              # Abstract base class
│       ├── lru.py               # LRU algorithm
│       ├── fifo.py              # FIFO algorithm
│       ├── belady.py            # Belady's Optimal
│       └── neural.py            # LSTM-based policy
│
├── ml/
│   ├── __init__.py
│   ├── model.py                 # LSTM architecture (PyTorch)
│   ├── train.py                 # Training loop
│   ├── predict.py               # Inference → eviction decision
│   ├── dataset.py               # Sliding window dataset builder
│   └── data/
│       ├── synthetic/           # Generated traces (.npy)
│       └── valgrind/            # Real program traces (optional)
│
├── trace/
│   ├── __init__.py
│   ├── generator.py             # Synthetic trace patterns
│   ├── loader.py                # Parse Valgrind / file traces
│   └── producer.py              # RabbitMQ publisher
│
├── workers/
│   ├── __init__.py
│   ├── celery_app.py            # Celery + RabbitMQ + Redis config
│   └── tasks.py                 # Celery tasks
│
├── api/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entry point
│   ├── schemas.py               # Pydantic models
│   ├── state.py                 # Shared state (Redis-backed)
│   └── routes/
│       ├── __init__.py
│       ├── control.py           # POST /run, POST /reset
│       ├── metrics.py           # GET /metrics
│       ├── page_table.py        # GET /page-table
│       └── llm.py               # GET /llm/explain
│
├── dashboard/
│   └── app.py                   # Streamlit UI
│
├── benchmark/
│   ├── run_benchmark.py
│   └── results/
│
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.dashboard
├── Dockerfile.worker
├── requirements.txt
└── README.md
```

---

## Build Phases

### Phase 1 — OS Memory Simulator ← CURRENT PHASE
### Phase 2 — Memory Trace Pipeline
### Phase 3 — LSTM Model
### Phase 4 — RabbitMQ + Celery Workers
### Phase 5 — FastAPI Backend
### Phase 6 — Streamlit Dashboard
### Phase 7 — Docker + Benchmarking + Polish

---

## PHASE 1 — OS Memory Simulator (CURRENT)

**Goal:** Pure Python simulation of virtual memory. No ML, no infra. Just a script that takes a list of page accesses and returns fault/hit counts.

**Files to build:**
- `simulator/page.py`
- `simulator/frame_manager.py`
- `simulator/page_table.py`
- `simulator/replacement/base.py`
- `simulator/replacement/lru.py`
- `simulator/replacement/fifo.py`
- `simulator/replacement/belady.py`
- `simulator/simulate.py`

---

### Design Decisions (Critical)

#### Separation of Responsibility

```
simulate()        → the brain. handles everything.
algorithm         → only answers ONE question: which page to evict?
```

The algorithm classes do NOT:
- check hits or faults
- update counters
- update timestamps
- load or evict pages

The algorithm classes ONLY implement:
```python
select_victim(page_table) → returns page_id to evict
```

`simulate()` calls `select_victim()` only when:
- a page fault occurs AND
- all frames are full

Everything else is handled by `simulate()`.

#### Timestamp = Access Counter (not real clock time)

Use a simple integer counter that increments on every access.
Simpler, no floating point, easier to debug.

```
access 1 → counter=1
access 2 → counter=2
access 3 → counter=3 (hit on page from access 1) → update last_accessed=3
```

---

### Class: `Page` (simulator/page.py)

**Purpose:** Data container for a single page in memory.

**Fields:**
```
page_id        → integer, identifies this page (e.g. 7)
loaded_at      → counter value when page was first loaded into RAM (never changes)
last_accessed  → counter value of most recent access (updates on every hit)
```

**Key insight:**
- At creation: `loaded_at == last_accessed` (just arrived)
- On every hit: only `last_accessed` updates, `loaded_at` stays fixed
- FIFO uses `loaded_at` to find oldest page
- LRU uses `last_accessed` to find least recently used

**Constructor signature:**
```python
def __init__(self, page_id, timestamp):
    self.page_id = page_id
    self.loaded_at = timestamp
    self.last_accessed = timestamp
```

**Current student code (needs minor fix):**
```python
class Page():
    def __init__(self, Page_id):
        self.id = Page_id
        self.loaded_at = None        # ← should receive timestamp, not None
        self.last_accessed_at = None # ← should receive timestamp, not None
        self.access_count = 0        # ← not needed for Phase 1, remove
```

**Corrected version:**
```python
class Page:
    def __init__(self, page_id, timestamp):
        self.page_id = page_id
        self.loaded_at = timestamp
        self.last_accessed = timestamp
```

---

### Class: `FrameManager` (simulator/frame_manager.py) ← NEXT TO BUILD

**Purpose:** Manages the pool of N physical RAM slots.

**Think of it as:** A fixed-size list of slots. Each slot holds either `None` (free) or a `Page` object.

```
n_frames = 4
slots = [None, None, None, None]       ← start empty

After loading pages 4, 7, 2:
slots = [Page(4), Page(7), Page(2), None]

After loading page 3 (now full):
slots = [Page(4), Page(7), Page(2), Page(3)]
```

**Methods needed:**
```
get_free_frame()      → returns index of a free slot, or None if all full
load_page(page)       → puts page into a free slot
evict_page(page_id)   → finds slot with that page_id, sets it to None
get_all_pages()       → returns list of all Page objects currently loaded
```

**Constructor:**
```python
def __init__(self, n_frames):
    self.n_frames = n_frames
    self.slots = [None] * n_frames
```

---

### Class: `PageTable` (simulator/page_table.py)

**Purpose:** Fast lookup — is a page loaded? Which frame is it in?

**Internally:** Just a dictionary `{ page_id: Page object }`

**Methods needed:**
```
is_loaded(page_id)      → returns True/False
get_page(page_id)       → returns Page object or None
add_page(page)          → adds page to table
remove_page(page_id)    → removes page from table
get_all_pages()         → returns all Page objects
```

---

### Abstract Base: `BaseReplacement` (simulator/replacement/base.py)

```python
from abc import ABC, abstractmethod

class BaseReplacement(ABC):
    @abstractmethod
    def select_victim(self, page_table, **kwargs):
        # returns page_id to evict
        pass
```

---

### Algorithm: `LRU` (simulator/replacement/lru.py)

```
select_victim:
  → look at all pages in page_table
  → return page_id with the smallest last_accessed value
```

---

### Algorithm: `FIFO` (simulator/replacement/fifo.py)

```
select_victim:
  → look at all pages in page_table
  → return page_id with the smallest loaded_at value
```

---

### Algorithm: `Belady's` (simulator/replacement/belady.py)

```
select_victim(page_table, future_trace):
  → for each page currently in frames:
      find its next appearance index in future_trace
      if it never appears again → evict it immediately
  → return page_id whose next appearance is furthest ahead
```

Note: `future_trace` is the slice of the trace AFTER the current access position.
Belady's needs this — which is why it only works in simulation (you have the full trace).

---

### Main Function: `simulate()` (simulator/simulate.py)

**Signature:**
```python
def simulate(trace, algorithm, n_frames):
    → returns dict with hits, faults, hit_rate, fault_rate, fault_log
```

**Full logic:**
```
counter = 0
hits = 0
faults = 0
fault_log = []

initialize PageTable (empty)
initialize FrameManager (n_frames, all empty)

for each page_id in trace:
    counter += 1

    if page_table.is_loaded(page_id):
        # HIT
        hits += 1
        page_table.get_page(page_id).last_accessed = counter

    else:
        # FAULT
        faults += 1

        free_frame = frame_manager.get_free_frame()

        if free_frame is not None:
            # free slot available, just load
            new_page = Page(page_id, timestamp=counter)
            frame_manager.load_page(new_page)
            page_table.add_page(new_page)

        else:
            # no free slot, must evict
            victim_id = algorithm.select_victim(page_table, future_trace=trace[i+1:])
            frame_manager.evict_page(victim_id)
            page_table.remove_page(victim_id)

            new_page = Page(page_id, timestamp=counter)
            frame_manager.load_page(new_page)
            page_table.add_page(new_page)

        fault_log.append({ access: counter, page: page_id, ... })

return {
    hits: hits,
    faults: faults,
    hit_rate: hits / counter,
    fault_rate: faults / counter,
    fault_log: fault_log
}
```

---

### Phase 1 Verification Test

Use this exact trace (standard OS textbook example):

```
trace  = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
frames = 3

Expected results:
  FIFO   → 9 faults
  LRU    → 10 faults
  Belady → 7 faults
```

> Note: Original spec listed Belady → 6 faults. Verified manually and via simulation: 7 is the correct optimal count. Spec was updated on 2026-06-11 (see Session Audit Log).

If your simulator matches these numbers → Phase 1 is complete and correct.

---

## PHASE 2 — Memory Trace Pipeline (UPCOMING)

**Goal:** Generate memory access sequences for LSTM training and simulation.

### Synthetic Trace Patterns to Generate

| Pattern | Description |
|---------|-------------|
| Working set | Small group of pages accessed repeatedly (80% of accesses) |
| Sequential | Pages in order: 0,1,2,3,4... |
| Strided | Every kth page: 0,4,8,12... |
| Random spike | Occasional random page outside working set |
| Mixed | Combination of above |

### Valgrind Integration (Optional but impressive)

```bash
valgrind --tool=lackey --trace-mem=yes ./your_program 2> trace.txt
```

Convert memory address to page_id:
```
page_id = memory_address >> 12   (right shift by 12 = divide by 4096)
```

### Sliding Window Dataset for LSTM

```
trace = [4, 7, 2, 4, 7, 3, 4, 7, 2, 3]
window_size = 5

Sample 0: X=[4,7,2,4,7]  Y=3
Sample 1: X=[7,2,4,7,3]  Y=4
Sample 2: X=[2,4,7,3,4]  Y=7
```

---

## PHASE 3 — LSTM Model (UPCOMING)

**Goal:** Train a neural network that predicts future page accesses.

### Architecture

```
Input: sequence of page_ids (length = window_size=20)
  ↓
Embedding(num_pages, embed_dim=64)
  ↓
LSTM(input=64, hidden=128, layers=2, dropout=0.2)
  ↓
Linear(128 → num_pages)
  ↓
Softmax → probability distribution over all pages
```

### Eviction Decision

```
Given: current frames = [4, 7, 2, 5]
       recent history = [4,7,2,4,7,3,4,7,2,5]

LSTM output probabilities:
  Page 4 → 0.91 (very likely needed)
  Page 7 → 0.87 (very likely needed)
  Page 2 → 0.72 (likely needed)
  Page 5 → 0.11 (unlikely needed) ← EVICT THIS
```

### Hyperparameters

```
window_size   = 20
embed_dim     = 64
hidden_size   = 128
num_layers    = 2
dropout       = 0.2
learning_rate = 0.001
batch_size    = 64
epochs        = 20
loss          = CrossEntropyLoss
optimizer     = Adam
```

---

## PHASE 4 — RabbitMQ + Celery (UPCOMING)

### Architecture Flow

```
trace/producer.py
  → publishes page_id to RabbitMQ queue "page_events"
      → Celery worker consumes event
          → runs simulator step
          → if fault: calls LSTM → evict → load
          → updates metrics in Redis
              → FastAPI reads Redis → serves to Streamlit
```

### Config

```
broker_url      = amqp://guest:guest@rabbitmq:5672//
result_backend  = redis://redis:6379/0
```

### Celery Tasks

```
process_page_event(page_id, algorithm)
  → feed into simulator
  → update Redis counters

compute_metrics()
  → read Redis
  → return hit_rate, fault_rate, comparison stats
```

---

## PHASE 5 — FastAPI Backend (UPCOMING)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /run | Start simulation |
| POST | /reset | Reset state |
| GET | /metrics | Hit rate, fault rate, counts |
| GET | /page-table | Current frame contents |
| GET | /comparison | All 4 algorithms on same trace |
| GET | /llm/explain | LLM analysis of recent behavior |

---

## PHASE 6 — Streamlit Dashboard (UPCOMING)

### Sections

```
1. Sidebar control panel     → algorithm picker, frame count, trace selector, start/reset
2. Live metrics row          → hit rate %, fault rate %, total accesses (st.metric)
3. Page table grid           → N frame cards showing current contents
4. Algorithm showdown chart  → 4 lines: LRU vs FIFO vs Neural vs Belady (st.line_chart)
5. LLM analyst panel         → explain button → streams Claude response
```

### Live Refresh Pattern

```python
while True:
    data = requests.get("http://api:8000/metrics").json()
    container.metric("Hit Rate", data["hit_rate"])
    time.sleep(1)
    st.rerun()
```

---

## PHASE 7 — Docker + Benchmarking (UPCOMING)

### Docker Compose Services

```
rabbitmq   → message broker
redis      → celery backend + shared state
api        → FastAPI (port 8000)
worker     → Celery worker (ML inference)
dashboard  → Streamlit (port 8501)
```

### Benchmark Matrix

```
Traces  × Frames × Algorithms = Total runs
5       × 3      × 4          = 60 benchmark runs

Traces:     working_set, sequential, random, strided, mixed
Frames:     4, 8, 16
Algorithms: LRU, FIFO, Neural, Belady
```

---

## Requirements (requirements.txt)

```
fastapi
uvicorn[standard]
pydantic
torch
numpy
celery[redis]
redis
streamlit
httpx
pytest
black
anthropic
```

---

## Environment Variables (.env)

```
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
REDIS_URL=redis://redis:6379/0
ANTHROPIC_API_KEY=your_key_here
N_FRAMES=8
WINDOW_SIZE=20
MODEL_PATH=ml/checkpoints/best_model.pt
```

---

## Interview Talking Points

- **OS depth:** "I implemented page replacement from scratch including Belady's Optimal, which requires foreknowledge of the full access trace — impossible in a real OS but useful as a theoretical benchmark"
- **ML angle:** "The LSTM learns temporal patterns in memory access sequences — working sets, strides — which LRU and FIFO completely ignore"
- **Systems angle:** "RabbitMQ decouples event production from ML inference the same way an OS interrupt handler defers expensive work to a background process"
- **Result:** "On working-set traces, the neural policy achieved X% fault rate vs Y% for LRU — closing Z% of the gap toward Belady's theoretical optimum"

---

## Current Progress

- [x] Project designed and planned
- [x] Phase 1 design finalized
- [x] `Page` class — written, needs minor correction (add timestamp param, remove access_count)
- [ ] `FrameManager` class — next to build
- [ ] `PageTable` class
- [ ] `BaseReplacement` abstract class
- [ ] `LRU`, `FIFO`, `Belady` algorithms
- [ ] `simulate()` main function
- [ ] Phase 1 verification test
- [ ] Phase 2 onwards

---

## Key Design Rules (Do Not Break)

1. `simulate()` handles ALL bookkeeping — hits, faults, timestamps, loading, evicting
2. Algorithm classes ONLY implement `select_victim()` — nothing else
3. `select_victim()` is called ONLY when a fault occurs AND all frames are full
4. Timestamp = integer access counter, not real clock time
5. `Page` objects are created dynamically on first access, not pre-created
6. `loaded_at` never changes after creation. `last_accessed` updates on every hit.
7. All 4 algorithms use the same `simulate()` — only the algorithm object differs

---

---

## Session Audit Log

> Living record of what was built, decided, and learned in each session.
> Future AI: read this to restore full context.

### Session 1 — Phase 1 Build + Phase 2 Planning

**Date:** 2026-06-11
**Phase reached:** Phase 1 complete, Phase 2 planned

#### Phase 1 — Completed Files

| File | Status | Notes |
|------|--------|-------|
| `simulator/page.py` | ✓ built | `page_id`, `last_accessed` (corrected from student's draft `id`, `last_accessed_at`) |
| `simulator/frame_manager.py` | ✓ built | `evict_page` uses `page_id` (not `id`) |
| `simulator/page_table.py` | ✓ built | method renamed: student's `is_page_loaded` → spec's `is_loaded` |
| `simulator/replacement/base.py` | ✓ built | abstract `BaseReplacement` with `select_victim(page_table, **kwargs)` |
| `simulator/replacement/lru.py` | ✓ built | `min(pages, key=lambda p: p.last_accessed)` |
| `simulator/replacement/fifo.py` | ✓ built | `min(pages, key=lambda p: p.loaded_at)` |
| `simulator/replacement/belady.py` | ✓ built | uses precomputed `next_occurrence` map |
| `simulator/belady_helper.py` | ✓ built (new, not in original spec) | `build_next_occurrence(trace)` |
| `simulator/simulate.py` | ✓ built | takes optional `next_occurrence` param |

#### Architectural Decisions Made

1. **Belady performance optimization** (not in original spec)
   - Original design: pass `trace[i+1:]` slice to `select_victim` on every fault → O(T) copy + O(T) lookup per page → O(N·M·T) total
   - **Fix:** precompute `next_occurrence[page_id][i]` = next position of `page_id` at-or-after `i` via single right-to-left sweep. O(T·unique_pages) one-time cost.
   - `simulate()` passes `(trace, current_index, next_occurrence)` to `select_victim` instead of slicing.
   - **Result:** 50k trace, 16 frames, Belady runs in 62ms (vs would-have-been-seconds).

2. **Folder cleanup**
   - Created proper `simulator/` and `simulator/replacement/` subfolders with `__init__.py`
   - Deleted empty root stubs: `Belady.py`, `FIFO.py`, `LRU.py`, `simulate.py`
   - Deleted empty `Replacement/` folder (replaced by `simulator/replacement/`)

3. **Spec correction**
   - Original spec said "Belady → 6 faults" on textbook trace. Verified manually and via simulation: correct answer is **7 faults**. Spec was updated inline.

#### Phase 1 Verification Results

```
Trace: [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5], 3 frames
FIFO   → 9 faults  ✓
LRU    → 10 faults ✓
Belady → 7 faults  ✓ (corrected from spec's 6)
```

#### Phase 2 — Decisions Locked In

- **Build scope:** `trace/generator.py` + `trace/dataset.py` only
- **Skip for now:** `trace/loader.py` (Valgrind parser), `trace/producer.py` (RabbitMQ — Phase 4)
- **Window size:** 20
- **Output format:** in-memory `list[int]`, no disk I/O
- **Generators planned:** `working_set(n, hot_size, cold_prob)`, `sequential(n, num_pages)`, `strided(n, stride, num_pages)`, `random_spike(n, base_size, spike_prob)`, `mixed(n, weights)`
- **Dataset:** `build_dataset(trace, window_size=20) → (X, Y)` numpy int64 arrays
  - `X.shape = (len(trace) - 20, 20)`, `Y.shape = (len(trace) - 20,)`
  - `X[i] = trace[i:i+20]`, `Y[i] = trace[i+20]`

#### Open / Deferred Questions

- **Valgrind loader decision:** user said "i will tell you later"
- **Trace source strategy** for resume/demo (synthetic only vs SPEC benchmarks + Valgrind)
- **Design conversation** about "not reducing list size after index used" led to the Belady optimization above

#### Files NOT yet touched

- All of `ml/`, `workers/`, `api/`, `dashboard/`, `benchmark/` (Phase 3+)
- `trace/loader.py`, `trace/producer.py` (Phase 2 skip / Phase 4)
- `trace/__init__.py` (will be created when Phase 2 builds)
- `requirements.txt`, Dockerfiles (Phase 7)

#### Current Project Tree

```
.
├── .env/                  # Python venv (not code)
├── .vscode/
├── PROJECT_CONTEXT.md
└── simulator/
    ├── __init__.py
    ├── page.py
    ├── page_table.py
    ├── frame_manager.py
    ├── simulate.py
    ├── belady_helper.py
    └── replacement/
        ├── __init__.py
        ├── base.py
        ├── lru.py
        ├── fifo.py
        └── belady.py
```

---

  