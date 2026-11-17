# lab08-starter — API Testing & Quality Assurance


## 1. Chuẩn bị và chạy API


```bash
python -m app --port 5000
```

API: `http://127.0.0.1:5000`

### REST endpoints

| Method | Path | Trả về |
|---|---|---|
| GET | `/health` | 200 |
| GET | `/books?author=&year=&page=` | 200, JSON array, page 1-based, 20 items/page |
| GET | `/books/{id}` | 200 / 400 (ID sai định dạng) / 404 |
| POST | `/books` | 201 / 400 / 409 (ISBN trùng) |
| PUT | `/books/{id}` | 200 / 400 / 404 / 409 |
| DELETE | `/books/{id}` | 204 (không body) / 400 / 404 |
| POST | `/auth/login` | 200 / 401, chỉ để minh họa |


## 2. Lab 3 — Postman/Newman

### Chuẩn bị



**Terminal 2 —  chạy Newman** (cũng từ thư mục gốc repository):

```powershell
npx newman run "books-api.postman_collection.json" `
  -e "postman/local.postman_environment.json" `
  -r cli,junitfull `
  --reporter-junitfull-export "reports/junit.xml"
```

### Ảnh minh chứng

Các đường dẫn dưới đây là **đường dẫn tạm**; hãy chụp ảnh kết quả thật và lưu/thay đường dẫn tương ứng trước khi nộp:

![Kết quả Newman: 7 requests, 0 failed, thời gian dưới 10 giây](success.png)



