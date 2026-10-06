import base64
import json
import logging
import uuid
from flask import Flask, jsonify, request, Response
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ERROR_BASE = "localhost:3000"

class ProblemError(Exception):
    def __init__(self, status: int, title: str, detail: str = None, type_path: str = None, **extra):
        super().__init__(title)
        self.status = status
        self.title = title
        self.detail = detail
        self.type = f"{ERROR_BASE}/{type_path}" if type_path else "about:blank"
        self.extra = extra

def _make_problem_response(status: int, title: str, detail: str = None, type_url: str = "about:blank", **extra):
    body = {
        "type": type_url,
        "title": title,
        "status": status,
        "instance": request.path,
        "trace_id": str(uuid.uuid4())
    }
    if detail:
        body["detail"] = detail
    
    body.update(extra)

    response = jsonify(body)
    response.status_code = status
    response.headers["Content-Type"] = "application/problem+json"
    return response

@app.errorhandler(ProblemError)
def handle_problem_error(err):
    return _make_problem_response(
        status=err.status,
        title=err.title,
        detail=err.detail,
        type_url=err.type,
        **err.extra
    )

@app.errorhandler(HTTPException)
def handle_http_exception(err):
    return _make_problem_response(
        status=err.code,
        title=err.name,
        detail=err.description,
        type_url="about:blank"
    )

@app.errorhandler(Exception)
def handle_unexpected_error(err):
    logger.exception("Internal Server Error xảy ra: %s", str(err))
    
    return _make_problem_response(
        status=500,
        title="Internal Server Error",
        detail="Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.",
        type_url="about:blank"
    )

# --- MOCK DATABASES ---

posts_db = [
    {"id": 1, "title": "test", "content": "week 4", "user_id": 1},
]

comments_db = [
    {"id": 1, "post_id": 1, "user_id": 2, "content": "Bài viết hay quá!"}
]

tags_db = [
    {"id": 1, "name": "python"},
    {"id": 2, "name": "flask"}
]

post_tags_db = [
    {"post_id": 1, "tag_id": 1},
    {"post_id": 1, "tag_id": 2}
]

users_db = [
    {"id": 1, "username": "author_user", "bio": "Lập trình viên Flask"},
    {"id": 2, "username": "reader_user", "bio": "Người đọc yêu công nghệ"}
]

follows_db = [
    {"follower_id": 2, "following_id": 1}
]

orders_db = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 150.0, "created_at": "2026-01-01T10:00:00Z"},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 85.5, "created_at": "2026-01-02T11:00:00Z"},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 200.0, "created_at": "2026-01-03T12:00:00Z"},
    {"id": 4, "customer_id": 103, "status": "cancelled", "total": 45.0, "created_at": "2026-01-04T13:00:00Z"},
    {"id": 6, "customer_id": 102, "status": "paid", "total": 99.9, "created_at": "2026-01-06T15:00:00Z"},
    {"id": 7, "customer_id": 104, "status": "pending", "total": 120.0, "created_at": "2026-01-07T16:00:00Z"}
]


def encode_cursor(data: dict) -> str:
    json_bytes = json.dumps(data).encode('utf-8')
    return base64.b64encode(json_bytes).decode('utf-8')

def decode_cursor(cursor_str: str) -> dict:
    try:
        json_bytes = base64.b64decode(cursor_str.encode('utf-8'))
        return json.loads(json_bytes.decode('utf-8'))
    except Exception:
        raise ProblemError(400, "Bad Request", "Cursor không hợp lệ hoặc bị hỏng")


