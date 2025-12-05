import stow
from datetime import datetime

from mltu.configs import BaseModelConfig

class ModelConfig(BaseModelConfig):
    def __init__(self):
        super().__init__()
        self.dataset_path = stow.join('Datasets', datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.vocab = ''
        self.height = 32
        self.width = 128
        self.max_text_length = 0
        self.batch_size = 16
        self.learning_rate = 0.001
        self.train_epochs = 100
        self.train_workers = 8
        