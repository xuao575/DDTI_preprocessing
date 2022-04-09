from pathlib import Path
from PIL import Image, ImageDraw
from os.path import splitext
import numpy as np
from numpy import ndarray
from skimage.morphology import erosion, dilation


class Thyroid:
    img_dir = None
    out_dir = None
    mask_dir = None

    def __init__(self,
                 filename,
                 number,
                 subscript,
                 points,
                 tirads,
                 nod_num,
                 part
                 ):
        # image_idx
        self.subscript = subscript  # how many images in an xml
        self.filename = splitext(filename)[0] + f'_{self.subscript}' + '.jpg'  # image name
        self.number = number    # tag in xml
        self.nod_num = nod_num  # 1 or 2, how many nodules in image
        self.part = part        # left -> 1 / right -> 2 if two nodules in image

        self.points = points    # points list
        self.points.append(self.points[0])

        self.tirads = tirads    # tirads

        self.img = Image.open(Thyroid.img_dir / self.filename).convert('L')  # image of PIL
        self.nod = None
        self.mask = None

        self.left = 0
        self.up = 0
        self.right = 0
        self.down = 0

    @classmethod
    def get_dirs(cls, img_dir: Path, out_dir: Path, mask_dir: Path):
        cls.img_dir = img_dir
        cls.out_dir = out_dir
        cls.mask_dir = mask_dir

    def remove_border(self, bar=10):
        """remove border if a row / column's average value is below bar"""
        nod = np.asarray(self.nod)
        mask = np.asarray(self.mask)

        row = np.mean(nod, axis=1)
        nod = nod[row > bar, :]
        mask = mask[row > bar, :]

        col = np.mean(nod, axis=0)
        nod = nod[:, col > bar]
        mask = mask[:, col > bar]

        self.nod = Image.fromarray(nod).resize((300, 300))
        self.mask = Image.fromarray(mask).resize((300, 300))

    def draw_mask(self):
        self.mask = Image.new(mode='1', size=self.img.size, color=1)

        draw = ImageDraw.Draw(self.mask)
        for i in range(len(self.points)-1):
            x1 = self.points[i]['x']
            y1 = self.points[i]['y']

            x2 = self.points[i+1]['x']
            y2 = self.points[i+1]['y']

            draw.line((x1, y1, x2, y2), width=5, fill=0)

    def resize_nodule(self, border=30):
        # leave a size of 30 pixels
        x_list = [point['x'] for point in self.points]
        y_list = [point['y'] for point in self.points]

        self.left = max(0, min(x_list) - border)
        self.up = max(0, min(y_list) - border)
        self.right = min(self.img.width, max(x_list) + border)
        self.down = min(self.img.height, max(y_list) + border)

        self.nod = self.img.crop((self.left, self.up, self.right, self.down)).resize((300, 300))
        self.mask = self.mask.crop((self.left, self.up, self.right, self.down)).resize((300, 300))

    def fill_bfs(self):
        # img = self.mask.getdata():
        img = np.asarray(self.mask)
        q = [(0, 0)]
        seen = set()
        seen.add((0, 0))
        while len(q) > 0:
            x, y = q.pop()
            img[x, y] = 0
            # neighbours
            neis = [(x + 1, y),
                    (x - 1, y),
                    (x, y - 1),
                    (x, y + 1)]
            for nei in neis:
                x0 = nei[0]
                y0 = nei[1]
                if (nei not in seen) and x0 >= 0 and y0 >= 0 and x0 < self.mask.width \
                        and y0 < self.mask.height and img[x0, y0] != 0:
                    q.append(nei)
                    seen.add(nei)
        self.mask = Image.fromarray(img)

    def erode_dilate(self, e=3, d=5):
        img = np.asarray(self.mask)
        cross = np.array([[0, 1, 0],
                          [1, 1, 1],
                          [0, 1, 0]])
        for i in range(e):
            img = erosion(img, cross)
        for i in range(d):
            img = dilation(img, cross)
        self.mask = Image.fromarray(img)

    def save(self):
        Thyroid.out_dir.mkdir(parents=True, exist_ok=True)
        Thyroid.mask_dir.mkdir(parents=True, exist_ok=True)

        # img has two nodules
        if self.nod_num == 2:
            file_png = (splitext(self.filename)[0] + f'({self.part}).png')
            file_gif = (splitext(self.filename)[0] + f'({self.part}).gif')
            out_path = Thyroid.out_dir / file_png
            mask_path = Thyroid.mask_dir / file_gif

            self.nod.save(out_path, quality=100)
            self.mask.save(mask_path, quality=100)
        # one nodule in image
        else:
            self.nod.save(Thyroid.out_dir / (splitext(self.filename)[0] + '.png'), quality=100)
            self.mask.save(Thyroid.mask_dir / (splitext(self.filename)[0] + '.gif'), quality=100)


