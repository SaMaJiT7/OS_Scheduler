class FrameManager:
    def __init__(self, n_frames):
        self.n_frames = n_frames
        self.frames = [None] * n_frames

    def get_free_frame(self):
        for i in range(self.n_frames):
            if self.frames[i] is None:
                return i
        return None

    def load_page(self, page):
        free_frame = self.get_free_frame()
        if free_frame is not None:
            self.frames[free_frame] = page
            return free_frame

    def evict_page(self, page_id):
        for i in range(self.n_frames):
            if self.frames[i] is not None and self.frames[i].page_id == page_id:
                self.frames[i] = None
                return True
        return False

    def get_all_pages(self):
        return [frame for frame in self.frames if frame is not None]
