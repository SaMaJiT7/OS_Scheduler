from abc import ABC, abstractmethod


class BaseReplacement(ABC):
    @abstractmethod
    def select_victim(self, page_table, **kwargs):
        pass
