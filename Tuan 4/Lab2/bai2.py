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
    app.run(debug=True)