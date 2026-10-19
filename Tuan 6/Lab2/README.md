# Tuan 6 - Lab 2

## Kết quả gọi API bằng `curl.exe`

Khởi động ứng dụng bằng lệnh:

```powershell
python app.py
```

### 1. Sắp xếp theo giá giảm dần (-price) và lọc theo danh mục category=1:   

```powershell
curl.exe "http://localhost:5000/api/v1/books?category=1&sort=-price&limit=5"
```

Output:

```json
{
  "data": [
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_24",
      "isbn": "9780132350824",
      "numeric_id": 24,
      "price_vnd": 340000,
      "stock": 34,
      "title": "Sách Lập Trình Tập 24"
    },
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_23",
      "isbn": "9780132350823",
      "numeric_id": 23,
      "price_vnd": 330000,
      "stock": 33,
      "title": "Sách Lập Trình Tập 23"
    },
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_22",
      "isbn": "9780132350822",
      "numeric_id": 22,
      "price_vnd": 320000,
      "stock": 32,
      "title": "Sách Lập Trình Tập 22"
    },
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_21",
      "isbn": "9780132350821",
      "numeric_id": 21,
      "price_vnd": 310000,
      "stock": 31,
      "title": "Sách Lập Trình Tập 21"
    },
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_20",
      "isbn": "9780132350820",
      "numeric_id": 20,
      "price_vnd": 300000,
      "stock": 30,
      "title": "Sách Lập Trình Tập 20"
    }
  ],
  "page": {
    "more": true,
    "next": "eyJzIjogIi1wcmljZSIsICJ2IjogMzAwMDAwLCAiaSI6IDIwfQ"
  }
}
```

### 2. Sử dụng next cursor trả về từ kết quả trước để phân trang tiếp theo:   

```powershell
curl.exe "http://localhost:5000/api/v1/books?category=1&sort=-price&limit=5&cursor=eyJzIjogIi1wcmljZSIsICJ2IjogMzAwMDAwLCAiaSI6IDIwfQ"
```

Output:

```json
{
  "data": [
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_19",
      "isbn": "9780132350819",
      "numeric_id": 19,
      "price_vnd": 290000,
      "stock": 29,
      "title": "Sách Lập Trình Tập 19"
    },
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_18",
      "isbn": "9780132350818",
      "numeric_id": 18,
      "price_vnd": 280000,
      "stock": 28,
      "title": "Sách Lập Trình Tập 18"
    },
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_17",
      "isbn": "9780132350817",
      "numeric_id": 17,
      "price_vnd": 270000,
      "stock": 27,
      "title": "Sách Lập Trình Tập 17"
    },
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_16",
      "isbn": "9780132350816",
      "numeric_id": 16,
      "price_vnd": 260000,
      "stock": 26,
      "title": "Sách Lập Trình Tập 16"
    },
    {
      "authors": [],
      "category": {
        "id": 1,
        "name": "Công nghệ",
        "slug": "tech"
      },
      "id": "book_15",
      "isbn": "9780132350815",
      "numeric_id": 15,
      "price_vnd": 250000,
      "stock": 25,
      "title": "Sách Lập Trình Tập 15"
    }
  ],
  "page": {
    "more": true,
    "next": "eyJzIjogIi1wcmljZSIsICJ2IjogMjUwMDAwLCAiaSI6IDE1fQ"
  }
}
```

### 3. Kiểm tra lỗi bảo mật / validate khi truyền tham số sort không có trong Whitelist[cite: 23, 28]:

```powershell
curl.exe "http://localhost:5000/api/v1/books?sort=malicious_column"```

Output:

```json
{
  "error": "bad_sort",
  "message": "Sort key không hợp lệ"
}
curl: (3) URL rejected: Bad hostname
```
