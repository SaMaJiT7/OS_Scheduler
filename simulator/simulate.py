from simulator.page import Page
from simulator.page_table import PageTable
from simulator.frame_manager import FrameManager
from simulator.belady_helper import build_next_occurrence


def simulate(trace, algorithm, n_frames, next_occurrence=None):
    counter = 0
    hits = 0
    faults = 0
    fault_log = []

    page_table = PageTable()
    frame_manager = FrameManager(n_frames)

    algo_name = type(algorithm).__name__
    if algo_name == "Belady" and next_occurrence is None:
        next_occurrence = build_next_occurrence(trace)

    for i, page_id in enumerate(trace):
        counter += 1

        if page_table.is_loaded(page_id):
            hits += 1
            page_table.get_page(page_id).last_accessed = counter
        else:
            faults += 1

            free_frame = frame_manager.get_free_frame()

            if free_frame is not None:
                new_page = Page(page_id, timestamp=counter)
                frame_manager.load_page(new_page)
                page_table.add_page(new_page)
            else:
                victim_id = algorithm.select_victim(
                    page_table,
                    trace=trace,
                    current_index=i,
                    next_occurrence=next_occurrence,
                )
                frame_manager.evict_page(victim_id)
                page_table.remove_page(victim_id)

                new_page = Page(page_id, timestamp=counter)
                frame_manager.load_page(new_page)
                page_table.add_page(new_page)

            fault_log.append({"access": counter, "page": page_id})

    return {
        "hits": hits,
        "faults": faults,
        "hit_rate": hits / counter if counter else 0,
        "fault_rate": faults / counter if counter else 0,
        "fault_log": fault_log,
    }
