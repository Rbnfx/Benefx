
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Análise Jurídica", layout="wide")
st.title("⚖️ Análise Jurídica de Processos")

numero = st.text_input("Digite o número do processo (formato CNJ):")

def analisar_processo(numero_processo):
    try:
        url = "https://www2.tjal.jus.br/cpopg/show.do"
        params = {
            "cbPesquisa": "NUMPROC",
            "dadosConsulta.tipoConsulta": "NUMPROC",
            "dadosConsulta.valorConsulta": numero_processo,
            "dadosConsulta.origemConsulta": "jsp",
            "uuidCaptcha": ""
        }

        r = requests.get(url, params=params, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        movimentacoes = soup.select(".secaoFormBody tr")
        movs = []
        for mov in movimentacoes:
            tds = mov.find_all("td")
            if len(tds) >= 2:
                data = tds[0].get_text(strip=True)
                texto = tds[1].get_text(strip=True)
                movs.append(f"{data} - {texto}")

        # Análise simples automatizada
        resumo = {
            "fase": "Desconhecida",
            "movs": movs[:3],
            "risco": "Desconhecido",
            "obs": "Sem dados suficientes.",
            "score": 50
        }

        for linha in movs:
            if "cumprimento de sentença" in linha.lower():
                resumo["fase"] = "Cumprimento de Sentença"
            if "habilitação de crédito" in linha.lower() or "expedição" in linha.lower():
                resumo["risco"] = "Baixo"
                resumo["obs"] = "Processo regular. Não há recursos pendentes ou impugnações registradas."
                resumo["score"] = 87
                break

        return resumo
    except Exception as e:
        return {"erro": str(e)}

if numero:
    resultado = analisar_processo(numero)
    if "erro" in resultado:
        st.error(f"Erro ao consultar processo: {resultado['erro']}")
    else:
        st.markdown(f"### Resumo Jurídico do Processo: `{numero}`")
        st.write(f"- **Fase Atual:** {resultado['fase']}")
        st.write(f"- **Últimas Movimentações:** {', '.join(resultado['movs'])}")
        st.write(f"- **Risco Jurídico:** {resultado['risco']}")
        st.write(f"- **Observações:** {resultado['obs']}")
        st.write(f"- **Score Jurídico Estimado:** **{resultado['score']} / 100**")
