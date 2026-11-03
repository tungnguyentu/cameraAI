# Dataset log

Footage and labels stay in `data/` on this machine. They are not in git.

Labels come from `scripts/autolabel.py`. `person` comes from YOLO11m COCO (conf 0.4). Goods come from YOLOE-11L text prompts (conf 0.15, several prompts per class, class-agnostic NMS). No human reviewed the labels. Metrics against these labels show agreement with the teacher models, not true accuracy.

## Clips (CAM1 main stream, home test camera, 2026-11-03)

| Clip | Time | Frames | Content | Auto labels |
|------|------|--------|---------|-------------|
| `raw/cam1` | 23:30, 10 min, 1 frame / 2 s | 300 | Person sitting, a snack bag, no cartons | person 300, carton 0 (18 false carton labels on the snack bag removed by hand) |
| `raw/cam1-carry` | 23:45, 114 s, 4 fps | 456 | Person carries a brown carton, several passes | person 248, carton 69 |
| `raw/cam1-carry2` | 23:49, 57 s, 4 fps | 228 | Person carries a white and yellow printed carton, 4 passes | person 181, carton 56 |

## Dataset `demo-carton.yaml`

Train is `cam1` plus `cam1-carry`. Val is `cam1-carry2`, a separate recording with a different carton. No frame is shared between train and val.

A visual check of 24 val frames found no false carton labels. The teacher missed the carton in 5 of the 11 frames where it is clearly visible, so the val labels are incomplete.

## Dataset `demo-carton-v2.yaml` (2026-11-04)

New clip `raw/cam1-inout` (00:14, 180 s, the in/out counting test). Frames: 0 to 100 s at 1 fps, 100 to 160 s at 6 fps (the carton passes), 160 to 180 s at 1 fps. 480 frames.

Labels in the `ds2-*` folders use the teacher (YOLOE conf 0.12) plus the v1 model (`runs/demo-carton-y11s`, conf 0.3) as a student. A student box is added only where no teacher box overlaps it (IoU < 0.5). Carton labels rose from 69 to 91 in `cam1-carry` and from 56 to 73 in `cam1-carry2`.

Train is `ds-cam1-auto`, `ds2-carry`, `ds2-carry2`, and `ds2-inout` minus the hold-out. Val is the last carton pass of `cam1-inout` (140 to 150 s, 60 frames), with a 1 s gap on each side. A visual check of the hold-out labels found the carton labeled in 21 of 23 frames where it is visible. The hold-out uses the same carton and room as other training frames, so it is easier than a new scene. Because v1 helped make the labels, the metrics favor v1.

## Superseded

`ds-cam1-auto` from the first trial (person only, 9 wrong `sack` labels on the snack bag) was rebuilt with the carton-only prompt.
