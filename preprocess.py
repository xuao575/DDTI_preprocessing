from xml.etree import ElementTree
from pathlib import Path
from os import listdir
from os.path import splitext, basename
import json

data_dir = Path('./thyroid')


class Thyroid:
    def __init__(self, filename, number, subscript, points, tirads):
        self.filename = filename
        self.number = number
        self.subscript = subscript

        self.points = points
        self.tirads = tirads

    @classmethod
    def draw_mask(cls):
        pass


def main():
    def file_filter(f):
        if splitext(f)[1] in ['.xml']:
            return True
        else:
            return False

    files = listdir(data_dir)
    files = list(filter(file_filter, files))

    for file in files:
        tree = ElementTree.parse(data_dir / file)
        root = tree.getroot()

        number = list(root.iter(tag='number'))[0].text
        tirads = list(root.iter(tag='tirads'))[0].text

        marks = list(root.iter(tag='mark'))
        for mark in marks:
            subscript = list(mark.iter(tag='image'))[0].text

            svg_ = list(mark.iter(tag='svg'))[0].text
            svgs = []
            try:
                svgs = json.loads(svg_)
            except:
                continue
            finally:
                for svg in svgs:
                    points = svg['points']
                    thy = Thyroid(filename=file,
                                  number=number,
                                  subscript=subscript,
                                  tirads=tirads,
                                  points=points)


if __name__ == '__main__':
    main()
