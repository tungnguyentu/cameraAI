# Chỉ tiêu (bản nháp, chờ người dùng duyệt)

Phần cứng: RTX 3050 6 GB trên máy này. Trạng thái: DRAFT, ngày 2026-11-03.

## Model (giai đoạn 2)

Đo trên tập test lấy từ camera thật, quay vào ngày khác với tập train.

| Lớp | mAP50 | mAP50-95 |
|-----|-------|----------|
| `person` | ≥ 0.90 | ≥ 0.65 |
| `carton` | ≥ 0.85 | ≥ 0.60 |
| `sack` | ≥ 0.80 | ≥ 0.55 |
| `wrapped` | ≥ 0.80 | ≥ 0.55 |

Giai đoạn 1 chỉ đo mốc, không có ngưỡng đạt.

## Đếm (giai đoạn 3)

So với số đếm tay của người, trên ít nhất 10 phiên bốc hàng thật ở cửa thùng xe. Đo riêng LOAD và UNLOAD.

| Chỉ số | Chỉ tiêu |
|--------|----------|
| Sai số tổng mỗi lớp, cộng tất cả phiên | ≤ 3 % |
| Sai số mỗi lớp trong một phiên | ≤ 5 % |
| Đếm trùng hoặc đếm sai lớp | ≤ 2 % số vật |

Sai số = |đếm máy − đếm tay| / đếm tay.

## Hiệu năng realtime

| Chỉ số | Chỉ tiêu |
|--------|----------|
| FPS xử lý mỗi camera (input 640, TensorRT FP16) | ≥ 15 FPS |
| Số camera đồng thời trên RTX 3050 | 2 (người dùng chốt 1 đến 2) |
| Độ trễ từ khung hình nhận được tới overlay | ≤ 300 ms |
| Độ trễ từ cảnh thật tới màn hình (gồm RTSP) | ≤ 1 s |
| VRAM | ≤ 5 GB |
| Chạy liên tục không lỗi, RAM không tăng dần | ≥ 8 giờ |
| Tự kết nối lại khi mất RTSP | ≤ 10 s |

## Định nghĩa xong

Vision QA báo PASS với số liệu ở trên, đo trên footage thật từ camera kho.
