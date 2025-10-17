import streamlit as st
import pandas as pd
import torch
import numpy as np # Pandas ile birlikte lazım olabilir

# RAG Kütüphaneleri
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Sabit Tanımlamalar
FILE_PATH = "sirince_otelleri.csv"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ----------------------------------------------------
# 1. RAG KURULUM FONKSİYONLARI (Cache ile sadece 1 kez çalışır)
# ----------------------------------------------------

@st.cache_resource
def setup_rag_faiss(file_path):
    # Veriyi yükle (CSV'nizin kodlaması farklıysa encoding='iso-8859-9' deneyin)
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return None # Hata durumunda None döndür

    # DataFrame'i LangChain dokümanlarına dönüştür
    loader = DataFrameLoader(df, page_content_column="Yorum_Metni")
    data = loader.load()

    # Metin parçalama (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(data)

    # Embedding modelini tanımla
    device = "cuda" if torch.cuda.is_available() else "cpu"
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={'device': device})

    # Vektör veritabanını oluştur ve doldur
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    return vectorstore

# Sadece EN ALAKALI TEK BİR SONUCU getiren fonksiyon
def get_answer_from_retriever(vectorstore, query):
    # k=1 ile sadece en alakalı TEK bir yorumu bul
    results = vectorstore.similarity_search(query, k=1) 
    
    if results:
        doc = results[0]
        otel_adi = doc.metadata.get('Otel_Adi', 'Bilinmiyor')
        yorum = doc.page_content
        
        response = (
            f"**En Alakalı Bilgi Şuradan Bulunmuştur:** **{otel_adi}**\n\n"
            f"**Alıntı Yapılan Yorum:** *'{yorum}'*"
        )
    else:
        response = "Üzgünüm, yorumlarda bu konuyla ilgili çok alakalı bir bilgi bulamadım."
    
    return response


# ----------------------------------------------------
# 2. STREAMLIT ANA UYGULAMA GÖVDESİ (Hibrit Panel)
# ----------------------------------------------------

st.set_page_config(layout="wide", page_title="Hibrit Otel Analiz ve Chatbot")

st.title("Hibrit Şirince Otel Analiz Paneli & RAG Chatbot")
st.markdown("Veriyi soldaki filtrelerle görsel olarak keşfedin veya aşağıdaki chatbot'a spesifik sorular sorun.")

# ----------------------------------------------------
# CHATBOT ALANI (Dashboard'un Hemen Altında)
# ----------------------------------------------------

st.header("🤖 Yorumlara Dayalı Chatbot")
st.markdown("Otel yorumlarında arama yapmak için bir soru sorun. Örneğin: *'Kahvaltısı harika olan bir konak var mıydı?'*")

# RAG kurulumunu yap
vector_db = setup_rag_faiss(FILE_PATH)

if vector_db:
    user_query = st.text_input("Sorgunuzu buraya girin:")

    if user_query:
        with st.spinner("Yorumlarda anlamsal arama yapılıyor..."):
            response = get_answer_from_retriever(vector_db, user_query)
            st.success("Sorgunuza En Alakalı Cevap:")
            st.markdown(response)
            
st.markdown("---") # Chatbot ile Dashboard arasına ayırıcı


# ----------------------------------------------------
# DASHBOARD / ANALİZ ALANI (Chatbot'tan Sonra)
# ----------------------------------------------------

# BU NOKTADAN SONRA, ESKİ FİLTRELEME VE GRAFİK KODLARINIZ DEVAM ETMELİDİR.
# 
# Örnek Başlıklar (Eski Kodlarınızdan Alınmıştır)
st.header("📊 Genel Bakış ve Analiz") 

# Burada, önceki filtreleme ve grafik kodlarınız yer almalı. 
# Örneğin:
# df = pd.read_csv("sirince_otelleri.csv")
# selected_hotels = st.sidebar.multiselect("Otelleri Seçin:", df['Otel_Adi'].unique())
# # ... diğer filtreler, grafikler ve metrikler ...

# ÖNEMLİ: Eğer mevcut filtreleme kodlarınızda "st.title" veya "st.header" gibi 
# kodlar tekrarlanıyorsa, onları SİLİN ve sadece grafik/filtre mantığını buraya taşıyın.