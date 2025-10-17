import streamlit as st
import pandas as pd
import torch

# Yeni Google/Gemini RAG Kütüphaneleri
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Sabit Tanımlamalar
FILE_PATH = "sirince_otelleri.csv"
LLM_MODEL = "gemini-pro" # Kullanılacak Gemini modeli

# ----------------------------------------------------
# 1. RAG KURULUM FONKSİYONLARI (Cache ile sadece 1 kez çalışır)
# ----------------------------------------------------

@st.cache_resource
def setup_rag_chroma():
    # API Anahtarını Streamlit Secrets'ten güvenli bir şekilde al
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Hata: GEMINI_API_KEY bulunamadı. Lütfen Streamlit Secrets'e ekleyin.")
        return None
    
    # Google API anahtarı, LangChain tarafından otomatik olarak kullanılacaktır.

    try:
        df = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        st.error(f"Hata: Veri dosyası bulunamadı: {FILE_PATH}")
        return None

    # Veri İşleme
    loader = DataFrameLoader(df, page_content_column="Yorum_Metni")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(data)

    # Embedding modelini tanımla (Gemini - Yüksek Kalite)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Vektör veritabanını oluştur
    vectorstore = Chroma.from_documents(docs, embeddings)
    
    return vectorstore

@st.cache_resource
def get_rag_chain(vectorstore):
    if vectorstore is None:
        return None
        
    # LLM (Gemini Pro)
    llm = GoogleGenerativeAI(model=LLM_MODEL)
    
    # RetrievalQA zinciri: En alakalı 3 sonucu bul ve cevabı üret
    qa_chain = RetrievalQA.from_chain_type(
        llm, 
        chain_type="stuff", 
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
    )
    return qa_chain


# ----------------------------------------------------
# STREAMLIT ANA UYGULAMA GÖVDESİ (SADECE RAG BOT)
# ----------------------------------------------------

st.set_page_config(layout="wide", page_title="Gemini RAG Chatbot | Otel Yorumları")
st.title("✨ Gemini Destekli Otel Yorumları RAG Chatbot")
st.markdown("---")

# RAG kurulumunu yap
vector_db = setup_rag_chroma()
qa_chain = get_rag_chain(vector_db)

if qa_chain:
    st.subheader("Gemini Destekli Akıllı Sorgulama")
    st.info("Bu bot, otel yorumlarına dayanarak Türkçe cevaplar üretir.")

    user_query = st.text_input("Otel yorumlarına dayalı bir soru sorun (Örn: Hangi otelin kahvaltısı çok övülmüş?):")

    if user_query:
        with st.spinner("Gemini cevap üretiyor..."):
            # RAG zincirini çalıştır
            response = qa_chain.run(user_query)
            st.success("🤖 Cevap:")
            st.markdown(response)

else:
    st.warning("RAG sistemi başlatılamadı. Lütfen GEMINI_API_KEY'in doğru olduğundan ve CSV dosyasının bulunduğundan emin olun.")