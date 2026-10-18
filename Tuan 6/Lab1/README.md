# Tuan 6 - Lab 1

## Kết quả gọi API bằng `curl.exe`

Khởi động ứng dụng bằng lệnh:

```powershell
python app.py
```

### 1. Lấy danh sách sách

```powershell
curl.exe "http://127.0.0.1:5000/api/v1/books?limit=2"
```

Output:

```json
{
  "data": [
    {
      "id": "book_24",
      "numeric_id": 24,
      "title": "Sách Lập Trình Tập 24",
      "isbn": "9780132350824",
      "price_vnd": 340000,
      "stock": 34,
      "category": {"id": 1, "name": "Công nghệ", "slug": "tech"},
      "authors": []
    },
    {
      "id": "book_23",
      "numeric_id": 23,
      "title": "Sách Lập Trình Tập 23",
      "isbn": "9780132350823",
      "price_vnd": 330000,
      "stock": 33,
      "category": {"id": 1, "name": "Công nghệ", "slug": "tech"},
      "authors": []
    }
  ],
  "pagination": {
    "next_cursor": "eyJzIjogIi1pZCIsICJ2IjogMjMsICJpIjogMjN9",
    "has_more": true,
    "limit": 2
  }
}
```

### 2. Lấy thông tin sách có mã `1`

```powershell
curl.exe "http://127.0.0.1:5000/api/v1/books/1"
```

Output:

```json
{
  "id": "book_1",
  "numeric_id": 1,
  "title": "Sách Lập Trình Tập 1",
  "isbn": "9780132350801",
  "price_vnd": 110000,
  "stock": 11,
  "category": {"id": 1, "name": "Công nghệ", "slug": "tech"},
  "authors": [
    {"id": 1, "name": "Robert C. Martin", "role": "lead"},
    {"id": 2, "name": "Martin Fowler", "role": "co"}
  ]
}
```

### 3. Kiểm tra sort không hợp lệ

```powershell
curl.exe "http://127.0.0.1:5000/api/v1/books?sort=unknown"
```

Output:

```json
{
  "error": "invalid_sort",
  "message": "Sort key không hợp lệ. Cho phép: ['id', 'price', 'title']"
}
```
