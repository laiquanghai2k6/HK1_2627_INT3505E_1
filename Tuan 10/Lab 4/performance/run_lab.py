"""Run A/B/C against isolated, identically seeded databases; rebuild analysis."""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (("A", 10, 2, 30), ("B", 50, 5, 60), ("C", 200, 50, 30))


def load_report(name):
    text = (ROOT / "reports" / f"{name}.html").read_text(encoding="utf-8")
    return json.loads(re.search(r"window\.templateArgs\s*=\s*(\{.*\})", text).group(1))


def write_analysis(historical=False):
    reports = {name: load_report(name) for name, *_ in SCENARIOS}
    totals = {name: next(r for r in report["requests_statistics"] if r["name"] == "Aggregated") for name, report in reports.items()}
    lines = ["# Lab 4 - Phân tích kiểm thử tải Books API", ""]
    if historical:
        lines += ["> Báo cáo A/B/C là số liệu cũ, chưa xác minh code giả lập HTTP 500 hiện tại. Cần chạy lại `python performance/run_lab.py` trước khi nộp.", ""]
    else:
        lines += ["Đo bằng script run_lab.py, mỗi kịch bản dùng database riêng với cùng 50 sách ban đầu.", ""]
    lines += ["## Số liệu", "", "p95 lấy từ dòng Aggregated; đơn vị ms.", "", "| Kịch bản | Users | Spawn/s | Thời gian | Requests | p95 | Failure rate | RPS |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, users, spawn, seconds in SCENARIOS:
        r = totals[name]
        lines.append(f"| {name} | {users} | {spawn} | {seconds}s | {r['num_requests']} | {r['response_time_percentile_0.95']} | {100*r['num_failures']/max(r['num_requests'],1):.2f}% | {r['total_rps']:.2f} |")
    worst = max(totals, key=lambda n: totals[n]['response_time_percentile_0.95'])
    lines += ["", "## 1. Kịch bản có p95 cao nhất", "", f"Kịch bản {worst}: {totals[worst]['response_time_percentile_0.95']} ms. Tải cao có thể làm tăng thời gian chờ CPU, thread, kết nối và tranh chấp ghi SQLite. Đây là giả thuyết từ kiến trúc; cần profiling để xác định nút thắt thực tế.", "", "## 2. Failure rate theo endpoint", "", "| Endpoint | A | B | C |", "|---|---:|---:|---:|"]
    for endpoint in [r['name'] for r in reports['A']['requests_statistics'] if r['name'] != 'Aggregated']:
        values = []
        for name, *_ in SCENARIOS:
            r = next(r for r in reports[name]['requests_statistics'] if r['name'] == endpoint)
            values.append(f"{r['num_failures']}/{r['num_requests']} ({100*r['num_failures']/max(r['num_requests'],1):.2f}%)")
        lines.append(f"| `{endpoint}` | " + " | ".join(values) + " |")
    lines += ["", "Lỗi ghi nhận trong báo cáo:", ""]
    for name, report in reports.items():
        errors = report.get('failures_statistics') or []
        lines.append(f"- {name}: " + ('; '.join(f"{e['name']}: {e['error']} ({e['occurrences']} lần)" for e in errors) or 'Không ghi nhận lỗi.'))
    lines += ["", "Mỗi request tìm theo năm có xác suất 1% yêu cầu server trả HTTP 500 thật khi bật LAB_FAULT_INJECTION. Tỷ lệ quan sát có thể bằng 0 với mẫu nhỏ; không đồng nghĩa toàn workload có 1% lỗi. Tăng user không đổi xác suất này. Status 0 và ConnectionRefusedError là lỗi kết nối, không phải HTTP 500. GET theo ID chấp nhận 404 có chủ đích."]
    if historical:
        lines += ["", "B có 163 search nhưng 0 failure, không khớp cơ chế cứ 100 response đánh dấu lỗi của code cũ. C có lỗi kết nối ở cả bốn endpoint. Chưa đủ bằng chứng kết luận server dừng hay quá tải; báo cáo cũ không xác nhận hành vi code hiện tại."]
    passed = [n for n, r in totals.items() if r['response_time_percentile_0.95'] < 300]
    lines += ["", "## 3. SLO và baseline cho CI gate", "", "Với SLO p95 tổng < 300 ms, kịch bản đạt: " + (', '.join(passed) or 'không có') + ". Nếu SLO áp dụng từng endpoint, phải kiểm tra riêng p95 của mỗi endpoint.", "", "Đề xuất A (10 users, spawn 2/s, 30s) làm baseline ban đầu trên runner cố định, database sạch 50 sách. Gate: p95 tổng < 300 ms và không có lỗi ngoài lỗi giả lập. Chạy riêng lượt không fault injection để kiểm tra 0 lỗi; lượt bật injection dùng kiểm tra quan sát lỗi. Không ép tỷ lệ bằng đúng 1% với mẫu nhỏ. Lặp baseline vài lần trước khi chốt ngưỡng; B/C chạy định kỳ.", "", "Flask development server và SQLite local chỉ đại diện môi trường lab. Wait time 1–3 giây khiến 200 user không đồng nghĩa 200 truy vấn đồng thời. Thời gian HTML có thể dài hơn cấu hình do chờ request kết thúc.", "", "## Bonus: connection pool giới hạn 5", "", "Khi cả 5 connection đều bận, request cần connection thứ sáu phải chờ. p95 có thể tăng, throughput chững lại và có thể xảy ra pool timeout. Không phải cứ 200 user là lập tức lỗi.", "", "Kiểm chứng với QueuePool, pool_size=5, max_overflow=0 và pool_timeout cố định; so sánh C với pool lớn hơn trên cùng dữ liệu và workload. Đo p95, RPS, failures, thời gian chờ checkout và log timeout. Chỉ pool_size=5 chưa giới hạn cứng nếu còn overflow. Code hiện chưa áp dụng giới hạn này; SQLite cũng có tranh chấp ghi riêng.", ""]
    (ROOT / 'performance' / 'analysis.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze-existing", action="store_true")
    args = parser.parse_args()
    if args.analyze_existing:
        write_analysis(historical=True)
        return
    # Check dependencies before touching reports or starting a server.
    subprocess.run([sys.executable, "-c", "from importlib.util import find_spec; "
                    "missing=[m for m in ('locust','flask_sqlalchemy','marshmallow') if find_spec(m) is None]; "
                    "assert not missing, 'Missing dependencies: ' + ', '.join(missing)"], check=True)
    (ROOT / "reports").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="books-lab4-", ignore_cleanup_errors=True) as tmp:
        for name, users, spawn, seconds in SCENARIOS:
            # A fresh OS-assigned port avoids Windows TIME_WAIT between runs.
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            host = f"http://127.0.0.1:{port}"
            database = Path(tmp, f"{name}.db").as_posix()
            server_code = (
                "from app import create_app; from models import Book, db; "
                f"app=create_app({{'SQLALCHEMY_DATABASE_URI': 'sqlite:///{database}', 'LAB_FAULT_INJECTION': True}}); "
                "ctx=app.app_context(); ctx.push(); "
                "db.session.add_all([Book(title=f'Book {i}',author='seed',year=(1996,2017,2021)[i%3]) for i in range(50)]); "
                f"db.session.commit(); ctx.pop(); app.run(host='127.0.0.1',port={port},debug=False)"
            )
            with (ROOT / "reports" / f"{name}-server.log").open("w", encoding="utf-8") as log:
                server = subprocess.Popen([sys.executable, "-c", server_code], cwd=ROOT, stdout=log, stderr=log)
                try:
                    for attempt in range(100):
                        if server.poll() is not None:
                            raise RuntimeError(f"Server {name} exited; inspect server log")
                        try:
                            with urlopen(f"{host}/health", timeout=1) as response:
                                if response.status == 200:
                                    break
                        except OSError:
                            time.sleep(0.1)
                    else:
                        raise RuntimeError("Server did not become ready")
                    print(f"Running {name}: users={users}, spawn={spawn}, duration={seconds}s", flush=True)
                    output = Path(tmp, f"{name}.html")
                    result = subprocess.run([sys.executable, "-m", "locust", "-f", "performance/locustfile.py",
                                             "--headless", "-H", host, "-u", str(users),
                                             "-r", str(spawn), "-t", f"{seconds}s", "--html", str(output)], cwd=ROOT)
                    # Locust uses exit 1 for request failures, including deliberate 500.
                    if result.returncode not in (0, 1):
                        raise RuntimeError(f"Locust exited with {result.returncode}")
                    if not output.exists():
                        raise RuntimeError("Locust did not create a new report")
                    (ROOT / "reports" / f"{name}.html").write_bytes(output.read_bytes())
                    load_report(name)
                finally:
                    if os.name == "nt" and server.poll() is None:
                        # Store Python/venv launchers can own a child interpreter.
                        # Stop only this server's process tree to release SQLite.
                        subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                       check=False)
                    elif server.poll() is None:
                        server.terminate()
                    server.wait(timeout=10)
    write_analysis()
    print("Updated reports/A.html, B.html, C.html and performance/analysis.md")


if __name__ == "__main__":
    main()