@app.route('/orders', methods=['GET'])
@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    status_filter = request.args.get('status', type=str)
    customer_id_filter = request.args.get('customer_id', type=int)
    sort_by = request.args.get('sort', default='id', type=str)
    fields_param = request.args.get('fields', type=str)
    limit = request.args.get('limit', default=10, type=int)
    cursor_param = request.args.get('cursor', type=str)

    results = list(orders_db)

    if status_filter:
        results = [o for o in results if o['status'] == status_filter]
    if customer_id_filter is not None:
        results = [o for o in results if o['customer_id'] == customer_id_filter]

    reverse = False
    sort_field = sort_by
    if sort_by.startswith('-'):
        reverse = True
        sort_field = sort_by[1:]

    if results and sort_field not in results[0]:
        raise ProblemError(400, "Bad Request", f"Trường sắp xếp '{sort_field}' không hợp lệ")

    results.sort(key=lambda x: x.get(sort_field), reverse=reverse)

    if cursor_param:
        decoded_cursor = decode_cursor(cursor_param)
        last_id = decoded_cursor.get('last_id')
        
        start_index = 0
        for idx, item in enumerate(results):
            if item['id'] == last_id:
                start_index = idx + 1
                break
        results = results[start_index:]

    has_more = len(results) > limit
    paginated_results = results[:limit]

    next_cursor = None
    if has_more and paginated_results:
        last_item = paginated_results[-1]
        next_cursor = encode_cursor({"last_id": last_item['id']})

    if fields_param:
        fields = [f.strip() for f in fields_param.split(',') if f.strip()]
        final_data = []
        for item in paginated_results:
            filtered_item = {k: v for k, v in item.items() if k in fields}
            final_data.append(filtered_item)
    else:
        final_data = paginated_results

    return jsonify({
        "data": final_data,
        "pagination": {
            "limit": limit,
            "has_more": has_more,
            "next_cursor": next_cursor
        }
    }), 200


@app.route('/api/v1/posts', methods=['GET'])
def get_posts():
    user_id = request.args.get('user_id', type=int)
    if user_id:
        filterd = [p for p in posts_db if p['user_id'] == user_id]
        return jsonify(filterd), 200
    return jsonify(posts_db), 200

