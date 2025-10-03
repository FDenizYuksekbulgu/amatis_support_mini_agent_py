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



---



\## 🖥️ Demo Terminal Çıktısı



```bash

$ python agent.py



Kullanıcı: Sipariş 1234567 nerede?

Agent: Sipariş durumu: Kargoya verildi. Tahmini teslim: 3-5 gün.



Kullanıcı: İade nasıl yapılır?

Agent: Ürün teslim tarihinden itibaren 14 gün içinde iade edebilirsiniz. Detaylar: kb/return\_policy.md



Kullanıcı: 3 adet 129.90 TL toplam ne olur?

Agent: Toplam: 428.67 TRY  (adet:3 × 129.9 = 389.7 + KDV %10 → 38.97)



Kullanıcı: İstanbul çalışma saatleri?

Agent: Hafta içi 09:00-19:00, Cmt 10:00-16:00









