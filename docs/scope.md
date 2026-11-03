# Phạm vi (bản nháp, chờ người dùng duyệt)

Nguồn: `brief-grok-report.pdf`. Trạng thái: DRAFT, ngày 2026-11-03. Người dùng đã chốt vạch đếm, chiều đếm và lớp `wrapped` (xem mục Đã chốt).

## Mục tiêu

Phát hiện, theo dõi và đếm hàng realtime từ camera RTSP trong kho. Màn hình hiện box, tên lớp, confidence và bảng LOAD đếm theo từng lớp hàng.

## Lớp đối tượng

| Lớp | Mô tả | Có đếm LOAD |
|-----|-------|-------------|
| `person` | Người trong khung hình | Không (chỉ phát hiện và theo dõi) |
| `carton` | Thùng carton, hộp giấy | ✓ |
| `sack` | Bao, bao tải, bao xi măng | ✓ |
| `wrapped` | Cả pallet bọc màng co, tính là 1 | ✓ |

## Quy tắc đếm

- Đếm qua vạch (line crossing) có hướng, đặt ngang cửa thùng xe. Mỗi track ID chỉ được đếm một lần cho mỗi hướng.
- Đi vào xe là `LOAD +1`. Đi ra khỏi xe là `UNLOAD +1`. Bảng hiện LOAD, UNLOAD và số ròng (LOAD − UNLOAD) cho mỗi lớp.
- Đếm theo vùng (region) chỉ là phương án dự phòng khi camera không thấy rõ đường đi của hàng.
- Một vật cần ít nhất 3 khung hình liên tiếp có cùng track ID trước khi được tính, để loại phát hiện nhiễu.

## Stack

- Ultralytics YOLO (YOLO11 hoặc mới hơn) cho phát hiện.
- ByteTrack cho theo dõi (BoT-SORT là phương án dự phòng).
- `ObjectCounter` hoặc logic đếm qua vạch riêng nếu cần quy tắc ở trên.
- OpenCV cho overlay. Dashboard web chạy local.
- Gán nhãn bằng công cụ chạy local (CVAT hoặc Label Studio tự host). Không dùng Roboflow cloud vì footage có người.

## Kế hoạch 3 giai đoạn

| Giai đoạn | Việc | Chủ | Xong khi |
|-----------|------|-----|----------|
| 1. Mốc (baseline) | Đọc RTSP ổn định, lưu mẫu clip và ảnh vào `data/` (local). Chạy YOLO11 COCO cho `person`, chạy YOLOE hoặc YOLO-World với prompt chữ cho `carton`, `sack`, `wrapped`. Đo FPS và mAP mốc. | App Engineer (pipeline), ML Engineer (mốc) | Có báo cáo FPS và mAP mốc trên tập test nhỏ, và ít nhất 2 giờ footage đại diện được lưu local. |
| 2. Model riêng | Gán nhãn, chia train/val/test theo ngày quay (không theo khung hình). Train YOLO11s hoặc YOLO11n, xuất TensorRT FP16. | ML Engineer | Đạt chỉ tiêu mAP trong `targets.md` trên tập test. |
| 3. Đếm realtime và dashboard | Tracking, đếm qua vạch, overlay, bảng LOAD, dashboard, log số đếm theo phiên. | App Engineer, QA kiểm số đếm | Vision QA báo PASS với số liệu trên footage thật. |

## Ngoài phạm vi

- Nhận diện khuôn mặt hoặc danh tính người.
- Đếm tồn kho tĩnh trên kệ.
- Dịch vụ cloud, công cụ trả phí, camera hoặc phần cứng mới (cần người dùng duyệt trước).

## Dữ liệu và quyền riêng tư

- Footage chỉ nằm trên máy này, trong `data/` và `runs/` (đã có trong `.gitignore`).
- Không upload footage, không đưa footage vào git.
- URL và mật khẩu camera nằm trong `.env` (đã có trong `.gitignore`), không viết vào chat hoặc docs.

## Đã chốt (2026-11-03)

- Vạch đếm ở cửa thùng xe.
- Đếm cả hai chiều: LOAD và UNLOAD.
- `wrapped` là cả pallet bọc màng co, tính là 1.
- 1 đến 2 camera chạy đồng thời.

## Môi trường thử

Người dùng hiện ở nhà, chưa có cửa thùng xe để thử. Giai đoạn 1 và phần phát triển của giai đoạn 3 dùng một vạch giả lập ở nhà. Ví dụ: vạch ở khung cửa phòng, người bê thùng carton qua lại. Nghiệm thu (Vision QA PASS) bắt buộc dùng footage thật ở cửa thùng xe.

## Câu hỏi mở

1. Ở nhà có camera RTSP nào để lấy mẫu giai đoạn 1 không, hay dùng webcam hoặc video quay sẵn?
2. Khi nào có thể quay footage thật ở cửa thùng xe cho tập train và nghiệm thu?
