# Traffic Light Management System

Repository created in May 2021. Reorganized and cleaned up in October 2026 (file structure and README only, the code is as it was written at the time, except where the README notes a fix).

Adaptive traffic signal timing from camera snapshots. A YOLOv5 detector counts the vehicles waiting at each lane of a four way junction, and the green time given to that lane is computed from those counts, so a lane with more traffic gets a longer green and an empty lane gets a short one. Built in May 2021 as a team project (Ansh Singh, Paras Arora, Pratyaksh Chanda, Shreshth Mehrotra) at IIT Roorkee.

## What it does

1. A snapshot of the next lane is taken while the current lane is on its last few seconds of green.
2. The snapshot is passed through YOLOv5, which returns the number of cars, motorcycles, buses and trucks in it.
3. A scheduling function turns those counts into a green signal time for that lane.
4. A countdown loop runs the red, yellow and green timers for all four signals, prints their state every second, and repeats the process for the next lane.

The signal state is printed as a nested list in RYG order, one inner list per signal, for example `[[0, 0, 12], [17, 0, 0], [0, 0, 0], [0, 0, 0]]` means signal 0 has 12 s of green left and signal 1 has 17 s of red left.

A hardware mock up of the same cycle was also built in Tinkercad on two Arduino UNO boards: one drives the red, yellow and green LEDs using the computed green time as the delay, the other drives an LCD that shows the remaining green time over a serial link. See the report for the wiring picture and the Tinkercad link.

## Approach

Detection uses the ultralytics YOLOv5 implementation in PyTorch. The vendored copy of `detect.py` was adapted into `src/signalcountdown.py` so that, instead of only drawing boxes, it fills a per class count list. The counted COCO classes are `car`, `motorcycle`, `bus` and `truck`, so the pretrained `yolov5s.pt` checkpoint works out of the box. The team also fine tuned YOLOv5s on the KITTI dataset (see Dataset and training below), which is what `src/label_editor.py` was written for.

The signal controller is a plain Python simulation. It keeps a `signal` list with the remaining red, yellow and green seconds for each of the four signals, sleeps one second per tick, and switches lanes in order 0, 1, 2, 3, 0, ... The run stops after six lane changes (`maxruns`).

## How signal timing is decided

The green signal time (GST) for a lane is, from `gst()` in `src/signalcountdown.py`:

```
GST = floor( sum over vehicle classes ( count_of_class * average_crossing_time_of_class ) / (number_of_lanes + 1) )
```

with these average crossing times in seconds: car 4, motorcycle 2, bus 3.5, truck 3.5, and `number_of_lanes = 4`. So a snapshot with 10 cars, 2 motorcycles and 1 bus gives floor((40 + 4 + 3.5) / 5) = 9 seconds of green. The report lists start up lag per vehicle, the non linear extra lag for vehicles further back in the queue, and minimum and maximum green bounds (to avoid starving empty lanes) as factors the scheduler should consider, but the implemented formula is the one above. There is no minimum or maximum clamp in the code, so a lane with no detected vehicles gets 0 seconds of green.

The switching sequence implemented in `countdown()`:

- The first lane starts with a fixed 20 s of green (`--initial-green`). All other signals are red.
- While the green timer is above 5 s, only that timer counts down.
- In the last 5 s of green, the next signal's red timer is set to the green remaining plus 5, so it reads 10, 9, ... down to 6.
- When green reaches 0 the current signal turns yellow for 5 s and the next signal's red counts the same 5 s.
- When yellow ends, the next lane's snapshot is copied to `data/current/test.jpg`, YOLOv5 is run on it, `gst()` computes that lane's green time, and `countdown()` is called again for the next signal. The report describes this 5 s yellow window as the processing budget for detection.

## Dataset and training

From the project report:

- Dataset: KITTI object detection (https://www.kaggle.com/twaldo/kitti-object-detection), about 7500 images, of which 1600 were held out for validation.
- Labels: KITTI gives boxes as (left, top, right, bottom) in pixels. `src/label_editor.py` converts each label file to YOLO format, one `class_index x_center y_center width height` line per object, normalised by the image size (1242 x 375), dropping `DontCare` entries. The class list in the script is the KITTI one: Car, Van, Truck, Pedestrian, Person_sitting, Cyclist, Tram, Misc.
- Training command used (from inside `yolov5/`, with a `kittid.yaml` listing the train and val folders, the class count and class names):

```
python train.py --img 640 --batch 4 --epochs 5 --data kittid.yaml --weights yolov5s.pt
```

That is 5 epochs at batch size 4 and image size 640, starting from the pretrained YOLOv5s checkpoint. The `kittid.yaml` file and the KITTI images are not in this repository.

## Results

The report does not include quantitative detection metrics (mAP or similar) for the KITTI fine tuning, and no per lane timing results were recorded, so none are claimed here. The deliverables were the working simulation loop in `src/signalcountdown.py` and the Arduino / Tinkercad mock up described in the report.

## Repository layout

```
.
├── README.md
├── requirements.txt            # points at yolov5/requirements.txt
├── .gitignore
├── src/
│   ├── signalcountdown.py      # vehicle counting + signal scheduling loop (main script)
│   └── label_editor.py         # KITTI label -> YOLO label converter
├── data/
│   └── snapshots/              # put test0.jpeg, test1.jpeg, ... here (one per lane change)
├── reports/
│   ├── project_report.docx     # original project report
│   └── project_report.pdf      # PDF export of the same
└── yolov5/                     # vendored copy of ultralytics/yolov5, unmodified
```

`yolov5/` is a copy of https://github.com/ultralytics/yolov5 at commit `b8be76f` (6 May 2021, between the v5.0 and v6.0 releases), kept here as a vendored dependency under its own GPL-3.0 license (see `yolov5/LICENSE`). Nothing inside it was changed; the project code lives in `src/` and puts `yolov5/` on `sys.path`.

## How to run

The vendored yolov5 needs Python 3.8 or later and the packages in `yolov5/requirements.txt` (PyTorch 1.7 or later).

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Get weights. Either download the pretrained COCO checkpoint, which already knows the four vehicle classes:

```
cd yolov5 && bash weights/download_weights.sh && cd ..    # downloads yolov5s/m/l/x.pt into yolov5/
```

or fetch only `yolov5s.pt` from https://github.com/ultralytics/yolov5/releases/tag/v5.0. Pass its path with `--weights` (the script also auto downloads `yolov5s.pt` into the current directory if the file is missing). A fine tuned checkpoint from `yolov5/runs/train/exp/weights/best.pt` works the same way, as long as its class names include the four vehicle classes.

3. Put one snapshot per lane change in `data/snapshots/` named `test0.jpeg`, `test1.jpeg`, ... `test5.jpeg` (the loop stops after six lane changes, so six images are enough).

4. Run the simulation from the repository root:

```
python src/signalcountdown.py --weights yolov5s.pt
```

Useful flags: `--device cpu` to force CPU, `--initial-green 20` to change the first lane's fixed green time, `--conf-thres 0.25` to change the detection threshold, `--view-img` to show the annotated snapshot. Annotated images are written to `runs/detect/exp*/`.

To convert KITTI labels before training:

```
python src/label_editor.py --kitti-labels /path/to/kitti/training/label_2 --out /path/to/kitti/training/labels
```

then train with the command in Dataset and training above.

## Credits

Object detection is ultralytics YOLOv5 (https://github.com/ultralytics/yolov5), used under the GPL-3.0 license. The KITTI dataset is from the KITTI Vision Benchmark Suite, obtained through the Kaggle mirror linked above.
