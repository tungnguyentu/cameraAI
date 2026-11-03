"""Pseudo-label frames with pretrained models and build a YOLO dataset.

person: YOLO11 COCO. carton/sack/wrapped: YOLOE text prompts.
Labels are teacher output, not human ground truth.
Optional --student: a trained detector whose goods boxes are merged in, to fill teacher misses.
Usage: python autolabel.py <frames_dir> <out_dir> [--val-range START END] [--gap 5] [--goods carton sack] [--student best.pt]
"""
import argparse
from collections import Counter
from pathlib import Path

import torch
from ultralytics import YOLO, YOLOE
from ultralytics.utils.metrics import box_iou

NAMES = ["person", "carton", "sack", "wrapped"]
PROMPTS = {  # several text prompts per class raise teacher recall
    "carton": ["cardboard box", "box", "carton", "package"],
    "sack": ["sack bag", "woven sack", "cement bag"],
    "wrapped": ["pallet wrapped in plastic film", "shrink-wrapped pallet"],
}

ap = argparse.ArgumentParser()
ap.add_argument("frames")
ap.add_argument("out")
ap.add_argument("--val-range", type=int, nargs=2, help="frame index range [START, END) for val; default last 20%%")
ap.add_argument("--goods", nargs="+", default=list(PROMPTS), choices=list(PROMPTS), help="goods classes in this footage")
ap.add_argument("--gap", type=int, default=5, help="frames dropped between train and val")
ap.add_argument("--conf-person", type=float, default=0.4)
ap.add_argument("--conf-goods", type=float, default=0.3)
ap.add_argument("--student", help="trained weights with the same class names")
ap.add_argument("--conf-student", type=float, default=0.3)
a = ap.parse_args()

frames = sorted(Path(a.frames).glob("*.jpg"))
lo, hi = a.val_range or (len(frames) - len(frames) // 5, len(frames))
# ponytail: time-block split with a gap on both sides; split by recording day once real footage exists
splits = {"train": frames[: max(lo - a.gap, 0)] + frames[hi + a.gap :], "val": frames[lo:hi]}

coco = YOLO("yolo11m.pt")
yoloe = YOLOE("yoloe-11l-seg.pt")
yoloe.set_classes([t for g in a.goods for t in PROMPTS[g]])
goods_ids = [NAMES.index(g) for g in a.goods for _ in PROMPTS[g]]
student = YOLO(a.student) if a.student else None

out = Path(a.out).resolve()
counts = {s: Counter() for s in splits}
for split, files in splits.items():
    (out / "images" / split).mkdir(parents=True, exist_ok=True)
    (out / "labels" / split).mkdir(parents=True, exist_ok=True)
    for f in files:
        lines = []
        r = coco.predict(f, classes=[0], conf=a.conf_person, verbose=False)[0]
        lines += [(0, b) for b in r.boxes.xywhn.tolist()]
        r = yoloe.predict(f, conf=a.conf_goods, agnostic_nms=True, verbose=False)[0]
        lines += [(goods_ids[int(c)], b) for c, b in zip(r.boxes.cls.tolist(), r.boxes.xywhn.tolist())]
        if student:
            kept = r.boxes.xyxyn
            s = student.predict(f, classes=goods_ids, conf=a.conf_student, verbose=False)[0].boxes
            for c, xyxy, b in zip(s.cls.tolist(), s.xyxyn, s.xywhn.tolist()):
                if not len(kept) or box_iou(xyxy[None], kept).max() < 0.5:  # teacher missed it
                    lines.append((int(c), b))
                    kept = torch.cat([kept, xyxy[None]])
        for c, _ in lines:
            counts[split][NAMES[c]] += 1
        counts[split]["images"] += 1
        link = out / "images" / split / f.name
        if not link.exists():
            link.symlink_to(f.resolve())
        (out / "labels" / split / f"{f.stem}.txt").write_text(
            "".join(f"{c} {' '.join(f'{v:.6f}' for v in b)}\n" for c, b in lines)
        )

(out / "data.yaml").write_text(
    f"path: {out}\ntrain: images/train\nval: images/val\nnames:\n"
    + "".join(f"  {i}: {n}\n" for i, n in enumerate(NAMES))
)
for s, c in counts.items():
    print(s, dict(c))
