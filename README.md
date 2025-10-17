# 🏘️ İnteraktif Şirince Otel Tavsiye Paneli

Bu proje, Şirince'de otel arayan kullanıcılara yardımcı olmak için geliştirilmiş, Streamlit tabanlı interaktif bir web uygulamasıdır. Kullanıcılar, otel yorumlarını filtreleyebilir, puanları görsel olarak karşılaştırabilir ve spesifik sorularını chatbot'a sorabilirler.

![Uygulama Görüntüsü](panel_goruntusu.png)
*(NOT: Uygulamanızın çalışan halinin ekran görüntüsünü alıp `panel_goruntusu.png` adıyla proje klasörünüze eklemeyi unutmayın!)*

---

## 🚀 Projenin Amacı

Bu projenin temel amacı, ham bir veri setinden yola çıkarak son kullanıcının kolayca anlayabileceği ve karar verme sürecinde kullanabileceği anlamlı bir ürün ortaya koymaktır. Veri analizi, veri görselleştirme ve basit doğal dil işleme yeteneklerini tek bir hibrit panelde birleştirmeyi hedefler.

## ✨ Özellikler

- **İnteraktif Filtreleme:** Kullanıcılar otelleri ve minimum puanları kenar çubuğundan kolayca filtreleyebilir.
- **Dinamik Göstergeler:** Filtrelere göre anlık olarak güncellenen ortalama puan, yorum sayısı gibi kilit performans göstergeleri (KPI).
- **Veri Görselleştirme:** Otel puanlarının karşılaştırmalı analizini sunan interaktif **Plotly** grafikleri.
- **Hibrit Chatbot:** Kullanıcıların "En iyi otel hangisi?" veya "Kirke otelin en kötü yorumu ne?" gibi spesifik sorular sorabildiği, açılır-kapanır chatbot modülü.

## 🛠️ Kullanılan Teknolojiler

- **Python:** Ana programlama dili.
- **Streamlit:** Hızlı ve interaktif web arayüzü oluşturmak için.
- **Pandas:** Veri manipülasyonu ve analizi için.
- **Plotly:** Etkileşimli ve şık veri görselleştirmeleri için.

---

## 🏃‍♀️ Kurulum ve Çalıştırma

Bu projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1.  **Depoyu klonlayın:**
    ```bash
    git clone https://github.com/busranirgulelmadag/otel-tavsiye-chatbot-panel.git
    ```
    cd otel-tavsiye-chatbot-panel
    ```

2.  **Sanal ortam oluşturun ve aktive edin:**
    ```bash
    python -m venv venv
    # Windows için:
    venv\Scripts\activate
    # macOS/Linux için:
    source venv/bin/activate
    ```

3.  **Gerekli kütüphaneleri yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Uygulamayı çalıştırın:**
    ```bash
    streamlit run app.py
    ```
Uygulama, tarayıcınızda otomatik olarak açılacaktır.

## 🔗 Canlı Uygulamayı Görün

Uygulamaya doğrudan Streamlit Cloud üzerinden erişmek için aşağıdaki bağlantıyı kullanabilirsiniz:

[OTEL TAVSİYE CHATBOT PANELİ CANLI BAĞLANTI](https://otel-tavsiye-chatbot-panel.streamlit.app/)

---