from flask import Flask, jsonify, request

app = Flask(__name__)

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
        return jsonify({"error": "Thiếu 'title' hoặc 'content' hoặc 'user_id'"}), 400
    
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
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    return jsonify(post), 200

@app.route('/api/v1/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id:
        return jsonify({"error": "Chưa xác thực danh tính "}), 401
    if post['user_id'] != user_id:
        return jsonify({"error": "Bạn không có quyền chỉnh sửa bài viết của người khác"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "dữ liệu cập nhật không hợp lệ"}), 400
    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])
    return jsonify(post), 200

@app.route('/api/v1/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global posts_db
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id:
        return jsonify({"error": "Chưa xác thực danh tính"}), 401
    if post['user_id'] != user_id:
        return jsonify({"error": "Bạn không có quyền xóa bài viết của người khác"}), 403
    posts_db = [p for p in posts_db if p['id'] != post_id]
    return jsonify({"message": "Đã xóa bài viết thành công"}), 200

@app.route('/api/v1/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    comments = [c for c in comments_db if c['post_id'] == post_id]
    return jsonify(comments), 200

@app.route('/api/v1/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id:
        return jsonify({"error": "Chưa xác thực danh tính"}), 401
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Thiếu nội dung bình luận"}), 400
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
        return jsonify({"error": "Không tìm thấy bình luận"}), 404
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id:
        return jsonify({"error": "Chưa xác thực danh tính"}), 401
    if comment['user_id'] != user_id:
        return jsonify({"error": "Bạn không có quyền xóa bình luận của người khác"}), 403
    comments_db = [c for c in comments_db if c['id'] != comment_id]
    return jsonify({"message": "Đã xóa bình luận thành công"}), 200

@app.route('/api/v1/posts/<int:post_id>/tags', methods=['GET'])
def get_post_tags(post_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    tag_ids = [pt['tag_id'] for pt in post_tags_db if pt['post_id'] == post_id]
    tags = [t for t in tags_db if t['id'] in tag_ids]
    return jsonify(tags), 200

@app.route('/api/v1/posts/<int:post_id>/tags/<int:tag_id>', methods=['PUT'])
def add_tag_to_post(post_id, tag_id):
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id or post['user_id'] != user_id:
        return jsonify({"error": "Không có quyền gán thẻ cho bài viết này"}), 403
    tag = next((t for t in tags_db if t['id'] == tag_id), None)
    if not tag:
        return jsonify({"error": "Không tìm thấy thẻ"}), 404
    exists = any(pt for pt in post_tags_db if pt['post_id'] == post_id and pt['tag_id'] == tag_id)
    if not exists:
        post_tags_db.append({"post_id": post_id, "tag_id": tag_id})
    return jsonify({"message": "Gán thẻ thành công"}), 200

@app.route('/api/v1/posts/<int:post_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_tag_from_post(post_id, tag_id):
    global post_tags_db
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Không tìm thấy bài viết"}), 404
    user_id = request.headers.get('X-User-ID', type=int)
    if not user_id or post['user_id'] != user_id:
        return jsonify({"error": "Không có quyền gỡ thẻ bài viết này"}), 403
    post_tags_db = [pt for pt in post_tags_db if not (pt['post_id'] == post_id and pt['tag_id'] == tag_id)]
    return jsonify({"message": "Đã gỡ thẻ khỏi bài viết"}), 200

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404
    return jsonify(user), 200

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    auth_user_id = request.headers.get('X-User-ID', type=int)
    if not auth_user_id or auth_user_id != user_id:
        return jsonify({"error": "Không có quyền chỉnh sửa hồ sơ này"}), 403
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dữ liệu không hợp lệ"}), 400
    user['username'] = data.get('username', user['username'])
    user['bio'] = data.get('bio', user['bio'])
    return jsonify(user), 200

@app.route('/api/v1/users/<int:user_id>/followers', methods=['POST'])
def follow_user(user_id):
    follower_id = request.headers.get('X-User-ID', type=int)
    if not follower_id:
        return jsonify({"error": "Chưa xác thực danh tính"}), 401
    if follower_id == user_id:
        return jsonify({"error": "Không thể tự theo dõi chính mình"}), 400
    target_user = next((u for u in users_db if u['id'] == user_id), None)
    if not target_user:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404
    exists = any(f for f in follows_db if f['follower_id'] == follower_id and f['following_id'] == user_id)
    if not exists:
        follows_db.append({"follower_id": follower_id, "following_id": user_id})
    return jsonify({"message": "Theo dõi thành công"}), 201

@app.route('/api/v1/users/<int:user_id>/followers', methods=['DELETE'])
def unfollow_user(user_id):
    global follows_db
    follower_id = request.headers.get('X-User-ID', type=int)
    if not follower_id:
        return jsonify({"error": "Chưa xác thực danh tính"}), 401
    follows_db = [f for f in follows_db if not (f['follower_id'] == follower_id and f['following_id'] == user_id)]
    return jsonify({"message": "Đã hủy theo dõi thành công"}), 200

if __name__ == '__main__':
    app.run(debug=True)