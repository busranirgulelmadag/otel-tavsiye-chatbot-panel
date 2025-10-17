import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Yapılandırması
st.set_page_config(page_title="Hibrit Şirince Otel Paneli", page_icon="🏨", layout="wide")

# Veriyi Yükleme
@st.cache_data
def veri_yukle(dosya_yolu):
    try:
        df = pd.read_csv(dosya_yolu)
        df['Yorum_Tarihi'] = pd.to_datetime(df['Yorum_Tarihi'])
        return df
    except FileNotFoundError:
        return None

DATA = veri_yukle('sirince_otelleri.csv')

# --- CHATBOT'UN İŞLEM MOTORU (TÜM YETENEKLER) ---
def otel_puanini_bul(otel_adi):
    sonuc = DATA[DATA['Otel_Adi'].str.lower() == otel_adi.lower()]
    if not sonuc.empty:
        ortalama_puan = sonuc['Puan'].mean()
        return f"'{otel_adi.title()}' otelinin ortalama müşteri puanı: **{ortalama_puan:.2f} / 5**"
    return f"'{otel_adi.title()}' adında bir otel bulamadım."

def en_kotu_yorumu_bul(otel_adi):
    sonuc = DATA[DATA['Otel_Adi'].str.lower() == otel_adi.lower()]
    if not sonuc.empty:
        en_dusuk_puanli_yorum = sonuc.loc[sonuc['Puan'].idxmin()]
        yorum = en_dusuk_puanli_yorum['Yorum_Metni']
        puan = en_dusuk_puanli_yorum['Puan']
        return f"'{otel_adi.title()}' için en düşük puanlı ({puan}/5) yorum: *\"{yorum}\"*"
    return f"'{otel_adi.title()}' için yorum bulunamadı."

def en_iyi_yorumu_bul(otel_adi):
    sonuc = DATA[DATA['Otel_Adi'].str.lower() == otel_adi.lower()]
    if not sonuc.empty:
        en_yuksek_puanli_yorum = sonuc.loc[sonuc['Puan'].idxmax()]
        yorum = en_yuksek_puanli_yorum['Yorum_Metni']
        puan = en_yuksek_puanli_yorum['Puan']
        return f"'{otel_adi.title()}' için en yüksek puanlı ({puan}/5) yorum: *\"{yorum}\"*"
    return f"'{otel_adi.title()}' için yorum bulunamadı."

def otel_oda_tiplerini_listele(otel_adi):
    sonuc = DATA[DATA['Otel_Adi'].str.lower() == otel_adi.lower()]
    if not sonuc.empty:
        oda_tipleri = sonuc['Oda_Tipi'].unique()
        liste = ", ".join(oda_tipleri)
        return f"'{otel_adi.title()}' otelindeki oda tipleri: **{liste}**"
    return f"'{otel_adi.title()}' adında bir otel bulamadım."

def en_iyi_oteli_bul():
    puan_ortalamalari = DATA.groupby('Otel_Adi')['Puan'].mean()
    en_iyi_otel = puan_ortalamalari.idxmax()
    en_yuksek_puan = puan_ortalamalari.max()
    return f"Müşteri yorumlarına göre en yüksek puanlı otel: **{en_iyi_otel}** (Ortalama Puan: {en_yuksek_puan:.2f})"

# --- CHATBOT'UN BEYNİ (GÜNCELLENMİŞ VERSİYON) ---
def niyeti_anla(kullanici_girdisi):
    girdi_kelimeleri = kullanici_girdisi.lower().split()
    tum_oteller = DATA['Otel_Adi'].unique()

    if any(kelime in girdi_kelimeleri for kelime in ["en iyi", "tavsiye", "öneri", "hangisi"]):
        return 'en_iyi_oteli_bul', None

    bulunan_otel = None
    for kelime in girdi_kelimeleri:
        for otel_tam_adi in tum_oteller:
            if kelime in otel_tam_adi.lower():
                bulunan_otel = otel_tam_adi
                break
        if bulunan_otel:
            break

    if bulunan_otel:
        if any(kelime in girdi_kelimeleri for kelime in ["puan", "puanı", "nasıl", "kaç"]):
            return 'puan_sor', bulunan_otel
        if any(kelime in girdi_kelimeleri for kelime in ["kötü", "şikayet", "olumsuz"]):
            return 'kotu_yorum', bulunan_otel
        if any(kelime in girdi_kelimeleri for kelime in ["iyi", "güzel", "olumlu"]):
            return 'iyi_yorum', bulunan_otel
        if any(kelime in girdi_kelimeleri for kelime in ["oda", "odaları", "oda tipleri"]):
            return 'oda_tipleri', bulunan_otel

    return 'anlasilmadi', None


