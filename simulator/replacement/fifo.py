from simulator.replacement.base import BaseReplacement


class FIFO(BaseReplacement):
    def select_victim(self, page_table, **kwargs):
        pages = page_table.get_all_pages()
        victim = min(pages, key=lambda p: p.loaded_at)
        return victim.page_id
