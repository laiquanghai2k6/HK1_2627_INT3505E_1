# Tuan 6 - BTVN 2

## Kết quả gọi API bằng `curl.exe`

Khởi động ứng dụng bằng lệnh:

```powershell
python app.py
```

### 1. Sử dụng chiến lược Offset Pagination kết hợp lọc theo thể loại tech và sắp xếp đa khóa (-price,title):

```powershell
curl.exe "http://localhost:5000/api/v1/books?strategy=offset&genre=tech&sort=-price,title&limit=5&offset=0"```

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
  "pagination": {
    "has_next": true,
    "limit": 5,
    "offset": 0,
    "strategy": "offset",
    "total": 24
  }
}
```

### 2.Sử dụng chiến lược Cursor Pagination (mặc định) kèm lọc thể loại tech:

```powershell
curl.exe "http://localhost:5000/api/v1/books?strategy=cursor&genre=tech&sort=-price&limit=5"```

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
  "pagination": {
    "has_more": true,
    "limit": 5,
    "next_cursor": "eyJpZCI6IDIwfQ",
    "strategy": "cursor"
  }
}
```

### 3. Truyền tiếp next_cursor cho trang kế tiếp của Cursor strategy:

```powershell
curl.exe "http://localhost:5000/api/v1/books?strategy=cursor&genre=tech&sort=-price&limit=5&cursor=eyJpZCI6IDIwfQ"```

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
    }
  ],
  "pagination": {
    "has_more": false,
    "limit": 5,
    "next_cursor": null,
    "strategy": "cursor"
  }
}
```
