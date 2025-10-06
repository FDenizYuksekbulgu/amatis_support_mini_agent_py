from dataclasses import dataclass
from pathlib import Path
import json

# -------------------------------
# Basit sonuç nesnesi
# -------------------------------
@dataclass
class ToolResult:
    payload: dict | None = None   # başarılı sonuçlar buraya
    error: str | None = None      # hata varsa metin olarak buraya

# -------------------------------
# Araç (tool) kayıt ve çağrı sistemi
# -------------------------------
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
            # Geliştirme sırasında hatayı görmek için:
            return ToolResult(error=str(e))

    # ---------------------------
    # Tool 1: Sipariş Durumu
    # ---------------------------
    def check_order_status(self, order_id: str | None = None) -> ToolResult:
        if not order_id:
            return ToolResult(error="order_id gerekli (örn: 'Sipariş 1234567 nerede?').")

        orders_path = self.base_dir / "data" / "orders.json"
        if not orders_path.exists():
            return ToolResult(error="orders.json bulunamadı. 'data/orders.json' dosyasını kontrol et.")

        data = json.loads(orders_path.read_text(encoding="utf-8"))
        order = next((o for o in data if str(o.get("order_id")) == str(order_id)), None)
        if not order:
            return ToolResult(error=f"{order_id} için kayıt bulunamadı.")
        return ToolResult(payload={
            "status": order.get("status", "bilinmiyor"),
            "eta": order.get("eta", "bilinmiyor"),
        })

    # ---------------------------
    # Tool 2: İade Politikası
    # ---------------------------
    def retrieve_return_policy(self) -> ToolResult:
        md_path = self.base_dir / "kb" / "return_policy.md"
        if not md_path.exists():
            return ToolResult(error="return_policy.md bulunamadı. 'kb/return_policy.md' dosyasını oluştur.")
        text = md_path.read_text(encoding="utf-8")

        # Markdown karakterlerini temizle ve sadeleştir
        clean_text = (
            text.replace("#", "")
                .replace("-", "")
                .replace("\\", "")
                .replace("\n", " ")
                .strip()
        )

        # payload/error sözleşmesine uygun dön
        return ToolResult(payload={"answer": clean_text})

    # ---------------------------
    # Tool 3: Fiyat Hesaplama
    # ---------------------------
    def calc_price(self, quantity: int = 1, unit_price: float | None = None, currency: str = "TRY") -> ToolResult:
        if unit_price is None:
            return ToolResult(error="Birim fiyat bulunamadı (örn: '3 adet 129.90 TL').")

        if isinstance(quantity, str) and quantity.isdigit():
            quantity = int(quantity)
        if quantity <= 0:
            return ToolResult(error="Adet 1 veya daha büyük olmalı.")
        if unit_price < 0:
            return ToolResult(error="Birim fiyat negatif olamaz.")

        subtotal = round(quantity * unit_price, 2)
        tax_rate = 0.10  # %10 KDV varsayımı
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax, 2)
        breakdown = f"(adet:{quantity} × {unit_price} = {subtotal} + KDV %10 → {tax})"
        return ToolResult(payload={
            "total": total,
            "currency": currency,
            "breakdown": breakdown
        })
