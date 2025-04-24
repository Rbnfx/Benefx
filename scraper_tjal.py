
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def consultar_processo(numero_processo):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www2.tjal.jus.br/cpopg/open.do")
        time.sleep(2)

        campo = driver.find_element(By.ID, "numeroDigitoAnoUnificado")
        campo.send_keys(numero_processo[:7])

        campo_ano = driver.find_element(By.ID, "foroNumeroUnificado")
        campo_ano.send_keys(numero_processo[8:12])

        campo_justica = driver.find_element(By.ID, "foroId")
        campo_justica.send_keys(numero_processo[-4:])

        botao = driver.find_element(By.XPATH, "//input[@value='Consultar']")
        botao.click()
        time.sleep(3)

        pagina = driver.page_source
        return pagina
    except Exception as e:
        return f"Erro: {e}"
    finally:
        driver.quit()

from bs4 import BeautifulSoup

def analisar_processo_real(numero_processo):
    html = consultar_processo(numero_processo)

    if "Erro:" in html:
        return {
            "fase": "Desconhecida",
            "movimentacoes": "",
            "risco": "Desconhecido",
            "observacoes": "Não foi possível acessar o processo.",
            "score": 50
        }

    soup = BeautifulSoup(html, "html.parser")

    try:
        # Extrair fase do processo
        fase_tag = soup.find("span", string="Classe:")
        fase = fase_tag.find_next("td").text.strip() if fase_tag else "Desconhecida"

        # Extrair últimas movimentações
        tabela_movs = soup.find("table", class_="secaoFormBody")
        linhas = tabela_movs.find_all("tr")[1:6] if tabela_movs else []
        movimentacoes = []
        for linha in linhas:
            colunas = linha.find_all("td")
            if len(colunas) >= 2:
                movimentacoes.append(f"{colunas[0].text.strip()}: {colunas[1].text.strip()}")

        resumo = {
            "fase": fase,
            "movimentacoes": "\n".join(movimentacoes),
            "risco": "Baixo" if "Baixa" not in fase else "Desfavorável",
            "observacoes": "Análise automática com base no portal TJAL.",
            "score": 87 if "Cumprimento" in fase else 50
        }

        return resumo

    except Exception as e:
        return {
            "fase": "Erro",
            "movimentacoes": "",
            "risco": "Desconhecido",
            "observacoes": f"Erro de análise: {e}",
            "score": 50
        }