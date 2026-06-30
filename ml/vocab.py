import json
import numpy as np


class Vocab:
    def __init__(self):
        self.unk_token = "<unk>"
        self.unk_index = 0
        self.id_to_index = {self.unk_token: 0}
        self.index_to_id = {0: self.unk_token}

    def build(self, page_ids, top_k=50000):
        ids, counts = np.unique(page_ids, return_counts=True)
        top_k = min(top_k, len(ids))
        top_indices = np.argsort(-counts, kind="mergesort")[:top_k]
        for i, idx in enumerate(top_indices, start=1):
            pid = int(ids[idx])
            self.id_to_index[pid] = i
            self.index_to_id[i] = pid

    def page_to_index(self, page_id):
        return self.id_to_index.get(page_id, 0)

    def index_to_page(self, index):
        return self.index_to_id.get(index, self.unk_token)

    def __len__(self):
        return len(self.id_to_index)

    def save(self, path):
        id_to_index_serial = {}
        for k, v in self.id_to_index.items():
            key = str(k) if not isinstance(k, str) else k
            id_to_index_serial[key] = v
        index_to_id_serial = {}
        for k, v in self.index_to_id.items():
            val = str(v) if not isinstance(v, str) else v
            index_to_id_serial[str(k)] = val
        data = {
            "unk_token": self.unk_token,
            "unk_index": self.unk_index,
            "id_to_index": id_to_index_serial,
            "index_to_id": index_to_id_serial,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            data = json.load(f)
        vocab = cls()
        vocab.unk_token = data["unk_token"]
        vocab.unk_index = data["unk_index"]
        vocab.id_to_index = {}
        for k, v in data["id_to_index"].items():
            key = int(k) if k != data["unk_token"] else k
            vocab.id_to_index[key] = v
        vocab.index_to_id = {}
        for k, v in data["index_to_id"].items():
            idx = int(k)
            val = v if v == data["unk_token"] else int(v)
            vocab.index_to_id[idx] = val
        return vocab
