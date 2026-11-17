# Lab 4 - Phân tích kiểm thử tải Books API

Đo bằng script run_lab.py, mỗi kịch bản dùng database riêng với cùng 50 sách ban đầu.

## Số liệu

p95 lấy từ dòng Aggregated; đơn vị ms.

| Kịch bản | Users | Spawn/s | Thời gian | Requests | p95 | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 137 | 170 | 0.00% | 4.24 |
| B | 50 | 5 | 60s | 834 | 6200 | 0.12% | 13.04 |
| C | 200 | 50 | 30s | 883 | 8300 | 8.38% | 22.27 |

## 1. Kịch bản có p95 cao nhất

Kịch bản C: 8300 ms. Tải cao có thể làm tăng thời gian chờ CPU, thread, kết nối và tranh chấp ghi SQLite. Đây là giả thuyết từ kiến trúc; cần profiling để xác định nút thắt thực tế.

## 2. Failure rate theo endpoint

| Endpoint | A | B | C |
|---|---:|---:|---:|
| `GET /books` | 0/55 (0.00%) | 0/345 (0.00%) | 36/382 (9.42%) |
| `GET /books/{id}` | 0/37 (0.00%) | 0/233 (0.00%) | 24/255 (9.41%) |
| `GET /books?year` | 0/14 (0.00%) | 1/125 (0.80%) | 7/136 (5.15%) |
| `POST /books` | 0/31 (0.00%) | 0/131 (0.00%) | 7/110 (6.36%) |

Lỗi ghi nhận trong báo cáo:

- A: Không ghi nhận lỗi.
- B: GET /books?year: CatchResponseError('Unexpected status 500') (1 lần)
- C: GET /books: ConnectionRefusedError(10061, '[WinError 10061] No connection could be made because the target machine actively refused it.') (36 lần); POST /books: ConnectionRefusedError(10061, '[WinError 10061] No connection could be made because the target machine actively refused it.') (7 lần); GET /books/{id}: CatchResponseError('Unexpected status 0') (24 lần); GET /books?year: CatchResponseError('Unexpected status 500') (2 lần); GET /books?year: CatchResponseError('Unexpected status 0') (5 lần)

Mỗi request tìm theo năm có xác suất 1% yêu cầu server trả HTTP 500 thật khi bật LAB_FAULT_INJECTION. Tỷ lệ quan sát có thể bằng 0 với mẫu nhỏ; không đồng nghĩa toàn workload có 1% lỗi. Tăng user không đổi xác suất này. Status 0 và ConnectionRefusedError là lỗi kết nối, không phải HTTP 500. GET theo ID chấp nhận 404 có chủ đích.

## 3. SLO và baseline cho CI gate

Với SLO p95 tổng < 300 ms, kịch bản đạt: A. Nếu SLO áp dụng từng endpoint, phải kiểm tra riêng p95 của mỗi endpoint.

Đề xuất A (10 users, spawn 2/s, 30s) làm baseline ban đầu trên runner cố định, database sạch 50 sách. Gate: p95 tổng < 300 ms và không có lỗi ngoài lỗi giả lập. Chạy riêng lượt không fault injection để kiểm tra 0 lỗi; lượt bật injection dùng kiểm tra quan sát lỗi. Không ép tỷ lệ bằng đúng 1% với mẫu nhỏ. Lặp baseline vài lần trước khi chốt ngưỡng; B/C chạy định kỳ.

Flask development server và SQLite local chỉ đại diện môi trường lab. Wait time 1–3 giây khiến 200 user không đồng nghĩa 200 truy vấn đồng thời. Thời gian HTML có thể dài hơn cấu hình do chờ request kết thúc.

## Bonus: connection pool giới hạn 5

Khi cả 5 connection đều bận, request cần connection thứ sáu phải chờ. p95 có thể tăng, throughput chững lại và có thể xảy ra pool timeout. Không phải cứ 200 user là lập tức lỗi.

Kiểm chứng với QueuePool, pool_size=5, max_overflow=0 và pool_timeout cố định; so sánh C với pool lớn hơn trên cùng dữ liệu và workload. Đo p95, RPS, failures, thời gian chờ checkout và log timeout. Chỉ pool_size=5 chưa giới hạn cứng nếu còn overflow. Code hiện chưa áp dụng giới hạn này; SQLite cũng có tranh chấp ghi riêng.
