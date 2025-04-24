import streamlit as st
import pandas as pd

st.title("🔍 Validador da Base de Precatórios")

uploaded_file = st.file_uploader("Selecione a base (.csv) para validar", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
        st.success("Arquivo carregado com sucesso!")
        colunas_esperadas = [
            "numero_processo", "tipo", "valor", "tribunal",
            "ente_devedor", "status_pagamento", "ano_orcamento",
            "tempo_pagamento_previsto", "retorno_anual", "score"
        ]
        colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]

        if colunas_faltantes:
            st.error(f"⚠️ Faltam as seguintes colunas obrigatórias: {', '.join(colunas_faltantes)}")
        else:
            st.success("✅ A base contém todas as colunas necessárias.")
            st.dataframe(df.head(50), use_container_width=True)

            st.download_button(
                "📥 Baixar base validada",
                data=df.to_csv(index=False, sep=";", encoding="utf-8"),
                file_name="base_validada.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Erro ao carregar a base: {e}")