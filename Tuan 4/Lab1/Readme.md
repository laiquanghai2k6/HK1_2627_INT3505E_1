
## 1. Xác định Resources trong miền

Dựa trên yêu cầu bài toán, hệ thống bao gồm các tài nguyên chính:

- **Users (`/users`)**: Tài khoản người dùng, quản lý hồ sơ cá nhân và theo dõi tác giả khác.
- **Posts (`/posts`)**: Bài viết do người dùng sáng tạo.
- **Comments (`/comments`)**: Bình luận của người dùng trên các bài viết.
- **Tags (`/tags`)**: Phân loại nội dung bài viết theo từ khóa/thẻ.
- **Followers (`/followers`)**: Mối quan hệ theo dõi giữa các người dùng.

---

## 2. Phân loại Resource Architecture

| Tài nguyên | Loại Resource | Endpoint URL Pattern | Mô tả |
| :--- | :--- | :--- | :--- |
| **Posts** | Collection / Item | `/api/v1/posts`<br>`/api/v1/posts/{post_id}` | Danh sách & Chi tiết bài viết |
| **Comments** | Sub-resource | `/api/v1/posts/{post_id}/comments`<br>`/api/v1/posts/{post_id}/comments/{comment_id}` | Bình luận thuộc về một bài viết cụ thể |
| **Tags** | Sub-resource | `/api/v1/posts/{post_id}/tags`<br>`/api/v1/posts/{post_id}/tags/{tag_id}` | Thẻ gán trên một bài viết |
| **Users** | Collection / Item | `/api/v1/users/{user_id}` | Hồ sơ cá nhân người dùng |
| **Followers** | Sub-resource | `/api/v1/users/{user_id}/followers` | Người theo dõi / Đăng ký theo dõi tác giả |

---

## 3. Cấu trúc Cây Endpoint (API Tree)

Phiên bản API được định dạng bằng path segment `/api/v1/`.

