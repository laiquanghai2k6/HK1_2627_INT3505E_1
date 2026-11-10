# Lab 1 — Product API CRUD

## Yêu cầu & bất biến

### 1. Schema sản phẩm

| Field | Ràng buộc |
|---|---|
| `sku` | bắt buộc, 3–32 ký tự (duy nhất) |
| `name` | bắt buộc, 1–255 ký tự |
| `price_cents` | bắt buộc, ≥ 0 |
| `qty_in_stock` | ≥ 0, mặc định `0` |

Được khai báo ở `src/product_api/schemas.py` (`ProductIn`, `ProductPatch`, `ProductOut`) và `src/product_api/models/product.py`.

### 2. Phân trang

`GET /api/v1/products?page=1&size=20` trả về:

```json
{"items":[{"archived":false,"description":null,"id":1,"name":"iPhone 15","price_cents":2000000,"qty_in_stock":5,"sku":"IP15"}],"page":1,"size":20,"total":1}
```

- `page` mặc định 1, `size` mặc định 20 (tối đa 100).
- `total` là tổng số sản phẩm chưa bị archived.

### 3. Reserve

`POST /api/v1/products/<id>/reserve` với body `{"qty": 1}`:

```json
{"archived":false,"description":null,"id":1,"name":"iPhone 15","price_cents":2000000,"qty_in_stock":3,"sku":"IP15"}
```

- Giảm `qty_in_stock` đi `qty`.
- Không cho `qty_in_stock < 0`: nếu không đủ hàng trả **409** (`out_of_stock`) và số lượng tồn giữ nguyên.

### 4. Soft delete

`DELETE /api/v1/products/<id>` chỉ đặt `archived = true` và trả 204.

```http
HTTP/1.1 204 NO CONTENT
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 10 Nov 2026 10:59:40 GMT
Content-Type: text/html; charset=utf-8
Connection: close
```

- `GET` danh sách và `GET /<id>` mặc định loại trừ `archived = True` (sản phẩm đã xóa mềm trả 404).

### 5. Xử lý lỗi

404 / 409 / 422 đều trả JSON dạng:

```json
{"error": "...", "detail": "..."}
```

Ví dụ lỗi 400 (body không phải JSON hợp lệ):

```http
HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 10 Nov 2026 11:00:14 GMT
Content-Type: application/json
Content-Length: 112
Connection: close

{"detail":"The browser (or proxy) sent a request that this server could not understand.","error":"bad_request"}
```

| Status | `error` | Khi nào |
|---|---|---|
| 404 | `not_found` | Không tìm thấy sản phẩm / đơn hàng (hoặc sản phẩm đã archived) |
| 409 | `sku_conflict` | Trùng `sku` khi tạo |
| 409 | `out_of_stock` | Reserve vượt số lượng tồn |
| 422 | `validation_error` | Dữ liệu không hợp lệ; `detail` liệt kê lỗi theo từng field |

### 6. Cài đặt và chạy (Windows PowerShell)

```powershell
# 1. Vào thư mục project, kích hoạt venv
cd Lab1
.\.venv\Scripts\Activate.ps1          # nếu chưa có: python -m venv .venv

# 2. Cài package (kèm pytest)
pip install -e ".[dev]"
# Nếu dùng PostgreSQL: pip install -e ".[dev,postgres]"

# 3. Tạo file .env
Copy-Item .env.example .env           # rồi chỉnh DB_URL nếu cần

# 4. Tạo database bằng migration
flask --app wsgi db init              # chỉ chạy lần đầu
flask --app wsgi db migrate -m "create products"
flask --app wsgi db upgrade

# 5. Chạy server
flask --app wsgi run
```

Nếu bạn đã chạy bước 4 từ trước (khi project mới có `products`), sau khi thêm Order/OrderItem ở phần dưới cần sinh thêm một revision rồi áp dụng:

```powershell
flask --app wsgi db migrate -m "add orders and order_items"
flask --app wsgi db upgrade
```

Mở file revision trong `migrations/versions/` để kiểm tra trước khi `upgrade`.

---

## Phần mở rộng

### 7. Order và OrderItem — `/api/v1/orders`

Một đơn hàng (`Order`) gồm nhiều dòng hàng (`OrderItem`); mỗi `OrderItem` trỏ tới đúng một `Product`. Nhờ vậy một Order chứa được nhiều Product khác nhau, không bị gán cứng với một Product duy nhất. Resource nằm trong blueprint riêng `src/product_api/api/orders.py`, model ở `src/product_api/models/order.py`.

| Method | Đường dẫn | Mô tả | Thành công | Lỗi |
|---|---|---|---|---|
| POST | `/api/v1/orders` | Tạo đơn hàng | 201 | 400, 422 |
| GET | `/api/v1/orders?page=1&size=20` | Danh sách đơn có phân trang | 200 | 422 nếu `page`/`size` không phải số |
| GET | `/api/v1/orders/<id>` | Lấy một đơn hàng | 200 | 404 |

