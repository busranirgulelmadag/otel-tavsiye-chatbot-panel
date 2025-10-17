import streamlit as st
import pandas as pd

# RAG Kütüphaneleri (OpenAI ve ChromaDB)
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI # OpenAI'ın yeni import yolu
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Sabit Tanımlamalar
FILE_PATH = "sirince_otelleri.csv"
# Model adını küçük ve uygun maliyetli bir LLM ile değiştiriyoruz
LLM_MODEL = "gpt-3.5-turbo" 

# ----------------------------------------------------
# 1. RAG KURULUM FONKSİYONLARI 
# ----------------------------------------------------

@st.cache_resource
def setup_rag_chroma():
    # API Anahtarını Streamlit Secrets'ten güvenli bir şekilde al
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("Hata: OPENAI_API_KEY bulunamadı. Lütfen Streamlit Secrets'e ekleyin.")
        return None
    api_key = st.secrets["OPENAI_API_KEY"]

    try:
        df = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        return None

    # Veri İşleme
    loader = DataFrameLoader(df, page_content_column="Yorum_Metni")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(data)

    # Embedding modelini tanımla (OpenAI - Yüksek Kalite)
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)

    # Vektör veritabanını oluştur
    vectorstore = Chroma.from_documents(docs, embeddings)
    
    return vectorstore

@st.cache_resource
def get_rag_chain(vectorstore):
    if vectorstore is None:
        return None
        
    # LLM (OpenAI GPT-3.5)
    llm = ChatOpenAI(temperature=0, model_name=LLM_MODEL, openai_api_key=st.secrets["OPENAI_API_KEY"])
    
    # RetrievalQA zinciri: En alakalı 3 sonucu bul ve cevabı üret
    qa_chain = RetrievalQA.from_chain_type(
        llm, 
        chain_type="stuff", 
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}) # K=3 en alakalı 3 dokümanı kullan
    )
    return qa_chain


# ----------------------------------------------------
# STREAMLIT ANA UYGULAMA GÖVDESİ (SADECE RAG BOT)
# ----------------------------------------------------

st.set_page_config(layout="wide", page_title="Yüksek Kaliteli RAG Chatbot")
st.title("⭐️ Yüksek Kaliteli Otel Yorumları RAG Chatbot")
st.markdown("---")

# RAG kurulumunu yap
vector_db = setup_rag_chroma()
qa_chain = get_rag_chain(vector_db)

if qa_chain:
    st.subheader("GPT-3.5 Destekli Akıllı Sorgulama")
    st.info("Bu bot, yalnızca otel yorumlarına dayanarak Türkçe cevaplar üretir.")

    user_query = st.text_input("Otel yorumlarına dayalı bir soru sorun (Örn: Hangi otelin kahvaltısı çok övülmüş?):")

    if user_query:
        with st.spinner("GPT-3.5 cevap üretiyor..."):
            # RAG zincirini çalıştır
            response = qa_chain.run(user_query)
            st.success("🤖 Cevap:")
            st.markdown(response)

else:
    st.warning("RAG sistemi başlatılamadı. Lütfen API anahtarınızın doğru olduğundan ve CSV dosyasının bulunduğundan emin olun.")