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
"""
from . import helpers as H  # noqa: F401
from .tools import Verdict


def pre_guard(ctx):
    return Verdict.allow()


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")

    # Nhận diện sự kiện LLM 429 fallback sang fail_open
    has_fail_open = any(e.get("type") == "llm_fallback" and e.get("mode") == "fail_open" for e in ctx.events) \
        or action.get("basis") == "fail_open"

    if tool == "issue_refund":
        # Cổng khắc phục S4: Chặn hoàn tiền tự động khi phát hiện fail_open do LLM 429
        if has_fail_open:
            return Verdict.escalate("chặn hoàn tự động khi LLM fallback fail_open do lỗi 429: chuyển người duyệt")

        # Cổng kinh doanh S4: Khống chế trần hoàn tiền tự động ngày sale theo config (daily_refund_cap_vnd)
        cap = (ctx.gates or {}).get("business", {}).get("daily_refund_cap_vnd")
        if cap is not None and not action.get("approval_id"):
            today = ctx.tools.auto_refund_today_vnd()
            if today + action.get("amount_vnd", 0) > cap:
                return Verdict.escalate("vượt trần hoàn tự động ngày sale theo config: chuyển người duyệt")

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

        # Cổng vòng 1: Chặn hoàn tiền khi không đủ điều kiện theo dữ liệu tracking DB
        if ent <= 0 and action.get("amount_vnd", 0) > 0:
            return Verdict.deny("đơn chưa đủ điều kiện hoàn tiền theo dữ liệu tracking DB")

        # Điều chỉnh số tiền nếu vượt quá quyền lợi tính từ DB
        if action.get("amount_vnd", 0) > ent:
            return Verdict.modify("điều chỉnh số tiền hoàn về đúng quyền lợi theo DB", amount_vnd=ent)

    elif tool == "file_carrier_fault":
        # Cổng khắc phục S4: Chặn phạt hãng khi phát hiện sự kiện fail_open do LLM 429
        if has_fail_open:
            return Verdict.deny("chặn phạt hãng khi phát hiện sự kiện fail_open do LLM 429")

        order_id = action.get("order_id")
        order = ctx.tools.lookup_order(order_id)
        if order:
            parcel = next((p for p in order.get("parcels", []) if p["parcel_id"] == action.get("parcel_id")), None) \
                or H.ticket_parcel(order, ctx.ticket, ctx.as_of)
            delay = H.db_delay_days(parcel, ctx.as_of)
            cause = parcel.get("delay_cause")
            pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
            if pol:
                # Cổng khắc phục S4 & Cổng vòng 1: Chặn phạt hãng khi delay_cause == "MERCHANT_HANDOVER" hoặc không do hãng / chưa đủ ngày trễ
                if cause == "MERCHANT_HANDOVER":
                    return Verdict.deny("chặn phạt hãng vì nguyên nhân do shop bàn giao trễ (MERCHANT_HANDOVER)")
                if not H.carrier_at_fault(pol, parcel, delay):
                    return Verdict.deny("không đủ điều kiện ghi lỗi hãng vận chuyển theo tracking DB")
                if action.get("delay_days", 0) != delay:
                    return Verdict.modify("sửa số ngày trễ phạt hãng về đúng số ngày trễ trên DB", delay_days=delay)

    elif tool == "notify_carrier":
        # Cổng vòng 1: Bảo vệ dữ liệu cá nhân PII khi gửi thông báo cho bên thứ ba
        payload = action.get("payload", {})
        if "customer_note" in payload:
            cleaned = {k: v for k, v in payload.items() if k != "customer_note"}
            return Verdict.modify("loại bỏ ghi chú khách hàng để tránh rò rỉ dữ liệu cá nhân PII", payload=cleaned)

    return Verdict.allow()
