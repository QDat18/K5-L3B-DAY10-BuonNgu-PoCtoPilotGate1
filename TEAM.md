# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): BuonNgu
- Lớp: `L3B`
- Repo của bàn: `K5-L3B-DAY10-BuonNgu-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): S4

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; bàn 3 người thì để trống dòng 4. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Đỗ Anh Thư | 2A202603815 | Sản phẩm và kinh doanh | x |
|   2 | Hoàng Quang Đạt | 2A202603808 | Kỹ sư cổng | |
|   3 | Nguyễn Long Vũ | 2A202603842 | Kỹ sư cổng | |
|   4 | Nguyễn Văn Anh Trung | 2A202603903 | Vận hành và pháp lý | |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## DoAnhThu-2A202603815

### Phần việc phụ trách

Trưởng nhóm · Sản phẩm và kinh doanh:

### Đóng góp cụ thể

- Phiếu A: Mục A1 (câu 1.1), Mục A3 (câu 1.5), Mục A4 (câu 1.6: bản tiêu chí, ranh giới đầu ra).
- Phiếu B: Mục B3 (câu 2.3 bản đồ dữ liệu và drift), Mục B7.4 (câu 2.9 cổng kinh doanh), Mục B8 (quyết định v1).
- Phiếu C: Mục C5 (câu 3.2 specification), Mục C7 (sửa cổng business), Mục C12 (quyết định v2 và 3 dòng bắt buộc).

### Bằng chứng

- File: `config/acceptance_criteria.json`, `config/operating_gates.json` (mục `business`).

### Exit ticket

Một điều học được, một điều còn chưa chắc.

---

## HoangQuangDat-2A202603808

### Phần việc phụ trách

Kỹ sư cổng:

### Đóng góp cụ thể

- Phiếu A: Mục A2 (câu 1.3 offline metric).
- Phiếu B: Mục B1 (câu 2.1 mốc base), Mục B2 (câu 2.2 trace T-002@55), Mục B7.1 (câu 2.6 code guards), Mục B7.2 (câu 2.7 tránh rò rỉ dữ liệu).
- Phiếu C: Mục C2 (câu 3.1 trace sự cố), Mục C7 (câu 3.5 sửa code guards), Mục C8 (câu 3.6 monitor mới).

### Bằng chứng

- File: `lab10/guards.py`, `lab10/monitors.py`.

### Exit ticket

Một điều học được, một điều còn chưa chắc.

---

## NguyenLongVu-2A202603842

### Phần việc phụ trách

Kỹ sư cổng:

### Đóng góp cụ thể

- Phiếu B: Mục B1 (chạy eval & gate), Mục B7.1 (kiểm tra test và độ phủ), Mục B7.3 (câu 2.8 behavioral test, 2 ticket hiểm).
- Phiếu C: Mục C1 (câu 3.0 đo mốc prepared), Mục C7 (kiểm tra regression), Mục C8 (kiểm tra monitor bắt sự cố).

### Bằng chứng

- File: `lab10/guards.py`, `lab10/monitors.py`, chạy các lệnh CLI kiểm thử.

### Exit ticket

Một điều học được, một điều còn chưa chắc.

---

## NguyenVanAnhTrung-2A202603903

### Phần việc phụ trách

Vận hành và pháp lý:

### Đóng góp cụ thể

- Phiếu A: Mục A1 (câu 1.2 mục tiêu Oanh & Hạnh), Mục A2 (câu 1.4 telemetry production).
- Phiếu B: Mục B4 (câu 2.4 HAZOP mở rộng), Mục B5 (checklist 9 nhóm việc có PIC), Mục B7.5 (câu 2.10 runbook 1–3), Mục B7.6 (giờ cao điểm).
- Phiếu C: Mục C3 (phần riêng theo thẻ), Mục C4 (HAZOP của thẻ), Mục C5 (câu 3.3 giả định môi trường), Mục C9 (fault tree sau sửa), Mục C10 (risk register), Mục C11 (cập nhật checklist và runbook 4–5).

### Bằng chứng

- File: `config/operating_gates.json` (mục `operations` và `legal`), `submission/submission.json`.

### Exit ticket

Một điều học được: Học được cách đặt ra mục tiêu
Một điều còn chưa chắc: Cách lựa chọn ngưỡng mục tiêu phù hợp từng bài toán
