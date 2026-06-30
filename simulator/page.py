class Page:
    def __init__(self, page_id, timestamp):
        self.page_id = page_id
        self.loaded_at = timestamp
        self.last_accessed = timestamp
