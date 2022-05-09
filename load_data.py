import os
from os import listdir
from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset
import csv
from os.path import splitext


class DDTIDataset(Dataset):
    def __init__(self, image_dir: Path, mask_dir: Path, label_dir: Path, transforms, bi_label: bool):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.label_dir = label_dir
        self.transforms = transforms
        self.bi_label = bi_label
        self.ids, self.labels = self.make_dict(label_dir)

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        name = self.ids[idx]
        label = self.labels[splitext(name)[0]]
        image = Image.open(self.image_dir / (splitext(name)[0] + '.PNG')).convert('RGB')
        mask = Image.open(self.mask_dir / (splitext(name)[0] + '.GIF')).convert('1')
        image = self.transforms(image)
        mask = self.transforms(mask)
        return {
            'image': image,
            'mask': mask,
            'label': label
        }
        # return image, label

    def make_dict(self, label_dir: Path):
        f = csv.reader(open(label_dir, 'r'))
        dict = {}
        list = []

        if not self.bi_label:
            for name, label, bi in f:
                target = label
                if target in ['None', '']:
                    continue
                if label == '4a':
                    target = 4
                elif label == '4b':
                    target = 5
                elif label == '4c':
                    target = 6
                elif label == 5:
                    target = 7
                target = int(target) - 2
                dict[name] = target
                # range from 0 to 5:

        elif self.bi_label:
            for name, label, bi in f:
                if bi in ['None', '']:
                    continue
                target = int(bi)
                dict[name] = target
                # range from 0 to 5: 2 / 3 / 4a / 4b / 4c / 5
                list.append(name)

        return list, dict


class STAGE2(Dataset):
    def __init__(self, image_dir: Path, mask_dir: Path, transforms):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transforms = transforms
        self.ids = self.make_list(image_dir)

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        name = self.ids[idx]
        image = Image.open(self.image_dir / (splitext(name)[0] + '.PNG')).convert('L')
        mask = Image.open(self.mask_dir / (splitext(name)[0] + '.PNG')).convert('1')
        image = self.transforms(image)
        mask = self.transforms(mask)
        return {
            'image': image,
            'mask': mask
        }
        # return image, label

    @classmethod
    def make_list(cls, image_dir: Path):
        list = os.listdir(image_dir)
        return list
