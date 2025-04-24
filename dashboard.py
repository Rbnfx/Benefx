import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

# --------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# --------------------------
st.set_page_config(page_title="Precatório Insights", layout="wide")

# --------------------------
# 2. CARREGAR DADOS
# --------------------------
import os

@st.cache_data(show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    arquivos = os.listdir("data")
    arquivos_csv = [f for f in arquivos if f.endswith(".csv")]

    if not arquivos_csv:
        st.error("Nenhuma base encontrada na pasta /data")
        return pd.DataFrame()

    caminho_base = f"data/{arquivos_csv[0]}"
    df = pd.read_csv(caminho_base, sep=";", encoding="utf-8")

    # Renomear se necessário
    if "tempo_pagamento_previsto" in df.columns:
        df = df.rename(columns={"tempo_pagamento_previsto": "tempo_paga"})

    # Converter valores
    if "valor" in df.columns:
        df["valor_float"] = (
            df["valor"]
              .astype(str)
              .str.replace(r"[R\$\.\s]", "", regex=True)
              .str.replace(",", ".")
              .astype(float)
        )

    # Adicionar score_juridico fixo caso não exista
    if "score_juridico" not in df.columns:
        df["score_juridico"] = 80

    # Adicionar score_total se não existir
    if "score_total" not in df.columns:
        from sklearn.preprocessing import MinMaxScaler

        fatores = []
        pesos = []

        if "tempo_paga" in df.columns:
            fatores.append("tempo_paga")
            pesos.append(0.4)

        if "retorno_anual" in df.columns:
            fatores.append("retorno_anual")
            pesos.append(0.4)

        if "valor_float" in df.columns:
            fatores.append("valor_float")
            pesos.append(0.1)

        if "score_juridico" in df.columns:
            fatores.append("score_juridico")
            pesos.append(0.1)

        try:
            df_scaled = MinMaxScaler().fit_transform(df[fatores])
            df["score_total"] = (df_scaled @ pesos) * 100
        except:
            st.warning("Não foi possível calcular o score_total por falta de colunas necessárias.")

    return df

df = carregar_dados()
# --------------------------
# 3. FILTROS
# --------------------------
st.sidebar.title("🔎 Filtros")

vmin, vmax = st.sidebar.slider(
    "Faixa de Valor (R$)",
    min_value=float(df["valor_float"].min()),
    max_value=float(df["valor_float"].max()),
    value=(df["valor_float"].quantile(0.05), df["valor_float"].quantile(0.95)),
    step=1.0,
    format="%.0f"
)
df = df.query("valor_float >= @vmin and valor_float <= @vmax")

for col, label in [
    ("tipo", "Tipo"),
    ("status_pagamento", "Status de Pagamento"),
    ("tribunal", "Tribunal"),
    ("ente_devedor", "Ente Devedor"),
]:
    options = ["Todos"] + sorted(df[col].dropna().unique().tolist())
    escolha = st.sidebar.selectbox(label, options, key=col)
    if escolha != "Todos":
        df = df[df[col] == escolha]

# --------------------------
# 4. FORMATAÇÃO
# --------------------------
def formatar_real(x: float) -> str:
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

# --------------------------
# 5. SIMULADOR
# --------------------------
with st.sidebar.expander("🔮 Simulador de Retorno"):
    taxa = st.number_input("Taxa Anual Esperada (%)", value=13.0, step=0.1)
    prazo = st.slider("Prazo (meses)", 1, 60, 12)
    ret = (1 + taxa / 100) ** (prazo / 12) - 1
    st.write(f"**Retorno Total:** {ret * 100:.2f}% em {prazo} meses")

# --------------------------
# 6. SCORE FINAL (Risco + Jurídico)
# --------------------------

# Se a base já tiver score_juridico, usa direto. Se não, preenche com valor neutro.
if "score_juridico" not in df.columns:
    df["score_juridico"] = None

df["score_juridico"] = df["score_juridico"].fillna(70)  # valor padrão conservador até análise online ser feita

def calcular_score_completo(df: pd.DataFrame) -> pd.DataFrame:
    fatores = []
    pesos = []

    if "tempo_paga" in df.columns:
        fatores.append("tempo_paga")
        pesos.append(0.35)  # menor prazo = melhor

    if "retorno_anual" in df.columns:
        fatores.append("retorno_anual")
        pesos.append(0.4)  # retorno tem alto peso

    if "valor_float" in df.columns:
        fatores.append("valor_float")
        pesos.append(0.1)

    if "score_juridico" in df.columns:
        fatores.append("score_juridico")
        pesos.append(0.15)  # risco jurídico com peso importante

    # Normalização e score
    scaler = MinMaxScaler()
    df_norm = scaler.fit_transform(df[fatores])
    df["score_total"] = (df_norm @ pesos) * 100
    return df

df = calcular_score_completo(df)
# --------------------------
# 7. MÉTRICAS
# --------------------------
st.title("💡 Melhores Oportunidades de Investimento")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Precatórios", f"{len(df)}")
col2.metric("Valor Total", formatar_real(df["valor_float"].sum()))
col3.metric("Valor Médio", formatar_real(df["valor_float"].mean()))
col4.metric("Prazo Médio", f"{df['tempo_paga'].mean():.1f} meses")
col5.metric("Retorno Médio", f"{df['retorno_anual'].mean():.2f}%")

# --------------------------
# 8. GRÁFICOS
# --------------------------
st.subheader("📊 Análises Visuais")

colA, colB = st.columns(2)
with colA:
    fig = px.histogram(df, x="valor_float", nbins=40, title="Distribuição dos Valores")
    st.plotly_chart(fig, use_container_width=True)

with colB:
    fig2 = px.bar(
        df.groupby("tipo")["retorno_anual"].mean().reset_index(),
        x="tipo", y="retorno_anual", title="Retorno Médio por Tipo"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.plotly_chart(
    px.scatter(df, x="tempo_paga", y="valor_float", color="score_total",
               title="Valor x Prazo com Score",
               labels={"tempo_paga": "Prazo (meses)", "valor_float": "Valor (R$)"})
, use_container_width=True)

# --------------------------
# 9. TOP 10 OPORTUNIDADES
# --------------------------
st.subheader("🏆 Top 10 Oportunidades")
top10 = df.sort_values("score_total", ascending=False).head(10).copy()
top10["Valor"] = top10["valor_float"].map(formatar_real)
top10["Retorno (%)"] = top10["retorno_anual"].round(2)
top10["Score"] = top10["score_total"].round(2)

st.dataframe(top10[[
    "numero_processo", "ente_devedor", "tribunal",
    "Valor", "tipo", "tempo_paga", "Retorno (%)", "Score"
]], use_container_width=True)

# --------------------------
# 10. RANKING
# --------------------------
st.subheader("📈 Ranking por Tribunal")
rank = df.groupby("tribunal")["score_total"].mean().reset_index()
rank["Score Médio"] = rank["score_total"].round(2)
rank = rank.sort_values("Score Médio", ascending=False)
st.dataframe(rank[["tribunal", "Score Médio"]], use_container_width=True)

# --------------------------
# 11. BASE COMPLETA
# --------------------------
st.subheader("📑 Dados Brutos")
df["Valor"] = df["valor_float"].map(formatar_real)
df["Retorno (%)"] = df["retorno_anual"].round(2)
df["Score"] = df["score_total"].round(2)
st.dataframe(df[[
    "numero_processo", "ente_devedor", "tribunal", "Valor", "tipo",
    "tempo_paga", "status_pagamento", "ano_orcamento", "Retorno (%)", "Score"
]], use_container_width=True)

# --------------------------
# 12. EXPORTAÇÃO
# --------------------------
csv = df.to_csv(index=False, sep=";", encoding="utf-8")
st.sidebar.download_button(
    "📥 Exportar Tabela Completa",
    data=csv,
    file_name="precatórios_filtrados.csv",
    mime="text/csv"
)