```text
/api/v1
│
├── /posts
│   ├── GET         - Lấy danh sách bài viết (lọc theo user_id qua query param)
│   ├── POST        - Tạo bài viết mới
│   │
│   └── /{post_id}
│       ├── GET     - Lấy chi tiết bài viết
│       ├── PUT     - Cập nhật bài viết (Yêu cầu xác thực chủ sở hữu)
│       ├── DELETE  - Xóa bài viết (Yêu cầu xác thực chủ sở hữu)
│       │
│       ├── /comments
│       │   ├── GET             - Lấy danh sách bình luận của bài viết
│       │   ├── POST            - Thêm bình luận mới vào bài viết
│       │   └── /{comment_id}
│       │       └──
### 4. Danh sách Endpoint API chi tiết & Kịch bản kiểm thử

#### 4.1. Bài viết (Posts)

##### GET /api/v1/posts: Lấy danh sách bài viết.
- Trường hợp 1: Lấy tất cả bài viết hiện có.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/posts
  - Response (200 OK):
    [
      {
        "content": "week 4",
        "id": 1,
        "title": "test",
        "user_id": 1
      }
    ]

- Trường hợp 2: Lọc danh sách bài viết theo tác giả (?user_id=<id>).
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/posts?user_id=1
  - Response (200 OK):
    [
      {
        "content": "week 4",
        "id": 1,
        "title": "test",
        "user_id": 1
      }
    ]

---

##### POST /api/v1/posts: Tạo bài viết mới.
- Trường hợp 1: Tạo thành công khi truyền đầy đủ title, content, user_id.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/posts -H "Content-Type: application/json" -d "{\"title\":\"Bài viết mới\",\"content\":\"Nội dung bài viết\",\"user_id\":1}"
  - Response (201 Created):
    {
      "content": "Nội dung bài viết",
      "id": 2,
      "title": "Bài viết mới",
      "user_id": 1
    }

- Trường hợp 2: Trả về lỗi 400 Bad Request nếu thiếu bất kỳ trường thông tin bắt buộc nào.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/posts -H "Content-Type: application/json" -d "{\"title\":\"Bài viết thiếu content\"}"
  - Response (400 Bad Request):
    {
      "error": "Thiếu 'title' hoặc 'content' hoặc 'user_id'"
    }

---

##### GET /api/v1/posts/{post_id}: Xem chi tiết bài viết theo ID.
- Trường hợp 1: Trả về thông tin bài viết nếu ID tồn tại.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/posts/1
  - Response (200 OK):
    {
      "content": "week 4",
      "id": 1,
      "title": "test",
      "user_id": 1
    }

- Trường hợp 2: Trả về lỗi 404 Not Found nếu bài viết không tồn tại.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/posts/999
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy bài viết"
    }

---

##### PUT /api/v1/posts/{post_id}: Cập nhật tiêu đề hoặc nội dung bài viết.
- Trường hợp 1: Cập nhật thành công khi người gửi request (X-User-ID) chính là tác giả bài viết.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/posts/1 -H "Content-Type: application/json" -H "X-User-ID: 1" -d "{\"title\":\"Tiêu đề mới\",\"content\":\"Nội dung mới\"}"
  - Response (200 OK):
    {
      "content": "Nội dung mới",
      "id": 1,
      "title": "Tiêu đề mới",
      "user_id": 1
    }

- Trường hợp 2: Trả về lỗi 401 Unauthorized nếu thiếu header X-User-ID.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/posts/1 -H "Content-Type: application/json" -d "{\"title\":\"Tiêu đề mới\"}"
  - Response (401 Unauthorized):
    {
      "error": "Chưa xác thực danh tính"
    }

- Trường hợp 3: Trả về lỗi 403 Forbidden nếu chỉnh sửa bài viết của người khác.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/posts/1 -H "Content-Type: application/json" -H "X-User-ID: 2" -d "{\"title\":\"Sửa trộm bài\"}"
  - Response (403 Forbidden):
    {
      "error": "Bạn không có quyền chỉnh sửa bài viết của người khác"
    }

- Trường hợp 4: Trả về lỗi 404 Not Found nếu bài viết không tồn tại.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/posts/999 -H "Content-Type: application/json" -H "X-User-ID: 1" -d "{\"title\":\"Tiêu đề mới\"}"
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy bài viết"
    }

---

##### DELETE /api/v1/posts/{post_id}: Xóa bài viết.
- Trường hợp 1: Xóa thành công khi người gửi request (X-User-ID) là tác giả bài viết.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1 -H "X-User-ID: 1"
  - Response (200 OK):
    {
      "message": "Đã xóa bài viết thành công"
    }

- Trường hợp 2: Trả về lỗi 401 Unauthorized nếu chưa xác thực header.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1
  - Response (401 Unauthorized):
    {
      "error": "Chưa xác thực danh tính"
    }

- Trường hợp 3: Trả về lỗi 403 Forbidden nếu cố tình xóa bài viết của người khác.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1 -H "X-User-ID: 2"
  - Response (403 Forbidden):
    {
      "error": "Bạn không có quyền xóa bài viết của người khác"
    }

- Trường hợp 4: Trả về lỗi 404 Not Found nếu bài viết không tồn tại.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/999 -H "X-User-ID: 1"
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy bài viết"
    }

---

#### 4.2. Bình luận (Comments)

##### GET /api/v1/posts/{post_id}/comments: Xem danh sách bình luận của bài viết.
- Trường hợp 1: Trả về danh sách các bình luận thuộc về bài viết.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/posts/1/comments
  - Response (200 OK):
    [
      {
        "content": "Bài viết hay quá!",
        "id": 1,
        "post_id": 1,
        "user_id": 2
      }
    ]

- Trường hợp 2: Trả về lỗi 404 Not Found nếu bài viết không tồn tại.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/posts/999/comments
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy bài viết"
    }

---

##### POST /api/v1/posts/{post_id}/comments: Thêm bình luận mới vào bài viết.
- Trường hợp 1: Thêm bình luận thành công khi truyền đủ content và header X-User-ID.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/posts/1/comments -H "Content-Type: application/json" -H "X-User-ID: 2" -d "{\"content\":\"Bình luận rất bổ ích!\"}"
  - Response (201 Created):
    {
      "content": "Bình luận rất bổ ích!",
      "id": 2,
      "post_id": 1,
      "user_id": 2
    }

- Trường hợp 2: Trả về lỗi 401 Unauthorized nếu thiếu header xác thực identity.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/posts/1/comments -H "Content-Type: application/json" -d "{\"content\":\"Bình luận ẩn danh\"}"
  - Response (401 Unauthorized):
    {
      "error": "Chưa xác thực danh tính"
    }

- Trường hợp 3: Trả về lỗi 400 Bad Request nếu thiếu nội dung content.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/posts/1/comments -H "Content-Type: application/json" -H "X-User-ID: 2" -d "{}"
  - Response (400 Bad Request):
    {
      "error": "Thiếu nội dung bình luận"
    }

- Trường hợp 4: Trả về lỗi 404 Not Found nếu bài viết cần bình luận không tồn tại.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/posts/999/comments -H "Content-Type: application/json" -H "X-User-ID: 2" -d "{\"content\":\"Bình luận\"}"
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy bài viết"
    }

---

##### DELETE /api/v1/posts/{post_id}/comments/{comment_id}: Xóa một bình luận.
- Trường hợp 1: Xóa bình luận thành công nếu X-User-ID chính là người viết bình luận.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1/comments/1 -H "X-User-ID: 2"
  - Response (200 OK):
    {
      "message": "Đã xóa bình luận thành công"
    }

- Trường hợp 2: Trả về lỗi 401 Unauthorized nếu chưa xác thực identity.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1/comments/1
  - Response (401 Unauthorized):
    {
      "error": "Chưa xác thực danh tính"
    }

- Trường hợp 3: Trả về lỗi 403 Forbidden nếu xóa bình luận của người khác.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1/comments/1 -H "X-User-ID: 1"
  - Response (403 Forbidden):
    {
      "error": "Bạn không có quyền xóa bình luận của người khác"
    }

- Trường hợp 4: Trả về lỗi 404 Not Found nếu bình luận hoặc bài viết không tồn tại.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1/comments/999 -H "X-User-ID: 2"
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy bình luận"
    }

---

#### 4.3. Thẻ (Tags)

##### GET /api/v1/posts/{post_id}/tags: Lấy danh sách tất cả thẻ gán trên bài viết.
- Trường hợp 1: Trả về các thẻ liên kết với bài viết tương ứng.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/posts/1/tags
  - Response (200 OK):
    [
      {
        "id": 1,
        "name": "python"
      },
      {
        "id": 2,
        "name": "flask"
      }
    ]

- Trường hợp 2: Trả về lỗi 404 Not Found nếu bài viết không tồn tại.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/posts/999/tags
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy bài viết"
    }

---

##### PUT /api/v1/posts/{post_id}/tags/{tag_id}: Gán thẻ vào bài viết.
- Trường hợp 1: Gán thẻ thành công khi X-User-ID là tác giả bài viết và tag_id hợp lệ.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/posts/1/tags/1 -H "X-User-ID: 1"
  - Response (200 OK):
    {
      "message": "Gán thẻ thành công"
    }

- Trường hợp 2: Trả về lỗi 403 Forbidden nếu không phải tác giả bài viết.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/posts/1/tags/1 -H "X-User-ID: 2"
  - Response (403 Forbidden):
    {
      "error": "Không có quyền gán thẻ cho bài viết này"
    }

- Trường hợp 3: Trả về lỗi 404 Not Found nếu bài viết hoặc thẻ không tồn tại.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/posts/1/tags/999 -H "X-User-ID: 1"
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy thẻ"
    }

---

##### DELETE /api/v1/posts/{post_id}/tags/{tag_id}: Gỡ thẻ khỏi bài viết.
- Trường hợp 1: Gỡ thẻ thành công nếu người gửi request là tác giả bài viết.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1/tags/1 -H "X-User-ID: 1"
  - Response (200 OK):
    {
      "message": "Đã gỡ thẻ khỏi bài viết"
    }

- Trường hợp 2: Trả về lỗi 403 Forbidden nếu không có quyền thao tác trên bài viết.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/1/tags/1 -H "X-User-ID: 2"
  - Response (403 Forbidden):
    {
      "error": "Không có quyền gỡ thẻ bài viết này"
    }

- Trường hợp 3: Trả về lỗi 404 Not Found nếu bài viết không tồn tại.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/posts/999/tags/1 -H "X-User-ID: 1"
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy bài viết"
    }

---

#### 4.4. Hồ sơ người dùng & Theo dõi (Users & Follow)

##### GET /api/v1/users/{user_id}: Lấy thông tin hồ sơ người dùng.
- Trường hợp 1: Trả về thông tin chi tiết hồ sơ cá nhân.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/users/1
  - Response (200 OK):
    {
      "bio": "Lập trình viên Flask",
      "id": 1,
      "username": "author_user"
    }

- Trường hợp 2: Trả về lỗi 404 Not Found nếu người dùng không tồn tại.
  - cURL:
    curl.exe -X GET http://127.0.0.1:5000/api/v1/users/999
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy người dùng"
    }

---

##### PUT /api/v1/users/{user_id}: Cập nhật thông tin hồ sơ (username, bio).
- Trường hợp 1: Cập nhật thành công nếu X-User-ID trùng khớp với {user_id}.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/users/1 -H "Content-Type: application/json" -H "X-User-ID: 1" -d "{\"username\":\"new_name\",\"bio\":\"New bio\"}"
  - Response (200 OK):
    {
      "bio": "New bio",
      "id": 1,
      "username": "new_name"
    }

- Trường hợp 2: Trả về lỗi 403 Forbidden nếu cố gắng chỉnh sửa hồ sơ người khác.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/users/1 -H "Content-Type: application/json" -H "X-User-ID: 2" -d "{\"username\":\"hacker\"}"
  - Response (403 Forbidden):
    {
      "error": "Không có quyền chỉnh sửa hồ sơ này"
    }

- Trường hợp 3: Trả về lỗi 400 Bad Request nếu dữ liệu gửi lên không đúng định dạng JSON.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/users/1 -H "Content-Type: application/json" -H "X-User-ID: 1" -d "invalid-json"
  - Response (400 Bad Request):
    {
      "error": "Dữ liệu không hợp lệ"
    }

- Trường hợp 4: Trả về lỗi 404 Not Found nếu người dùng không tồn tại.
  - cURL:
    curl.exe -X PUT http://127.0.0.1:5000/api/v1/users/999 -H "Content-Type: application/json" -H "X-User-ID: 999" -d "{\"username\":\"test\"}"
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy người dùng"
    }

---

##### POST /api/v1/users/{user_id}/followers: Theo dõi người dùng.
- Trường hợp 1: Theo dõi thành công người dùng khác khi truyền header X-User-ID.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/users/2/followers -H "X-User-ID: 1"
  - Response (201 Created):
    {
      "message": "Theo dõi thành công"
    }

- Trường hợp 2: Trả về lỗi 401 Unauthorized nếu thiếu header xác thực identity.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/users/2/followers
  - Response (401 Unauthorized):
    {
      "error": "Chưa xác thực danh tính"
    }

- Trường hợp 3: Trả về lỗi 400 Bad Request nếu cố tình tự theo dõi chính mình (X-User-ID == user_id).
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/users/1/followers -H "X-User-ID: 1"
  - Response (400 Bad Request):
    {
      "error": "Không thể tự theo dõi chính mình"
    }

- Trường hợp 4: Trả về lỗi 404 Not Found nếu tài khoản cần theo dõi không tồn tại.
  - cURL:
    curl.exe -X POST http://127.0.0.1:5000/api/v1/users/999/followers -H "X-User-ID: 1"
  - Response (404 Not Found):
    {
      "error": "Không tìm thấy người dùng"
    }

---

##### DELETE /api/v1/users/{user_id}/followers: Bỏ theo dõi người dùng.
- Trường hợp 1: Bỏ theo dõi thành công khi gửi request hợp lệ.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/users/2/followers -H "X-User-ID: 1"
  - Response (200 OK):
    {
      "message": "Đã hủy theo dõi thành công"
    }

- Trường hợp 2: Trả về lỗi 401 Unauthorized nếu chưa truyền thông tin xác thực.
  - cURL:
    curl.exe -X DELETE http://127.0.0.1:5000/api/v1/users/2/followers
  - Response (401 Unauthorized):
    {
      "error": "Chưa xác thực danh tính"
    }