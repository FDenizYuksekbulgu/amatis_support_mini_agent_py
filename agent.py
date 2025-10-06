import re
import os
from pathlib import Path
from tools import ToolRegistry, ToolResult

# --------- Gemini entegrasyonu ----------
import google.generativeai as genai

def _init_gemini():
    key = (os.environ.get("GEMINI_API_KEY") or "").strip().strip('"').strip("'")
    print("[DEBUG] API KEY FOUND:", bool(key))
    if not key:
        print("[DEBUG] No GEMINI_API_KEY")
        return None
    genai.configure(api_key=key)

    try:
        # generateContent destekleyen modelleri al
        models = [m for m in genai.list_models()
                  if "generateContent" in getattr(m, "supported_generation_methods", [])]
        if not models:
            print("[DEBUG] No model supports generateContent")
            return None

        # Tercih: flash -> pro; listeden gelen ADI olduğu gibi kullan (models/...")
        def score(m):
            n = m.name.lower()
            return (0 if "flash" in n else 1, n)  # flash önce
        models.sort(key=score)

        chosen = models[0].name  # ör: "models/gemini-1.5-flash"
        print(f"[DEBUG] Using model: {chosen}")
        return genai.GenerativeModel(chosen)
    except Exception as e:
        print(f"[DEBUG] Model discovery failed: {e}")
        return None

_GEMINI = _init_gemini()
ALLOWED_INTENTS = {"order_status", "return_policy", "pricing", "chitchat"}


# --------- LLM ile intent ----------
def classify_intent_gemini(message: str) -> str | None:
    if _GEMINI is None:
        return None
    prompt = f"""
You are an intent classifier. Reply with EXACTLY ONE label from:
order_status, return_policy, pricing, chitchat
No punctuation, no explanation.

User message:
{message}
""".strip()
    try:
        resp = _GEMINI.generate_content(prompt)
        label = (resp.text or "").strip().lower()
        return label if label in ALLOWED_INTENTS else None
    except Exception as e:
        print(f"[DEBUG] intent LLM error: {e}")
        return None


def detect_intent(message: str) -> str:
    llm_label = classify_intent_gemini(message)
    if llm_label in ALLOWED_INTENTS:
        return llm_label

    msg = message.lower()
    if any(k in msg for k in ["sipariş", "kargo", "teslimat", "order", "tracking"]):
        return "order_status"
    if any(k in msg for k in ["iade", "geri ödeme", "geri odeme", "refund", "return", "değişim", "degisim"]):
        return "return_policy"
    if any(k in msg for k in ["fiyat", "hesapla", "toplam", "price", "calculate"]):
        return "pricing"
    return "chitchat"


# --------- Argüman çıkarma ----------
def extract_args(intent: str, message: str):
    if intent == "order_status":
        m = re.search(r"\b(\d{6,})\b", message)
        return {"order_id": m.group(1) if m else None}
    if intent == "pricing":
        lower = message.lower()
        qty = re.search(r"(\d+)\s*(adet|pcs)?", lower)
        price = re.search(r"(\d+[\.,]\d+|\d+)\s*(tl|try|\$|usd|eur|€)?", lower)
        return {
            "quantity": int(qty.group(1)) if qty else 1,
            "unit_price": float(str(price.group(1)).replace(",", ".")) if price else None,
            "currency": (price.group(2) or "TRY").upper() if price else "TRY",
        }
    return {}


# --------- LLM ile yanıt biçimlendirme ----------
def render_with_gemini(intent: str, user_message: str, tool_payload: dict) -> str | None:
    if _GEMINI is None:
        return None
    system_hint = (
        "You are a helpful Turkish customer support AI. "
        "Keep answers short, clear and friendly. No markdown."
    )
    content = f"""
KULLANICI:
{user_message}

INTENT:
{intent}

TOOL_CIKTISI_JSON:
{tool_payload}

GOREV:
- Türkçe tek paragraf, kısa ve net cevap yaz.
- order_status ise: durum ve ETA'yı birleştir.
- return_policy ise: özeti tek cümle/tek paragraf ver.
- pricing ise: toplam ve para birimini net yaz.
""".strip()
    try:
        resp = _GEMINI.generate_content([{"role": "user", "parts": [system_hint + "\n\n" + content]}])
        return (resp.text or "").strip()
    except Exception as e:
        print(f"[DEBUG] render LLM error: {e}")
        return None


# --------- Mini Agent ----------
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
        print(f"[DEBUG] intent={plan['intent']} tool={plan['tool']} args={plan['args']}")
        observation: ToolResult | None = self.act(plan)

        # Genel sohbet: LLM yanıtlasın
        if observation is None:
            if _GEMINI:
                try:
                    print("[DEBUG] chitchat via LLM")
                    resp = _GEMINI.generate_content(message)
                    return (resp.text or "").strip()
                except Exception as e:
                    print(f"[DEBUG] LLM ERROR: {e}")
            return "Genel sohbet için sınırlıyım. Sipariş, iade veya fiyat hesaplama hakkında sorabilirsin."

        if observation.error:
            return f"Araç hatası: {observation.error}"

        # Tool çıktısını LLM ile parlat; olmazsa sabit metne düş
        if plan["intent"] == "order_status":
            llm = render_with_gemini(plan["intent"], message, observation.payload or {})
            if llm:
                return llm
            status = observation.payload.get("status", "bilinmiyor")
            eta = observation.payload.get("eta", "yok")
            return f"Sipariş durumu: {status}. Tahmini teslim: {eta}."

        if plan["intent"] == "return_policy":
            llm = render_with_gemini(plan["intent"], message, observation.payload or {})
            return llm or observation.payload.get("answer", "Politika bulunamadı.")

        if plan["intent"] == "pricing":
            llm = render_with_gemini(plan["intent"], message, observation.payload or {})
            if llm:
                return llm
            total = observation.payload.get("total")
            currency = observation.payload.get("currency", "TRY")
            breakdown = observation.payload.get("breakdown", "")
            return f"Toplam: {total} {currency}. {breakdown}"

        return "Yanıt üretilemedi."


# --------- CLI döngüsü ----------
if __name__ == "__main__":
    print(f"[DEBUG] LLM={'ON' if _GEMINI else 'OFF'}")
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
