"""Run YOLO + ByteTrack + Ultralytics ObjectCounter on a recorded clip.
Draws boxes, confidence, track id, the count line and the IN/OUT table; logs each count event.
Env: CONF (0.25), IMGSZ (640), TRACKER (bytetrack.yaml).
Usage: python count-inout-video.py <weights> <in_video> <out_video> [line_x_frac=0.5]
IN = crosses the line left->right, OUT = right->left. Each track counts once (ObjectCounter rule)."""
import csv, os, sys, time
import cv2, torch
from ultralytics import solutions

weights, src, dst = sys.argv[1:4]
line_x = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
W, H = 1280, 720  # model was trained on 1280x720 frames

cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS) or 20
x = int(W * line_x)
counter = solutions.ObjectCounter(model=weights, region=[(x, 0), (x, H)], classes=[0, 1],
                                  tracker=os.getenv("TRACKER", "bytetrack.yaml"), conf=float(os.getenv("CONF", "0.25")),
                                  imgsz=int(os.getenv("IMGSZ", "640")), show=False, show_conf=True, verbose=False)

events, frame_i = [], 0
orig = counter.count_objects
def logged(cur, tid, prev, cls):  # wrap to log every count event with time, class, track id
    before = (counter.in_count, counter.out_count)
    orig(cur, tid, prev, cls)
    if (counter.in_count, counter.out_count) != before:
        d = "IN" if counter.in_count != before[0] else "OUT"
        events.append((f"{frame_i / fps:.2f}", frame_i, counter.names[cls], int(tid), d))
        print(f"t={frame_i / fps:6.2f}s {d:3} {counter.names[cls]} id={tid}", flush=True)
counter.count_objects = logged

out = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
torch.cuda.reset_peak_memory_stats()
t0, lat, carton_frames = time.time(), [], 0
while True:
    ok, f = cap.read()
    if not ok:
        break
    t = time.time()
    r = counter(cv2.resize(f, (W, H)))
    lat.append(time.time() - t)
    carton_frames += 1 in counter.clss
    out.write(r.plot_im)
    frame_i += 1
out.release()
el = time.time() - t0
with open(dst.rsplit(".", 1)[0] + "-events.csv", "w", newline="") as fh:
    csv.writer(fh).writerows([("t_s", "frame", "class", "track_id", "dir"), *events])
lat.sort()
print(f"frames={frame_i} video_s={frame_i / fps:.1f} proc_fps={frame_i / el:.1f} "
      f"lat_ms_p50={lat[len(lat) // 2] * 1e3:.1f} p95={lat[int(len(lat) * .95)] * 1e3:.1f} "
      f"carton_frames={carton_frames} gpu_peak_mb={torch.cuda.max_memory_allocated() / 2**20:.0f}")
print("IN", counter.in_count, "OUT", counter.out_count, dict(counter.classwise_count))
