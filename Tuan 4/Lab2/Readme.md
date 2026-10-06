

### 1.1. Request tới Endpoint `/resources/{id}` (Lỗi 404)

curl.exe -i -X GET http://127.0.0.1:5000/api/v1/users/999

Kết quả:

HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:30:44 GMT
Content-Type: application/problem+json
Content-Length: 229
Connection: close
{
  "detail": "Không tìm thấy người dùng",
  "instance": "/api/v1/users/999",
  "status": 404,
  "title": "Not Found",
  "trace_id": "2cada044-c95d-4d5a-8277-5887f48446c7",
  "type": "about:blank"
}

---

### 1.2. Request Thiếu Authentication Header (Lỗi 401)

Thực hiện tạo bình luận nhưng không truyền header `X-User-ID`:

curl.exe -i -X POST http://127.0.0.1:5000/api/v1/posts/1/comments -H "Content-Type: application/json" -d '{"content":"Bài viết rất hay!"}'


Kết quả:
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:34:22 GMT
Content-Type: application/problem+json
Content-Length: 227
Connection: close

{
  "detail": "Ch\u01b0a x\u00e1c th\u1ef1c danh t\u00ednh",
  "instance": "/api/v1/posts/1/comments",
  "status": 401,
  "title": "Unauthorized",
  "trace_id": "75243c1e-6df6-4c64-95d4-5927da3ccd64",
  "type": "about:blank"
}

---

### 1.3. Request Thiếu Dữ Liệu Bắt Buộc (Lỗi 400)

Tạo bài viết mới nhưng không truyền `title`:


curl.exe -i -X POST http://127.0.0.1:5000/api/v1/posts -H "Content-Type: application/json" -d '{"content":"Nội dung thiếu title","user_id":1}'

Kết quả:

HTTP/1.1 400 BAD REQUEST
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:34:51 GMT
Content-Type: application/problem+json
Content-Length: 277
Connection: close

{
  "detail": "Failed to decode JSON object: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
  "instance": "/api/v1/posts",
  "status": 400,
  "title": "Bad Request",
  "trace_id": "fd23120d-ac8e-4f36-b335-122a362a36f2",
  "type": "about:blank"
}
---

### 1.4. Request Không Có Quyền Chỉnh Sửa (Lỗi 403)

Dùng `X-User-ID: 2` để sửa bài viết thuộc quyền của `user_id: 1`:

curl.exe -i -X PUT http://127.0.0.1:5000/api/v1/posts/1 -H "Content-Type: application/json" -H "X-User-ID: 2" -d '{"title":"Sửa trái phép"}'

Kết quả:

HTTP/1.1 403 FORBIDDEN
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:35:17 GMT
Content-Type: application/problem+json
Content-Length: 284
Connection: close

{
  "detail": "B\u1ea1n kh\u00f4ng c\u00f3 quy\u1ec1n ch\u1ec9nh s\u1eeda b\u00e0i vi\u1ebft c\u1ee7a ng\u01b0\u1eddi kh\u00e1c",
  "instance": "/api/v1/posts/1",
  "status": 403,
  "title": "Forbidden",
  "trace_id": "332ccb36-c338-45b4-be5f-8d95f32addb8",
  "type": "about:blank"
}
---

### 1.5. Kiểm Thử Header Accept (Trả về `application/problem+json` khi thiếu Accept hoặc dùng Accept JSON)


curl.exe -i -X GET http://127.0.0.1:5000/api/v1/users/999 -H "Accept: application/json"

Kết quả:
HTTP/1.1 404 NOT FOUND
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:37:57 GMT
Content-Type: application/problem+json
Content-Length: 229
Connection: close

{
  "detail": "Kh\u00f4ng t\u00ecm th\u1ea5y ng\u01b0\u1eddi d\u00f9ng",
  "instance": "/api/v1/users/999",
  "status": 404,
  "title": "Not Found",
  "trace_id": "206ac2be-3c0c-4195-90e0-6945fe6490c7",
  "type": "about:blank"
}
---

### 1.6. Xử Lý Exception Chưa Bắt (Lỗi Server 500)

Gửi request kích hoạt lỗi chưa được xử lý trên hệ thống:

curl.exe -i -X GET http://127.0.0.1:5000/api/v1/test-error

Kết quả:
HTTP/1.1 500 INTERNAL SERVER ERROR
Server: Werkzeug/3.1.8 Python/3.10.11
Date: Tue, 06 Oct 2026 11:40:54 GMT
Content-Type: application/problem+json
Content-Length: 277
Connection: close

{
  "detail": "\u0110\u00e3 x\u1ea3y ra l\u1ed7i h\u1ec7 th\u1ed1ng. Vui l\u00f2ng th\u1eedl\u1ea1i sau.",
  "instance": "/api/v1/test-error",
  "status": 500,
  "title": "Internal Server Error",
  "trace_id": "8a168df7-d5ca-4d57-a536-3237efccb1a2",
  "type": "about:blank"
}