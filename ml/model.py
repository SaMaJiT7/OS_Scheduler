import torch
import torch.nn as nn


class PageLSTM(nn.Module):
    def __init__(self, vocab_size, embedding_dim=64, hidden_dim=128,
                 num_layers=2, dropout=0.2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(
            embedding_dim, hidden_dim, num_layers,
            dropout=dropout, batch_first=True,
        )
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        emb = self.embedding(x)
        lstm_out, _ = self.lstm(emb)
        last_out = lstm_out[:, -1, :]
        logits = self.fc(last_out)
        return logits
