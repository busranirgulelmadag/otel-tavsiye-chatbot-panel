import streamlit as st
import pandas as pd
import torch
import os # Ortam değişkenlerini yönetmek için (gerekirse)

# RAG Kütüphaneleri
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Sabit Tanımlamalar
FILE_PATH = "sirince_otelleri.csv"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ----------------------------------------------------
# RAG KURULUM FONKSİYONLARI (Cache ile sadece 1 kez çalışır)
# ----------------------------------------------------

@st.cache_resource
def setup_rag_faiss(file_path):
    # 1. Veriyi yükle
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Hata: Veri dosyası bulunamadı: {file_path}")
        return None

    # DataFrame'i LangChain dokümanlarına dönüştür (Yorum_Metni sütununu kullanıyoruz)
    loader = DataFrameLoader(df, page_content_column="Yorum_Metni")
    data = loader.load()

    # Metin parçalama (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(data)

    # Embedding modelini tanımla (Yerel, API gerektirmez)
    # Cihazda GPU varsa kullanır, yoksa CPU'da çalışır
    device = "cuda" if torch.cuda.is_available() else "cpu"
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={'device': device})

    # Vektör veritabanını oluştur ve doldur
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    return vectorstore

def get_answer_from_retriever(vectorstore, query):
    # En alakalı 3 yorumu bul (k=3 en alakalı 3 dokümanı getirir)
    results = vectorstore.similarity_search(query, k=3) 
    
    # Bulunan yorum metinlerini birleştir
    context_list = []
    
    for doc in results:
        # Hangi otelden geldiğini ve yorum metnini al
        otel_adi = doc.metadata.get('Otel_Adi', 'Bilinmiyor')
        yorum = doc.page_content
        context_list.append(f"**Otel: {otel_adi}** - Yorum: {yorum}")

    # Kullanıcıya bir özet sunun
    response = "\n\n---\n\n".join(context_list)
    
    return response


# ----------------------------------------------------
# STREAMLIT ANA UYGULAMA GÖVDESİ (SADECE RAG BOT)
# ----------------------------------------------------

st.set_page_config(layout="wide", page_title="RAG Chatbot | Otel Yorumları")

st.title("🤖 Şirince Otel Yorumları RAG Chatbot")
st.markdown("---")

# RAG kurulumunu yap (Hata kontrolü eklenmiştir)
vector_db = setup_rag_faiss(FILE_PATH)

if vector_db:
    st.subheader("Otel Yorumlarına Dayalı Akıllı Sorgulama")
    st.markdown("Aşağıdaki alana, otel yorumlarına dayanarak cevap alabileceğiniz bir soru sorun. Örneğin: *'Huzurlu ve temizliği beğenilen bir konak var mı?'*")

    user_query = st.text_input("Sorgunuzu buraya girin:")

    if user_query:
        with st.spinner("Yorumlarda anlamsal arama yapılıyor..."):
            # Cevabı üret
            response = get_answer_from_retriever(vector_db, user_query)
            
            st.success("Sorgunuzla En Alakalı Bilgiler Aşağıdadır:")
            st.markdown(response)

else:
    st.warning("RAG sistemi başlatılamadı. Lütfen 'sirince_otelleri.csv' dosyasının bulunduğundan ve kütüphanelerin yüklü olduğundan emin olun.")