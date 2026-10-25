# Security Audit Report - Social Network API

Báo cáo kiểm tra bảo mật (Security Audit) tập trung vào các điểm lộ lọt tiềm ẩn trong mô hình xác thực và xử lý tài nguyên.

## 1. Thiếu Whitelist Thuật toán Chữ ký JWT (Algorithm Confusion / `alg: none`)
- **Mô tả:** Server không ép cứng danh sách thuật toán được phép chấp nhận (ví dụ chỉ định `RS256`), mà tin tưởng hoàn toàn vào trường `alg` do client gửi lên trong header của JWT.
- **Điểm lộ/Rủi ro:** Kẻ tấn công có thể sửa `alg` thành `none` hoặc dùng Public Key của hệ thống để ký giả mạo chữ ký bằng thuật toán đối xứng (`HS256`), dẫn đến việc chiếm đoạt quyền truy cập trái phép hoàn toàn.
- **Khắc phục:** Cấu hình strict whitelist trong code verify token (ví dụ: `algorithms: ['RS256']`).

## 2. Lộ Refresh Token và Không áp dụng Refresh Token Rotation (Replay Attack)
- **Mô tả:** Hệ thống cấp một Refresh Token cố định dài hạn và không thay đổi nó sau mỗi lần client đổi lấy Access Token mới.
- **Điểm lộ/Rủi ro:** Nếu Refresh Token bị lộ thông qua XSS hoặc Network Sniffing, kẻ tấn công có thể sử dụng vô thời hạn để duy trì phiên đăng nhập của nạn nhân mà không bị phát hiện.
- **Khắc phục:** Triển khai cơ chế Refresh Token Rotation (mỗi lần refresh sẽ hủy token cũ, sinh token mới theo `family_id`) kết hợp phát hiện tấn công tái sử dụng (Replay Detection).

## 3. Lưu trữ Token không an toàn trên Client (LocalStorage vs. HttpOnly Cookie)
- **Mô tả:** Lưu trữ Access Token và Refresh Token trực tiếp vào `localStorage` hoặc `sessionStorage` của trình duyệt.
- **Điểm lộ/Rủi ro:** Bất kỳ đoạn mã JavaScript độc hại nào chạy trên trang (do dính lỗi XSS từ bên thứ ba hoặc dependency bị chiếm đoạt) đều có thể đánh cắp toàn bộ token và gửi về server của hacker.
- **Khắc phục:** Lưu trữ token nhạy cảm trong `HttpOnly`, `Secure`, và `SameSite=Strict` Cookie để ngăn chặn tuyệt đối việc truy cập bằng JavaScript phía client.

## 4. Thiếu Giới hạn Tốc độ (Rate Limiting) trên Endpoint Đăng nhập (`POST /auth/login`)
- **Mô tả:** Endpoint `/auth/login` không giới hạn số lượng request xuất phát từ một IP hoặc một tài khoản trong khoảng thời gian ngắn.
- **Điểm lộ/Rủi ro:** Kẻ tấn công dễ dàng thực hiện tấn công Brute-force hoặc Credential Stuffing để dò mật khẩu người dùng với tốc độ cao.
- **Khắc phục:** Áp dụng Rate Limiting (ví dụ tối đa 5 lần thử/phút cho mỗi IP/Email) và tích hợp Captcha khi phát hiện bất thường.

## 5. Lỗi Phân quyền Tài nguyên Ngang (BOLA / IDOR ở `GET /posts/{id}`)
- **Mô tả:** Endpoint `GET /posts/{id}` chỉ kiểm tra xem người dùng đã đăng nhập và có scope `posts:read` hay chưa, nhưng thiếu bước kiểm tra xem bài viết đó có ở trạng thái riêng tư (private/draft) hoặc bị khóa hay không.
- **Điểm lộ/Rủi ro:** Bất kỳ người dùng nào có token hợp lệ đều có thể thay đổi tham số `{id}` trên đường dẫn để truy cập vào các bài viết ẩn hoặc dữ liệu nội bộ của người dùng khác.
- **Khắc phục:** Kiểm tra chặt chẽ quyền sở hữu (`authorId` khớp với `userId` trong token) hoặc trạng thái hiển thị của tài nguyên trước khi trả về dữ liệu.