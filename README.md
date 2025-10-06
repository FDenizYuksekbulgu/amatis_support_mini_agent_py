# 🎯 Amatis Support Mini-Agent (Gemini LLM Entegre)

Bu proje, **Google Gemini (Generative AI)** ile entegre edilmiş, küçük ama güçlü bir müşteri destek mini-asistanıdır.  
Sipariş durumu, iade politikası ve fiyat hesaplama gibi temel talepleri akıllıca yorumlar.

---

## 🚀 Özellikler
- ✅ **Gemini API (LLM)** ile doğal dil anlama ve yanıt üretimi  
- 🧠 **Niyet (intent) tespiti:** `order_status`, `return_policy`, `pricing`, `chitchat`  
- 🛠️ **Araç (Tool) sistemi:** sipariş sorgu, iade politikası okuma, fiyat hesaplama  
- 🇹🇷 Tamamen **Türkçe** destek yanıtları  
- ⚙️ **Offline fallback:** API yoksa kural tabanlı yanıtlar verir  

---

## 🧩 Kurulum

### 1️⃣ Gerekli bağımlılıklar
```bash
pip install google-generativeai
