\# Amatis Support Mini-Agent (Python)



Bu proje, \*\*LLM Agent mantığını\*\* basit bir şekilde göstermek için hazırlanmış bir mini örnektir.  

Kullanıcıdan gelen mesajları yorumlar, \*\*niyet (intent)\*\* tespiti yapar, uygun \*\*tool\*\* seçer ve yanıt üretir.



\## Özellikler

\- Intent tespiti: sipariş sorgulama, iade politikası, fiyat hesaplama

\- Tool çağrısı:

&nbsp; - Sipariş durumu → `data/orders.json` okunur

&nbsp; - İade politikası → `kb/return\_policy.md` özetlenir

&nbsp; - Fiyat → %10 KDV ile toplam hesaplanır

\- Genişletilebilir yapı (yeni tool eklemek kolay)



\## Proje Yapısı

\- `agent.py` – agent döngüsü: planlama, tool seçimi, cevap üretme

\- `tools.py` – tool fonksiyonları

\- `data/orders.json` – örnek sipariş verisi

\- `kb/return\_policy.md` – bilgi tabanı (Markdown)



\## Çalıştırma

```bash

python agent.py



