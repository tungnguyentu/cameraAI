"""Read an RTSP stream for N seconds; report real FPS, read failures, reconnects.
URL comes from env CAM_URL only and is never printed."""
import os, re, sys, time
os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp|timeout;10000000")
import cv2

url = os.environ["CAM_URL"]
secs = float(sys.argv[1]) if len(sys.argv) > 1 else 30
snap = sys.argv[2] if len(sys.argv) > 2 else None
mask = lambda s: re.sub(r"rtsp://[^\s]*@", "rtsp://***@", str(s))

t_open = time.time()
cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
if not cap.isOpened():
    sys.exit("open failed")
print(f"open_s={time.time()-t_open:.2f} declared_fps={cap.get(cv2.CAP_PROP_FPS):.2f} "
      f"size={int(cap.get(3))}x{int(cap.get(4))}")

ok = fail = reconnects = 0
saved = False
t0 = time.time()
first_t = None
while time.time() - t0 < secs:
    r, frame = cap.read()
    if not r or frame is None:
        fail += 1
        if fail % 5 == 0:  # 5 failed reads in a row-ish: reopen
            cap.release(); reconnects += 1
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        continue
    ok += 1
    if first_t is None:
        first_t = time.time()  # skip open/first-frame delay in fps
    if snap and not saved and ok >= 20:
        saved = cv2.imwrite(snap, frame)
el = time.time() - (first_t or t0)
print(f"frames={ok} read_fail={fail} reconnects={reconnects} elapsed_s={el:.1f} "
      f"real_fps={ok/el if el else 0:.2f} snapshot_saved={saved}")
cap.release()
