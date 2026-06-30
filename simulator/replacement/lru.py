from simulator.replacement.base import BaseReplacement


class LRU(BaseReplacement):
    def select_victim(self, page_table, **kwargs):
        pages = page_table.get_all_pages()
        victim = min(pages, key=lambda p: p.last_accessed)
        return victim.page_id
