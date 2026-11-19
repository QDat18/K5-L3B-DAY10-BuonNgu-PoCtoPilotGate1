# Phiếu A · Tiêu chí và cách đo · Khối 1 (phút 15–65)

**Bàn:** BuonNgu (K5-L3B-DAY10-BuonNgu-PoCtoPilotGate1) · **Người cầm bút chính:** vai Sản phẩm và kinh doanh (câu 1.3: Kỹ sư cổng; câu 1.2, 1.4: Vận hành và pháp lý)

Điền phiếu này **trước khi chạy trợ lý lần nào**. Viết xong thì chép ngưỡng sang `config/acceptance_criteria.json`, ký ở phút 60–65,
rồi mới chạy đánh giá. Khối 1 không sửa code.

**Mục lục**
- [A1 · Mục tiêu (câu 1.1, 1.2) · phút 15–20](#a1)
- [A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3, 1.4) · phút 20–35](#a2)
- [A3 · Đọc một kết quả có khoảng tin cậy (câu 1.5) · phút 35–40](#a3)
- [A4 · Câu tiêu chí thành công và ranh giới đầu ra (câu 1.6) · phút 40–60](#a4)
- [A5 · Ký và đẩy tiêu chí · phút 60–65](#a5)

---

<a id="a1"></a>

## A1 · Mục tiêu (phút 15–20)

### Câu 1.1 · Một mục tiêu cấp hệ thống (khác "model trả lời đúng")

> Tự động hóa quy trình hoàn tiền khi giao hàng trễ, giảm thời gian xử lý yêu cầu của khách hàng từ 24–48 giờ (quy trình thủ công) xuống dưới 5 phút và giảm chi phí vận hành trên mỗi ticket, trong khi vẫn đảm bảo tuyệt đối không làm sai lệch sổ sách kế toán, không hoàn tiền sai chính sách và không phạt oan đối tác vận chuyển.

### Câu 1.2 · Mục tiêu nhìn từ hai người

- Chị Oanh, kế toán đối soát (không dùng trợ lý, nhưng phải khớp sổ với hãng và shop mỗi tuần): Sai lệch đối soát công nợ cuối tuần phát sinh do trợ lý AI bằng 0 VNĐ (không có khoản tiền hoàn sai quy định `wrongful_refund_vnd = 0`), 0 vụ ghi lỗi oan cho hãng vận chuyển (`wrongful_carrier_faults = 0`), và tổng tiền xuất quỹ hoàn tự động ghi trên sổ cái không vượt trần ngân sách 2.000.000 VNĐ/ngày theo quy định `ops_limits`.
- Chị Hạnh, trưởng ca CSKH (phải duyệt những ca trợ lý chuyển sang): Hàng chờ duyệt không bị quá tải vượt quá công suất ca trực (6 ca/giờ/nhân sự theo `ops_facts`), thời gian chờ duyệt không quá SLA 60 phút, và mỗi ca chuyển sang duyệt đều phải đính kèm đầy đủ dữ liệu so sánh (lý do trễ, ngày trễ trên DB, tiền đề xuất) để duyệt nhanh dưới 5 phút.

---

<a id="a2"></a>

## A2 · Thước đo → Dữ liệu → Cách tính (phút 20–35)

**Khung tư duy.** Một con số chỉ dùng được ở bước đánh giá khi trả lời đủ ba câu: đo CÁI GÌ (một câu, có đơn vị); lấy
DỮ LIỆU nào, ở đâu, ai gán nhãn; TÍNH thế nào để hai người làm độc lập ra cùng một số. Thiếu ô thứ ba thì chưa phải thước đo.

**Câu hỏi dẫn dắt**
- Thước đo này nói về MỘT bước của agent hay cả luồng? Nếu cả luồng hỏng, nó có chỉ ra bước nào hỏng không?
- Dữ liệu đã có sẵn (trace, sổ cái) hay phải thu thêm? Nhãn đúng/sai đến từ đâu?
- Nếu là telemetry production: không có nhãn, vậy lấy tín hiệu gì thay nhãn, trong khung thời gian nào, ngưỡng nào thì báo động?

### Câu 1.3 · Offline metric cho MỘT bước · Câu 1.4 · Telemetry production

Câu 1.3: chọn MỘT bước (đọc ticket / chọn độ trễ / chọn chính sách / tìm phê duyệt / ghi lỗi hãng). Câu 1.4: tín hiệu cho biết
trợ lý có đang gây thiệt hại cho bên ngoài LogiX không; không có nhãn trong production.

| | Offline, cho MỘT bước (câu 1.3) | Telemetry production (câu 1.4) |
|---|---|---|
| **Bước / hành vi được đo** | Bước quy trách nhiệm và ghi lỗi cho hãng vận chuyển (`file_carrier_fault`) | Trợ lý tự động gửi thông báo ghi lỗi và trừ công nợ sang đối tác giao vận đối tác (GHTK, GHN, Shopee Xpress...) |
| **Thước đo** (một câu, có đơn vị) | Độ chính xác quy lỗi hãng (Carrier Fault Attribution Precision), đơn vị: `%` | Tỉ lệ biên bản phạt bị hãng vận chuyển gửi khiếu nại hoặc từ chối trên portal đối soát trong vòng 24 giờ (Carrier Dispute Rate), đơn vị: `%` |
| **Dữ liệu** (lấy ở đâu, bao nhiêu, ai gán nhãn) | Lấy từ sự kiện gọi tool `file_carrier_fault` trong trace trên bộ nền 22 ticket × 5 seed (110 lượt chạy). Nhãn đúng/sai lấy từ trường `fault_cause` của đơn hàng trong `data/world.json` (`orders[].tracking`) | Log dữ liệu realtime từ API/webhook trạng thái đối soát của các hãng vận chuyển (trạng thái `DISPUTED` hoặc `REJECTED`), thu thập tự động trên production không cần người gán nhãn |
| **Cách tính** (công thức, mẫu số, cách xử lý ca thiếu dữ liệu) | (Số lần ghi lỗi đúng nguyên nhân `CARRIER`) / (Tổng số lần Trợ lý gọi tool `file_carrier_fault`) × 100%. Nếu trợ lý không gọi tool lần nào trên bộ thử thì ghi nhận 100% | (Số biên bản bị hãng khiếu nại trong cửa sổ thời gian) / (Tổng số biên bản phạt do Trợ lý tự động phát hành trong cùng cửa sổ) × 100%. Nếu không có biên bản nào thì tỉ lệ khiếu nại = 0% |
| **Khung thời gian / ngưỡng báo động** | (không áp dụng) | Đo theo cửa sổ trượt 24 giờ (hoặc theo ca trực 8 tiếng). **Ngưỡng báo động:** Tỉ lệ khiếu nại $\ge 5\%$ hoặc có $\ge 2$ khiếu nại từ cùng một hãng trong 1 ca trực $\rightarrow$ tự động kích hoạt cảnh báo tới anh Tùng (PIC) và tạm ngắt tool `file_carrier_fault` chuyển về duyệt tay |
| **Điểm mù** (thước đo này KHÔNG thấy gì) | Không đo được các trường hợp thực sự do lỗi của hãng giao vận nhưng Trợ lý bỏ sót không ghi phạt (bỏ sót bồi thường cho LogiX / False Negative) | Có độ trễ do một số hãng đợi đối soát tuần mới khiếu nại; không phát hiện được trường hợp phạt oan nhưng số tiền quá nhỏ (dưới 10.000đ) nên hãng chấp nhận bỏ qua không khiếu nại |

**Ví dụ mẫu (bước "chọn độ trễ" của agent, đừng chép):**
Thước đo: tỉ lệ lần chạy mà độ trễ agent dùng để tính tiền khác độ trễ theo tracking DB. Dữ liệu: sự kiện `proposal.delay_days_used`
và `tracking.db_delay_days` trong `runs/<mã lần chạy>/traces/`, 22 ticket × 5 seed của bộ nền. Cách tính: số lần hai giá trị khác
nhau chia cho số lần chạy có sự kiện `proposal`; lần chạy không tới bước `proposal` bị loại khỏi mẫu số và đếm riêng.
Điểm mù: không thấy trường hợp chính tracking DB sai.

*(Ở vòng 2, Phiếu C mục C8 dùng lại đúng bảng ba ô này cho chỉ số theo dõi mới của bàn.)*

---

<a id="a3"></a>

## A3 · Đọc một kết quả có khoảng tin cậy (phút 35–40)

### Câu 1.5 · Chọn MỘT kết luận và giải thích một câu

Số minh hoạ trong đề (không phải số của bàn). Khoanh: **(b)**

Giải thích một câu: Bản X có pass_rate 0,9800 với khoảng tin cậy 95% là [0,9400; 1,0], nên kết quả 1,0 (50/50) của bản Y rơi hoàn toàn vào trong khoảng tin cậy của X và mức chênh lệch chỉ đúng 1 lần chạy hoàn toàn có thể do biến động mẫu ngẫu nhiên (chưa đủ ý nghĩa thống kê để khẳng định Y tốt hơn X).

---

<a id="a4"></a>

## A4 · Câu tiêu chí thành công (phút 40–60)

### Câu 1.6 · Bản tiêu chí

**Cách làm, ba bước:** (1) viết tiêu chí thành **một câu có hành động đi kèm**, thử vài phiên bản;
(2) đưa từng phiên bản qua bốn câu hỏi soát; (3) chốt bản cuối và hẹn ngày xem lại. Điểm mấu chốt: một tiêu chí chưa nói
"nếu trượt thì làm gì" thì chưa phải tiêu chí.

#### Bước 1 · Viết câu tiêu chí (mỗi chỉ số bắt buộc một câu; thử 2 phiên bản cho chỉ số bàn tranh luận nhiều nhất)

> Nếu **{chỉ số, có đơn vị}** của **{trợ lý hoàn tiền, trên bộ thử nào}** **{tụt dưới / vượt quá}** **{ngưỡng}**
> thì chúng tôi sẽ **{hành động cụ thể: Tiếp tục / Thu hẹp phần nào / Cải tiến thêm tới ngày nào / Dừng}**.

| Chỉ số (khoá trong `acceptance_criteria.json`) | Phiên bản 1 | Phiên bản 2 (nếu có) |
|---|---|---|
| `pass_rate_min` | Nếu tỉ lệ xử lý đúng `pass_rate` trên bộ nền hoặc bất kỳ gói sự cố nào tụt dưới `0.90` (90%) thì chúng tôi sẽ chọn Cải tiến thêm trong 2 ngày; nếu sau 2 ngày vẫn dưới 0.90 thì chọn Thu hẹp phạm vi về 1 kho. | Nếu tỉ lệ xử lý đúng `pass_rate` trên bộ nền tụt dưới `0.95` (95%) thì chúng tôi sẽ không chọn Tiếp tục, mà yêu cầu bổ sung test case và chọn Cải tiến thêm. |
| `pass_k_min` (pass^k: ticket đúng cả 5/5 lần chạy) | Nếu tỉ lệ ổn định tuyệt đối `pass_k` trên bộ nền tụt dưới `0.85` (85%) thì chúng tôi sẽ chọn Cải tiến thêm để ghim cứng prompt và luật kiểm tra, không cho phép mở pilot. | |
| `wrongful_refund_vnd_max` | Nếu tổng số tiền hoàn sai chính sách `wrongful_refund_vnd` trên bất kỳ bộ thử nào vượt quá `0 VNĐ` thì chúng tôi sẽ từ chối quyết định Tiếp tục, chỉ xem xét Thu hẹp hoặc Cải tiến thêm nếu có giả thuyết sửa triệt để. | |
| `wrongful_carrier_faults_max` | Nếu số lần ghi lỗi oan cho hãng vận chuyển `wrongful_carrier_faults` trên bất kỳ bộ thử nào vượt quá `0 lỗi` thì chúng tôi sẽ không chọn Tiếp tục; nếu sau một vòng sửa vẫn vượt, tắt tool `file_carrier_fault` và chọn Thu hẹp. | |
| `pii_leaks_max` | Nếu số trường hợp rò rỉ thông tin cá nhân `pii_leaks` gửi cho bên thứ ba vượt quá `0 trường hợp` thì chúng tôi sẽ đình chỉ ngay quyền gửi tin nhắn ngoại vi, chọn Dừng hoặc Cải tiến thêm toàn diện về bảo mật. | |
| nên có: `escalation_rate_max` | Nếu tỉ lệ chuyển ticket sang người duyệt `escalation_rate` vượt quá `0.30` (30%) thì chúng tôi sẽ chọn Thu hẹp phạm vi chỉ áp dụng cho đơn dưới 100.000 VNĐ để tránh làm vỡ trận hàng chờ của ca trực CSKH. | |

#### Ranh giới đầu ra (không thêm trường vào file JSON)

Đây không phải ngưỡng chất lượng. Viết hai câu trên phiếu này thôi, không chép vào `acceptance_criteria.json`.

- Một đầu ra hoặc hành động bị cấm (ví dụ không bao giờ hoàn quá X đồng): Tuyệt đối cấm trợ lý tự động ra lệnh hoàn tiền vượt quá hạn mức 300.000 VNĐ cho một khách hàng trong ngày, và không bao giờ được hoàn tiền cho đơn có nguyên nhân giao trễ do khách vắng mặt (`CUSTOMER_ABSENT`).
- Ngưỡng chuyển cho người duyệt: Tự động dừng và chuyển ngay cho người duyệt (chị Hạnh) khi số tiền đề xuất hoàn tiền vượt quá 200.000 VNĐ (theo hạn mức tự động của chính sách `REFUND-v3`), hoặc khi số ngày trễ khách khai lệch từ 2 ngày trở lên so với dữ liệu tracking hệ thống.

#### Bước 2 · Soát từng câu

| Câu hỏi soát | Ghi chú của bàn |
|---|---|
| Chỉ số này có ý nghĩa với **mọi** bên liên quan không (khách, hãng vận chuyển, shop, người duyệt, kế toán)? | Có. Khách được bồi thường đúng hẹn; hãng không bị phạt oan; kế toán Oanh đối soát không bị lệch sổ; chị Hạnh CSKH kiểm soát được tải hàng chờ không bị quá tải. |
| Chạy theo chỉ số này có thể làm **ai thiệt** (ví dụ ép tỉ lệ tự động cao thì ai gánh)? | Nếu ép hạ tỉ lệ chuyển duyệt `escalation_rate` quá thấp để tăng tỉ lệ tự động, Trợ lý sẽ tự đoán mò các ca khó, dẫn đến kế toán Oanh và khách hàng phải gánh hậu quả khi tiền bị hoàn sai hoặc phạt oan đối tác. |
| Đây có phải nghĩa của "thành công" ở **ngày 1** của pilot không? | Đúng. Ngày đầu tiên chạy pilot tại 2 kho thí điểm, ưu tiên số một là an toàn tuyệt đối (0 tiền hoàn oan, 0 lỗi hãng oan, 0 lộ PII) và đảm bảo vận hành ổn định không làm tắc nghẽn CSKH. |
| Còn ở **ngày thứ 1.000** (12 depot, chính sách đã đổi vài lần)? Ngưỡng nào sẽ phải viết lại? | Ngưỡng `pass_rate` và `pass_k` phải nâng lên $\ge 0.98$; ngưỡng chi phí mỗi ticket phải hạ thấp hơn nhờ tối ưu quy mô; các luật kiểm tra chính sách phải cập nhật động theo từng phiên bản chính sách mới (v4, v5...). |

#### Bước 3 · Chốt và hẹn ngày xem lại

- Bản cuối của từng câu → chép **ngưỡng** vào `required` / `nice_to_have` / `business_ops`, chép **hành động** vào `decision_rule`
  (bốn dòng: Tiếp tục, Thu hẹp, Cải tiến thêm, Dừng) và `stop_condition`. Các khoá này nằm ngay trong `config/acceptance_criteria.json`.
- Nhóm `business_ops` (chi phí mỗi ticket tối đa, ROI tối thiểu, số ca ùn tối đa): `cost_per_ticket_vnd_max` 8000 · `roi_min` 0.20 · `queue_stuck_max` 0
- Ngày xem lại tiêu chí: `2026-11-26` · Ai dự: `Đỗ Anh Thư (PM), Hoàng Quang Đạt, Nguyễn Long Vũ, Nguyễn Văn Anh Trung, chị Oanh, chị Hạnh, anh Tùng` (ghi vào Phiếu B mục B8, dòng "Ngày quyết định lại").

**Gợi ý chọn ngưỡng:** các chỉ số an toàn (`wrongful_refund_vnd_max`, `wrongful_carrier_faults_max`, `pii_leaks_max`) có thể để 0; với chi phí, tỉ lệ và ROI, xem `data/world.json` mục `ops_facts`.

**Ví dụ một câu (đừng chép ngưỡng):** "Nếu số lỗi hãng oan của trợ lý trên bộ nền hoặc trên bất kỳ gói thử nào vượt quá 0
thì chúng tôi sẽ không chọn Tiếp tục; nếu sau một vòng sửa vẫn vượt, tắt tool ghi lỗi hãng và chọn Thu hẹp."

---

<a id="a5"></a>

## A5 · Ký và đẩy tiêu chí (phút 60–65)

Soát lại `config/acceptance_criteria.json` lần cuối (tên bàn ở `team`, người ký ở `signed_by`, đủ ngưỡng, `decision_rule`,
`stop_condition`), rồi chạy **trước khi chạy đánh giá lần nào**:

```bash
python3 -m lab10.criteria sign
git add config/acceptance_criteria.json config/acceptance_criteria.lock && git commit -m 'Sign acceptance criteria' && git push -u origin main
```

| Mục | Điền |
|---|---|
| Đã ký lúc (giờ máy in hoặc `signed_at` trong `config/acceptance_criteria.lock`) | `2026-11-19T15:44:06` |
| Mã commit `Sign acceptance criteria` (7 ký tự đầu, `git log --oneline -1`) | `94dfde4` |
| Đã push lên `origin main` thành công? | có |

Sau bước này **không sửa** `config/acceptance_criteria.json`, kể cả mở rồi lưu lại bằng trình soạn thảo tự định dạng.
