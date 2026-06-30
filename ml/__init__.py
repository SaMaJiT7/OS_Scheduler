from ml.vocab import Vocab

try:
    from ml.model import PageLSTM
except ImportError:
    PageLSTM = None

try:
    from ml.predict import load_model, predict_next_page
except ImportError:
    load_model = None
    predict_next_page = None
