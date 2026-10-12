"""Convert KITTI object detection labels to YOLO format.

KITTI label lines look like:

    Car 0.00 0 1.85 387.63 181.54 423.81 203.12 ...

where columns 4 to 7 are the bounding box as (left, top, right, bottom) in
pixels. YOLO wants one line per object of the form

    class_index x_center y_center width height

with all four numbers normalised by the image width and height. KITTI images
are 1242 x 375 pixels. "DontCare" lines are dropped.

Usage:

    python src/label_editor.py --kitti-labels path/to/training/label_2 --out path/to/labels
"""

import argparse
import os

names = ['Car', 'Van', 'Truck', 'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram', 'Misc', 'DontCare']
width = 1242
height = 375


def convert_file(src_path, dst_path):
    linelist = open(src_path).read().splitlines()
    N = []
    for j in linelist:
        if j[0] != "D":  # skip DontCare
            m = j.split(" ")
            n = []
            o = []
            for i in range(4, 8):
                n.append(float(m[i]))

            for k in range(0, len(names) - 1):
                if m[0] == names[k]:
                    o.append(k)

            left = n[0]
            top = n[3]
            right = n[2]
            bottom = n[1]
            xc = (left + right) / 2
            yc = (top + bottom) / 2
            wb = right - left
            hb = top - bottom

            o.append(xc / width)
            o.append(yc / height)
            o.append(wb / width)
            o.append(hb / height)

            st = ""
            for a in range(0, 5):
                st = st + str(o[a]) + " "
            st = st + "\n"
            N.append(st)

    with open(dst_path, 'w') as file1:
        file1.writelines(N)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--kitti-labels', required=True, help='directory of KITTI label_2 .txt files')
    parser.add_argument('--out', required=True, help='directory to write YOLO format label files')
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    files = sorted(os.listdir(args.kitti_labels))
    for testfile in files:
        convert_file(os.path.join(args.kitti_labels, testfile), os.path.join(args.out, testfile))
    print(f"converted {len(files)} label files to {args.out}")