# --- ANA UYGULAMA ARAYÜZÜ ---
st.title("🏨 Hibrit Şirince Otel Analiz Paneli & Chatbot")
st.write("Veriyi soldaki filtrelerle görsel olarak keşfedin veya aşağıdaki chatbot'a spesifik sorular sorun.")

if DATA is None:
    st.error("HATA: 'sirince_otelleri.csv' dosyası bulunamadı!")
else:
    # BÖLÜM 1: İNTERAKTİF PANEL
    st.sidebar.header("Filtreleme Seçenekleri")
    secilen_oteller = st.sidebar.multiselect("Otelleri Seçin:", options=DATA['Otel_Adi'].unique(), default=DATA['Otel_Adi'].unique())
    puan_araligi = st.sidebar.slider("Minimum Puanı Seçin:", min_value=1, max_value=5, value=1, step=1)
    
    filtrelenmis_df = DATA[(DATA['Otel_Adi'].isin(secilen_oteller)) & (DATA['Puan'] >= puan_araligi)]

    st.markdown("### 📈 Genel Bakış")
    col1, col2, col3 = st.columns(3)
    ortalama_puan = filtrelenmis_df['Puan'].mean()
    col1.metric("Ortalama Puan", f"{ortalama_puan:.2f} / 5")
    toplam_yorum = filtrelenmis_df.shape[0]
    col2.metric("Toplam Yorum", f"{toplam_yorum} adet")

    if not filtrelenmis_df.empty:
        en_iyi_otel = filtrelenmis_df.groupby('Otel_Adi')['Puan'].mean().idxmax()
        col3.metric("Seçimdeki En Popüler Otel", en_iyi_otel)
    else:
        col3.metric("Seçimdeki En Popüler Otel", "N/A")
    
    st.markdown("### 📊 Otel Puanlarının Karşılaştırması")
    puan_ortalamalari = filtrelenmis_df.groupby('Otel_Adi')['Puan'].mean().sort_values(ascending=False).reset_index()
    fig_otel_puan = px.bar(puan_ortalamalari, x='Otel_Adi', y='Puan', title="<b>Otellere Göre Ortalama Müşteri Puanları</b>", labels={'Puan': 'Ortalama Puan', 'Otel_Adi': 'Otel Adı'}, color='Otel_Adi')
    st.plotly_chart(fig_otel_puan, use_container_width=True)

    # BÖLÜM 2: CHATBOT
    st.markdown("---")
    with st.expander("🤖 Chatbot'a Soru Sormak İçin Tıklayın"):
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        prompt = st.text_input("Sorunuzu yazın:", key="chat_input")
        
        if prompt:
            niyet, varlik = niyeti_anla(prompt)
            cevap = ""
            if niyet == 'puan_sor': cevap = otel_puanini_bul(varlik)
            elif niyet == 'kotu_yorum': cevap = en_kotu_yorumu_bul(varlik)
            elif niyet == 'iyi_yorum': cevap = en_iyi_yorumu_bul(varlik)
            elif niyet == 'oda_tipleri': cevap = otel_oda_tiplerini_listele(varlik)
            elif niyet == 'en_iyi_oteli_bul': cevap = en_iyi_oteli_bul()
            else: cevap = "Üzgünüm, ne demek istediğinizi anlayamadım. Lütfen 'puan', 'oda tipleri', 'en iyi otel' gibi anahtar kelimeler içeren bir soru sorun."
            
            st.session_state.chat_history.append({"soru": prompt, "cevap": cevap})

        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**Siz:** {chat['soru']}")
            st.info(f"**Chatbot:** {chat['cevap']}")