from simulator.replacement.base import BaseReplacement


class Belady(BaseReplacement):
    def select_victim(self, page_table, **kwargs):
        current_index = kwargs.get("current_index", 0)
        next_occurrence = kwargs.get("next_occurrence", {})

        pages = page_table.get_all_pages()
        n = None

        for pid_map in next_occurrence.values():
            n = len(pid_map)
            break

        victim_id = None
        furthest_next = -1

        for page in pages:
            pid = page.page_id
            pid_map = next_occurrence.get(pid)
            if pid_map is None:
                return pid

            next_idx = pid_map[current_index] if current_index < n else None
            if next_idx is None:
                return pid

            if next_idx > furthest_next:
                furthest_next = next_idx
                victim_id = pid

        return victim_id
