from xml.etree import ElementTree
from pathlib import Path
from os import listdir
from os.path import splitext, basename
import json
from thyroid import Thyroid
import csv

data_dir = Path('./thyroid')
out_dir = Path('./cropped')
mask_dir = Path('./mask')

Thyroid.get_dirs(data_dir, out_dir, mask_dir)


def main():
    def file_filter(f):
        if splitext(f)[1] in ['.xml']:
            return True
        else:
            return False

    files = listdir(data_dir)
    files = list(filter(file_filter, files))

    f = open('diagnosis.csv', 'w', newline='')
    csv_writer = csv.writer(f)

    for file in files:
        tree = ElementTree.parse(data_dir / file)
        root = tree.getroot()

        number = int(list(root.iter(tag='number'))[0].text)
        tirads = list(root.iter(tag='tirads'))[0].text

        marks = list(root.iter(tag='mark'))
        for mark in marks:
            # for nodule in one image / one image contains one or two nodules
            subscript = int(list(mark.iter(tag='image'))[0].text)

            svg_ = list(mark.iter(tag='svg'))[0].text
            svgs = []
            try:
                svgs = json.loads(svg_)  # list
            except:
                continue
            finally:
                nod_num = len(svgs)
                if nod_num != 1:
                    nod_num = 2

                for i, svg in enumerate(svgs):
                    points = svg['points']
                    thy = Thyroid(filename=file,
                                  number=number,
                                  subscript=subscript,
                                  tirads=tirads,
                                  points=points,
                                  nod_num=nod_num,
                                  part=i+1)
                    thy.draw_mask()
                    thy.resize_nodule()
                    thy.fill_bfs()
                    thy.erode_dilate()
                    thy.remove_border()
                    thy.save()

                    if thy.nod_num == 2:
                        item = f'{splitext(thy.filename)[0]}({thy.part})'
                    else:
                        item = f'{splitext(thy.filename)[0]}'
                    csv_writer.writerow((item, thy.tirads))
                    print(f'{item} has been saved')
    f.close()


if __name__ == '__main__':
    main()
