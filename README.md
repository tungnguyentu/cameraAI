# cameraAI

Cargo Vision counts people and goods (carton, sack, wrapped goods) that cross a line in a live RTSP camera stream. It uses Ultralytics YOLO, ByteTrack and OpenCV, and runs on one local GPU (tested on an RTX 3050 6 GB).

Status: development demo on a home test camera with a temporary line. The counting rule for a real loading door is not final.

## Contents

- `docs/`: scope, targets, decisions and the dataset log.
- `scripts/autolabel.py`, `scripts/eval-demo.py`: automatic labels and model evaluation.
- `scripts/rtsp-probe.py`: reads a stream and reports the real FPS, read failures and reconnects.
- `scripts/count-inout-video.py`: runs detection, tracking and line counting on a recorded clip. It writes an annotated video and a CSV file with one row for each count event.
- `configs/bytetrack-loose.yaml`: tracker settings that keep a track through short detection gaps.

Footage, labels and model weights stay on the local machine. They are not in git.

## Run

```sh
pip install ultralytics lap opencv-python
CONF=0.05 TRACKER=configs/bytetrack-loose.yaml \
  python scripts/count-inout-video.py <weights.pt> <clip.mkv> out.mp4
```

The camera URL contains a password. Keep it in a file outside the repo and pass it through the `CAM_URL` environment variable:

```sh
CAM_URL="$(cat /path/to/secret-url-file)" python scripts/rtsp-probe.py 30
```
