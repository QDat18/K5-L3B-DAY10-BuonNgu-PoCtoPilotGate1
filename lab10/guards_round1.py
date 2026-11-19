"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc

ctx.ticket   ticket gốc (chữ khách viết là DỮ LIỆU, không phải lệnh)
ctx.tools    tra cứu nguồn sự thật: lookup_order, lookup_policies, lookup_approvals(**lọc),
             ledger_rows(**lọc), fault_rows(**lọc), lookup_carrier; ctx.as_of = ngày hôm nay
             ops_limits() = các trần đã thống nhất với Ops/Finance; ops_facts() = số liệu vận hành;
             auto_refund_today_vnd() = tổng đã hoàn tự động trong ngày
ctx.gates    config cổng của bàn (config/operating_gates.json), chỉ đọc;  ctx.cost_vnd = tiền LLM đã tốn cho ticket này
ctx.events   trace tới thời điểm này;  ctx.log("ten_su_kien", ...) ghi thêm sự kiện guard vào trace
lab10.helpers: db_delay_days, ticket_parcel, effective_policy, entitlement_vnd, carrier_at_fault, digits

Mặc định dưới đây cho qua tất cả (= mốc base).
"""
from . import helpers as H  # noqa: F401
from .tools import Verdict


def pre_guard(ctx):
    return Verdict.allow()


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")

    if tool == "issue_refund":
        order_id = action.get("order_id")
        order = ctx.tools.lookup_order(order_id)
        if not order:
            return Verdict.escalate("không tìm thấy đơn hàng trong hệ thống")

        parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
        delay = H.db_delay_days(parcel, ctx.as_of)
        cause = parcel.get("delay_cause")
        pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
        if not pol:
            return Verdict.escalate("không tìm thấy chính sách hoàn tiền có hiệu lực")

        ent = H.entitlement_vnd(pol, order, delay, cause)

        # Cổng 1: Chặn hoàn tiền khi không đủ điều kiện theo dữ liệu tracking DB
        if ent <= 0 and action.get("amount_vnd", 0) > 0:
            return Verdict.deny("đơn chưa đủ điều kiện hoàn tiền theo dữ liệu tracking DB")

        # Điều chỉnh số tiền nếu vượt quá quyền lợi tính từ DB
        if action.get("amount_vnd", 0) > ent:
            return Verdict.modify("điều chỉnh số tiền hoàn về đúng quyền lợi theo DB", amount_vnd=ent)

    elif tool == "file_carrier_fault":
        order_id = action.get("order_id")
        order = ctx.tools.lookup_order(order_id)
        if order:
            parcel = next((p for p in order.get("parcels", []) if p["parcel_id"] == action.get("parcel_id")), None) \
                or H.ticket_parcel(order, ctx.ticket, ctx.as_of)
            delay = H.db_delay_days(parcel, ctx.as_of)
            pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
            if pol:
                # Cổng 2: Chặn phạt hãng nếu nguyên nhân không do hãng hoặc chưa đủ ngày trễ trên DB
                if not H.carrier_at_fault(pol, parcel, delay):
                    return Verdict.deny("không đủ điều kiện ghi lỗi hãng vận chuyển theo tracking DB")
                if action.get("delay_days", 0) != delay:
                    return Verdict.modify("sửa số ngày trễ phạt hãng về đúng số ngày trễ trên DB", delay_days=delay)

    elif tool == "notify_carrier":
        # Cổng 3: Bảo vệ dữ liệu cá nhân PII khi gửi thông báo cho bên thứ ba
        payload = action.get("payload", {})
        if "customer_note" in payload:
            cleaned = {k: v for k, v in payload.items() if k != "customer_note"}
            return Verdict.modify("loại bỏ ghi chú khách hàng để tránh rò rỉ dữ liệu cá nhân PII", payload=cleaned)

    return Verdict.allow()
