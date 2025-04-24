
import streamlit as st
import pandas as pd
import os

def cadastrar_precatorio():
    with st.expander("📝 Abrir formulário de cadastro"):
        numero = st.text_input("Número do Processo")
        valor = st.text_input("Valor (ex: 1.234.567,89)")
        tipo = st.selectbox("Tipo", ["Alimentar", "Comum"])
        status = st.selectbox("Status de Pagamento", ["Pago", "Não pago"])
        ente = st.text_input("Ente Devedor")
        retorno = st.number_input("Retorno Anual (%)", min_value=0.0, step=0.1)
        tempo = st.number_input("Tempo de Pagamento Previsto (meses)", min_value=0)
        if st.button("Salvar Precatório"):
            try:
                valor_float = float(valor.replace(".", "").replace(",", "."))
                novo = {
                    "numero_processo": numero,
                    "valor": valor_float,
                    "tipo": tipo,
                    "status_pagamento": status,
                    "ente_devedor": ente,
                    "retorno_anual": retorno,
                    "tempo_pagamento_previsto": tempo,
                    "score": int((retorno / tempo) * 100) if tempo > 0 else 0
                }
                path = os.path.join("data", "base_completa_tjal_2024.csv")
                df = pd.read_csv(path, sep=";", encoding="utf-8")
                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                df.to_csv(path, sep=";", index=False, encoding="utf-8")
                st.success("Precatório cadastrado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao cadastrar: {e}")
