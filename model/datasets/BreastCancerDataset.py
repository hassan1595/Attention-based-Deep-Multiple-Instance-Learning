import os
import os.path as op
import PIL
from torch.utils.data import Dataset


class BreastCancerDataset(Dataset):
    """
    A class representing the BreastCancer-dataset.
    """
    def __init__(
            self, dir: str, transform=None
    ) -> None:
        self.transform = transform

    def __len__(self):
        return 0

    def __getitem__(self, i):
        
        return None