@app.route('/api/v1/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data or 'user_id' not in data:
        raise ProblemError(400, "Bad Request", "Thiếu 'title' hoặc 'content' hoặc 'user_id'")
    
    new_post = {
        "id": len(posts_db) + 1,
        "title": data['title'],
        "content": data['content'],
        "user_id": data['user_id']
    }
    posts_db.append(new_post)
    return jsonify(new_post), 201

@app.route('/api/v1/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise ProblemError(404, "Not Found", "Không tìm thấy bài viết")
    return jsonify(post), 200

@app.route('/api/v1/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise ProblemError(404, "Not Found", "Không tìm thấy bài viết")
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id:
        raise ProblemError(401, "Unauthorized", "Chưa xác thực danh tính")
    if post['user_id'] != user_id:
        raise ProblemError(403, "Forbidden", "Bạn không có quyền chỉnh sửa bài viết của người khác")
    data = request.get_json()
    if not data:
        raise ProblemError(400, "Bad Request", "Dữ liệu cập nhật không hợp lệ")
    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])
    return jsonify(post), 200

@app.route('/api/v1/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global posts_db
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise ProblemError(404, "Not Found", "Không tìm thấy bài viết")
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id:
        raise ProblemError(401, "Unauthorized", "Chưa xác thực danh tính")
    if post['user_id'] != user_id:
        raise ProblemError(403, "Forbidden", "Bạn không có quyền xóa bài viết của người khác")
    posts_db = [p for p in posts_db if p['id'] != post_id]
    return jsonify({"message": "Đã xóa bài viết thành công"}), 200

@app.route('/api/v1/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise ProblemError(404, "Not Found", "Không tìm thấy bài viết")
    comments = [c for c in comments_db if c['post_id'] == post_id]
    return jsonify(comments), 200

@app.route('/api/v1/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise ProblemError(404, "Not Found", "Không tìm thấy bài viết")
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id:
        raise ProblemError(401, "Unauthorized", "Chưa xác thực danh tính")
    data = request.get_json()
    if not data or 'content' not in data:
        raise ProblemError(400, "Bad Request", "Thiếu nội dung bình luận")
    new_comment = {
        "id": len(comments_db) + 1,
        "post_id": post_id,
        "user_id": user_id,
        "content": data['content']
    }
    comments_db.append(new_comment)
    return jsonify(new_comment), 201

@app.route('/api/v1/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    global comments_db
    comment = next((c for c in comments_db if c['id'] == comment_id and c['post_id'] == post_id), None)
    if not comment:
        raise ProblemError(404, "Not Found", "Không tìm thấy bình luận")
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id:
        raise ProblemError(401, "Unauthorized", "Chưa xác thực danh tính")
    if comment['user_id'] != user_id:
        raise ProblemError(403, "Forbidden", "Bạn không có quyền xóa bình luận của người khác")
    comments_db = [c for c in comments_db if c['id'] != comment_id]
    return jsonify({"message": "Đã xóa bình luận thành công"}), 200

@app.route('/api/v1/posts/<int:post_id>/tags', methods=['GET'])
def get_post_tags(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise ProblemError(404, "Not Found", "Không tìm thấy bài viết")
    tag_ids = [pt['tag_id'] for pt in post_tags_db if pt['post_id'] == post_id]
    tags = [t for t in tags_db if t['id'] in tag_ids]
    return jsonify(tags), 200

@app.route('/api/v1/posts/<int:post_id>/tags/<int:tag_id>', methods=['PUT'])
def add_tag_to_post(post_id, tag_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise ProblemError(404, "Not Found", "Không tìm thấy bài viết")
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id or post['user_id'] != user_id:
        raise ProblemError(403, "Forbidden", "Không có quyền gán thẻ cho bài viết này")
    tag = next((t for t in tags_db if t['id'] == tag_id), None)
    if not tag:
        raise ProblemError(404, "Not Found", "Không tìm thấy thẻ")
    exists = any(pt for pt in post_tags_db if pt['post_id'] == post_id and pt['tag_id'] == tag_id)
    if not exists:
        post_tags_db.append({"post_id": post_id, "tag_id": tag_id})
    return jsonify({"message": "Gán thẻ thành công"}), 200

@app.route('/api/v1/posts/<int:post_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_tag_from_post(post_id, tag_id):
    global post_tags_db
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise ProblemError(404, "Not Found", "Không tìm thấy bài viết")
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id or post['user_id'] != user_id:
        raise ProblemError(403, "Forbidden", "Không có quyền gỡ thẻ bài viết này")
    post_tags_db = [pt for pt in post_tags_db if not (pt['post_id'] == post_id and pt['tag_id'] == tag_id)]
    return jsonify({"message": "Đã gỡ thẻ khỏi bài viết"}), 200

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        raise ProblemError(404, "Not Found", "Không tìm thấy người dùng")
    return jsonify(user), 200

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    auth_user_id = request.headers.get('X-User-ID', type=int)
    if not auth_user_id or auth_user_id != user_id:
        raise ProblemError(403, "Forbidden", "Không có quyền chỉnh sửa hồ sơ này")
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        raise ProblemError(404, "Not Found", "Không tìm thấy người dùng")
    data = request.get_json()
    if not data:
        raise ProblemError(400, "Bad Request", "Dữ liệu không hợp lệ")
    user['username'] = data.get('username', user['username'])
    user['bio'] = data.get('bio', user['bio'])
    return jsonify(user), 200

@app.route('/api/v1/users/<int:user_id>/followers', methods=['POST'])
def follow_user(user_id):
    follower_id = request.headers.get('X-User-ID', type=int)
    if not follower_id:
        raise ProblemError(401, "Unauthorized", "Chưa xác thực danh tính")
    if follower_id == user_id:
        raise ProblemError(400, "Bad Request", "Không thể tự theo dõi chính mình")
    target_user = next((u for u in users_db if u['id'] == user_id), None)
    if not target_user:
        raise ProblemError(404, "Not Found", "Không tìm thấy người dùng")
    exists = any(f for f in follows_db if f['follower_id'] == follower_id and f['following_id'] == user_id)
    if not exists:
        follows_db.append({"follower_id": follower_id, "following_id": user_id})
    return jsonify({"message": "Theo dõi thành công"}), 201

@app.route('/api/v1/users/<int:user_id>/followers', methods=['DELETE'])
def unfollow_user(user_id):
    global follows_db
    follower_id = request.headers.get('X-User-ID', type=int)
    if not follower_id:
        raise ProblemError(401, "Unauthorized", "Chưa xác thực danh tính")
    follows_db = [f for f in follows_db if not (f['follower_id'] == follower_id and f['following_id'] == user_id)]
    return jsonify({"message": "Đã hủy theo dõi thành công"}), 200

@app.route('/api/v1/test-error')
def test_error():
    raise Exception("Test unexpected exception")

if __name__ == '__main__':
    app.run(port=5000, debug=True)