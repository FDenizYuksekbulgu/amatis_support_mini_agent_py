from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class ToolResult:
    payload: dict | None = None
    error: str | None = None

class ToolRegistry:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tools = {
            "check_order_status": self.check_order_status,
            "retrieve_return_policy": self.retrieve_return_policy,
            "calc_price": self.calc_price,
        }

    def call(self, name: str, **kwargs) -> ToolResult:
        fn = self.tools.get(name)
        if not fn:
            return ToolResult(error=f"Bilinmeyen tool: {name}")
        try:
            return fn(**kwargs)
        except Exception as e:
            return ToolResult(error=str(e))

    # ---- Tools ----
    def check_order_status(self, order_id: str | None = None) -> ToolResult:
        if not order_id:
            return ToolResult(error="order_id gerekli (örn: 'Sipariş 1234567 nerede?').")
        orders_path = self.base_dir / "data" / "orders.json"
        data = json.loads(orders_path.read_text(encoding="utf-8"))
        order = next((o for o in data if str(o.get("order_id")) == str(order_id)), None)
        if not order:
            return ToolResult(error=f"{order_id} için kayıt bulunamadı.")
        return ToolResult(payload={"status": order["status"], "eta": order.get("eta", "bilinmiyor")})

    def retrieve_return_policy(self) -> ToolResult:
        md_path = self.base_dir / "kb" / "return_policy.md"
        text = md_path.read_text(encoding="utf-8")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        answer = "\n".join(lines[:12])
        return ToolResult(payload={"answer": answer})

    def calc_price(self, quantity: int = 1, unit_price: float | None = None, currency: str = "TRY") -> ToolResult:
        if unit_price is None:
            return ToolResult(error="Birim fiyat bulunamadı (örn: '3 adet 129.90 TL').")
        subtotal = quantity * unit_price
        tax = round(subtotal * 0.10, 2)   # %10 KDV varsayımı
        total = round(subtotal + tax, 2)
        breakdown = f"(adet:{quantity} × {unit_price} = {subtotal} + KDV %10 → {tax})"
        return ToolResult(payload={"total": total, "currency": currency, "breakdown": breakdown})
