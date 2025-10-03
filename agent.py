import re
from pathlib import Path
from tools import ToolRegistry, ToolResult

# ----- Basit Niyet Tespiti -----
def detect_intent(message: str) -> str:
    msg = message.lower()
    if any(k in msg for k in ["sipariş", "kargo", "teslimat", "order", "tracking"]):
        return "order_status"
    if any(k in msg for k in ["iade", "geri ödeme", "refund", "return"]):
        return "return_policy"
    if any(k in msg for k in ["fiyat", "hesapla", "toplam", "price", "calculate"]):
        return "pricing"
    return "chitchat"

# ----- Basit Argüman Çıkarma -----
def extract_args(intent: str, message: str):
    if intent == "order_status":
        m = re.search(r"\b(\d{6,})\b", message)
        return {"order_id": m.group(1) if m else None}
    if intent == "pricing":
        qty = re.search(r"(\d+)\s*(adet|pcs)?", message.lower())
        price = re.search(r"(\d+[\.,]\d+|\d+)\s*(tl|try|\$|usd)?", message.lower())
        return {
            "quantity": int(qty.group(1)) if qty else 1,
            "unit_price": float(str(price.group(1)).replace(",", ".")) if price else None,
            "currency": price.group(2).upper() if price and price.group(2) else "TRY"
        }
    return {}

class MiniAgent:
    def __init__(self, tools: ToolRegistry):
        self.tools = tools

    def plan(self, message: str):
        intent = detect_intent(message)
        args = extract_args(intent, message)
        tool = None
        if intent == "order_status":
            tool = "check_order_status"
        elif intent == "return_policy":
            tool = "retrieve_return_policy"
        elif intent == "pricing":
            tool = "calc_price"
        return {"intent": intent, "tool": tool, "args": args}

    def act(self, plan):
        if not plan["tool"]:
            return None
        return self.tools.call(plan["tool"], **plan.get("args", {}))

    def respond(self, message: str) -> str:
        plan = self.plan(message)
        observation = self.act(plan)

        if observation is None:
            return "Genel sohbet için sınırlıyım. Sipariş, iade veya fiyat hesaplama hakkında sorabilirsin."
        if observation.error:
            return f"Araç hatası: {observation.error}"

        if plan["intent"] == "order_status":
            status = observation.payload.get("status", "bilinmiyor")
            eta = observation.payload.get("eta", "yok")
            return f"Sipariş durumu: **{status}**. Tahmini teslim: {eta}."
        if plan["intent"] == "return_policy":
            return observation.payload.get("answer", "Politika bulunamadı.")
        if plan["intent"] == "pricing":
            total = observation.payload.get("total")
            currency = observation.payload.get("currency", "TRY")
            breakdown = observation.payload.get("breakdown", "")
            return f"Toplam: {total} {currency}. {breakdown}"
        return "Yanıt üretilemedi."

if __name__ == "__main__":
    registry = ToolRegistry(base_dir=Path(__file__).parent)
    agent = MiniAgent(registry)
    print("Amatis Support Mini-Agent (çıkmak için Ctrl+C)")
    while True:
        try:
            msg = input("\nKullanıcı: ")
            reply = agent.respond(msg)
            print(f"Agent : {reply}")
        except KeyboardInterrupt:
            print("\nGörüşmek üzere!")
            break
