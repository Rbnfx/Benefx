# 1_Upload_Base.py

import streamlit as st
import pandas as pd

st.set_page_config(page_title="📁 Upload de Nova Base", layout="wide")

st.title("📁 Atualizar Base de Dados de Precatórios")
st.markdown("Envie abaixo um arquivo `.csv` com os dados reais atualizados para análise.")

arquivo = st.file_uploader("📥 Envie a base de dados (formato CSV separado por ponto e vírgula)", type="csv")

if arquivo:
    try:
        df = pd.read_csv(arquivo, sep=";", encoding="utf-8")
        st.success("Arquivo carregado com sucesso!")
        st.dataframe(df.head())
        st.info("⚠️ A base ainda precisa ser integrada manualmente à análise principal.")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
else:
    st.info("Envie um arquivo CSV real e válido para continuar.")
