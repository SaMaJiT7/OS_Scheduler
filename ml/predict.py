import torch

from ml.model import PageLSTM
from ml.vocab import Vocab


def load_model(checkpoint_path, vocab_size, device="cpu"):
    model = PageLSTM(vocab_size)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model


def predict_next_page(model, window, vocab, device="cpu"):
    indices = [vocab.page_to_index(pid) for pid in window]
    x = torch.tensor([indices], dtype=torch.long, device=device)
    with torch.no_grad():
        logits = model(x)
    pred_idx = logits.argmax(dim=1).item()
    return vocab.index_to_page(pred_idx)
