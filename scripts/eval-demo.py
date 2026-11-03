"""Compare carton models on a held-out pass: per-class metrics, FPS, and a preview grid.

Usage: python eval-demo.py <data.yaml> <val_images_dir> <out.jpg> <name=weights> [<name=weights> ...]
"""
import glob, sys, time
import cv2, numpy as np
from ultralytics import YOLO

data, val_dir, out_img, *models = sys.argv[1:]
imgs = sorted(glob.glob(f"{val_dir}/*.jpg"))
rows = []
for spec in models:
    name, w = spec.split("=", 1)
    m = YOLO(w)
    r = m.val(data=data, imgsz=640, batch=8, verbose=False, plots=False, project="/tmp/cv-val", name=name, exist_ok=True)
    for i in r.box.ap_class_index:
        print("%s %s P=%.3f R=%.3f mAP50=%.3f mAP50-95=%.3f" % ((name, m.names[int(i)]) + tuple(r.box.class_result(list(r.box.ap_class_index).index(i)))))
    m.predict(imgs[0], imgsz=640, verbose=False)
    t = time.perf_counter()
    preds = [m.predict(i, imgsz=640, conf=0.25, verbose=False)[0] for i in imgs]
    print(name, "FPS", round(len(imgs) / (time.perf_counter() - t), 1))
    print(name, "frames with carton >=0.25:", sum(int((p.boxes.cls == 1).any()) for p in preds), "/", len(imgs))
    tiles = []
    for k, (f, p) in enumerate(zip(imgs, preds)):
        im = cv2.imread(f)
        for c, (x1, y1, x2, y2) in zip(p.boxes.cls.tolist(), p.boxes.xyxy.int().tolist()):
            cv2.rectangle(im, (x1, y1), (x2, y2), (0, 0, 255) if c == 1 else (0, 255, 0), 8)
        cv2.putText(im, f"{name} {k}", (20, 110), 0, 3, (255, 0, 0), 8)
        tiles.append(cv2.resize(im, (320, 180)))
    tiles += [np.zeros_like(tiles[0])] * (-len(tiles) % 10)
    rows.append(np.vstack([np.hstack(tiles[i:i + 10]) for i in range(0, len(tiles), 10)]))
cv2.imwrite(out_img, np.vstack(rows))
