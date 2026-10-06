
### 1.1.

curl.exe -i -X GET 'http://localhost:5000/orders?status=paid'

Kết quả:

HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:46:50 GMT
Content-Type: application/json
Content-Length: 534
Connection: close

{
  "data": [
    {
      "created_at": "2026-01-01T10:00:00Z",
      "customer_id": 101,
      "id": 1,
      "status": "paid",
      "total": 150.0
    },
    {
      "created_at": "2026-01-03T12:00:00Z",
      "customer_id": 101,
      "id": 3,
      "status": "paid",
      "total": 200.0
    },
    {
      "created_at": "2026-01-06T15:00:00Z",
      "customer_id": 102,
      "id": 6,
      "status": "paid",
      "total": 99.9
    }
  ],
  "pagination": {
    "has_more": false,
    "limit": 10,
    "next_cursor": null
  }
}

---

### 1.2. 

curl.exe -i -X GET 'http://localhost:5000/orders?customer_id=101'

Kết quả:
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:47:22 GMT
Content-Type: application/json
Content-Length: 392
Connection: close

{
  "data": [
    {
      "created_at": "2026-01-01T10:00:00Z",
      "customer_id": 101,
      "id": 1,
      "status": "paid",
      "total": 150.0
    },
    {
      "created_at": "2026-01-03T12:00:00Z",
      "customer_id": 101,
      "id": 3,
      "status": "paid",
      "total": 200.0
    }
  ],
  "pagination": {
    "has_more": false,
    "limit": 10,
    "next_cursor": null
  }
}

---

### 1.3. Request Thiếu Dữ Liệu Bắt Buộc (Lỗi 400)

curl.exe -i -X GET 'http://localhost:5000/orders?status=paid&customer_id=101'

Kết quả:
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:48:24 GMT
Content-Type: application/json
Content-Length: 392
Connection: close

{
  "data": [
    {
      "created_at": "2026-01-01T10:00:00Z",
      "customer_id": 101,
      "id": 1,
      "status": "paid",
      "total": 150.0
    },
    {
      "created_at": "2026-01-03T12:00:00Z",
      "customer_id": 101,
      "id": 3,
      "status": "paid",
      "total": 200.0
    }
  ],
  "pagination": {
    "has_more": false,
    "limit": 10,
    "next_cursor": null
  }
}
