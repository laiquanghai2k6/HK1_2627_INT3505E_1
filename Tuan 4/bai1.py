from flask import Flask, jsonify, request

app = Flask(__name__)

posts_db = [
    {"id": 1, "title": "test", "content": "week 4", "user_id": 1},
]

@app.route('/api/v1/posts', methods=['GET'])
def get_posts():
    user_id = request.args.get('user_id',type=int)
    if user_id:
        filterd = [p for p in posts_db if p['user_id'] == user_id]
        return jsonify(filterd),200
    return jsonify(posts_db),200

        
    
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

if __name__ == '__main__':
    app.run(debug=True)