**Tạo đơn** — body:

```json
{
  "customer_name": "An",
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 2, "quantity": 1}
  ]
}
```

Response 201:

```json
{"created_at":"2026-11-10T11:05:00","customer_name":"An","id":1,"items":[{"id":1,"product_id":1,"product_name":"iPhone 15","quantity":2,"unit_price_cents":2000000},{"id":2,"product_id":2,"product_name":"Mouse","quantity":1,"unit_price_cents":250}],"total_cents":4000250}
```

Quy tắc:

- `customer_name`: bắt buộc, 1–255 ký tự. `items`: bắt buộc, ít nhất 1 phần tử. `quantity` ≥ 1.
- Trả **422** nếu `product_id` không tồn tại, sản phẩm đã bị archived, hoặc một `product_id` xuất hiện hai lần trong cùng đơn.
- `unit_price_cents` được lưu theo giá của sản phẩm **tại thời điểm đặt hàng**, nên sau này sản phẩm đổi giá thì đơn cũ không bị đổi. `total_cents` = tổng `quantity × unit_price_cents`.
- Tạo đơn **không** trừ `qty_in_stock`; trừ kho dùng endpoint `reserve` ở mục 3.
- Cặp (`order_id`, `product_id`) là duy nhất trong bảng `order_items`.

### 8. Health check

Hai endpoint tách riêng, không gộp chung:

| Endpoint | Loại | Ý nghĩa | Phụ thuộc DB |
|---|---|---|---|
| `GET /healthz` | Liveness | "Process còn sống không?" Trả 200 nếu app còn chạy | Không |
| `GET /ready` | Readiness | "Nhận traffic được chưa?" Chạy `SELECT 1`; 200 nếu DB ổn, **503** nếu DB lỗi | Có |

```json
{"status": "ok"}
```

```json
{"checks": {"db": "ok"}, "status": "ok"}
```

Khi DB lỗi, `/ready` trả 503 với `{"checks": {"db": "err"}, "status": "degraded"}`, còn `/healthz` vẫn trả 200 — orchestrator chỉ ngừng gửi traffic chứ không restart container.

### 9. Docker

Đóng gói bằng `Dockerfile` (multi-stage, chạy bằng user thường, dùng gunicorn) và `docker-compose.yml` (API + PostgreSQL 16). Máy khác chỉ cần cài Docker, không phải sửa gì:

```powershell
docker compose up --build        # build và chạy (API ở http://localhost:5000)
docker compose up --build -d     # chạy nền
docker compose logs -f api       # xem log
docker compose down              # dừng (giữ dữ liệu)
docker compose down -v           # dừng và xóa luôn dữ liệu Postgres
```

Cách hoạt động:

- Service `db` có healthcheck `pg_isready`; service `api` chỉ khởi động khi `db` đã healthy (`depends_on: condition: service_healthy`).
- Khi container `api` khởi động, nó chạy `flask init-db` (tạo các bảng còn thiếu, chạy lại nhiều lần vẫn an toàn) rồi mới chạy gunicorn.
- Biến môi trường (`DB_URL`, `SECRET_KEY`, `LOG_LEVEL`) khai báo trong `docker-compose.yml`; mật khẩu trong file là mật khẩu dev, đổi khi triển khai thật.
- Dữ liệu Postgres lưu trong volume `pgdata`.
- `.env` và `.venv` bị loại khỏi image bởi `.dockerignore`.

Kiểm tra sau khi chạy:

```powershell
curl.exe -i http://localhost:5000/healthz
curl.exe -i http://localhost:5000/ready
```

### 10. Kiểm thử (pytest)

```powershell
pytest -v
```

Test dùng SQLite in-memory (`TestConfig`), không cần Docker hay Postgres.

| File | Nội dung |
|---|---|
| `tests/test_products.py` | CRUD sản phẩm, phân trang, reserve, soft delete, các mã lỗi |
| `tests/test_orders.py` | `POST /orders` (thành công, nhiều sản phẩm, giữ giá lúc đặt, sản phẩm không tồn tại / archived / trùng, dữ liệu sai), `GET /orders/<id>`, `GET /orders` có eager loading |
| `tests/test_health.py` | `/healthz` không chạm DB, `/ready` trả 200 và 503 khi DB lỗi |

**Kiểm tra N+1 query.** `GET /api/v1/orders` dùng `selectinload(Order.items).selectinload(OrderItem.product)`. Test `test_list_orders_has_no_n_plus_1` gắn listener `before_cursor_execute` để đếm số câu `SELECT` thật sự gửi xuống DB, chạy với 2 đơn và với 10 đơn, và khẳng định cả hai đều ≤ 4 câu (orders, count, items, products). Nếu lazy load xảy ra, số câu sẽ tăng theo số đơn (1 + N + 2N) và test sẽ fail.