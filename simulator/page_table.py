class PageTable:
    def __init__(self):
        self.pages = {}

    def is_loaded(self, page_id):
        return page_id in self.pages

    def get_page(self, page_id):
        return self.pages.get(page_id, None)

    def add_page(self, page):
        self.pages[page.page_id] = page

    def remove_page(self, page_id):
        if page_id in self.pages:
            del self.pages[page_id]

    def get_all_pages(self):
        return list(self.pages.values())
