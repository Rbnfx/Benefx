from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def consultar_processo_tjal(numero_processo):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www2.tjal.jus.br/cpopg/open.do")
        time.sleep(2)
        campo = driver.find_element(By.ID, "numeroDigitoAnoUnificado")
        campo.clear()
        campo.send_keys(numero_processo)
        driver.find_element(By.NAME, "pesquisar").click()
        time.sleep(3)
        try:
            movimento = driver.find_element(By.CLASS_NAME, "unj-singleValue").text
        except:
            movimento = "Informações não encontradas"
    except Exception as e:
        movimento = f"Erro na consulta: {e}"
    finally:
        driver.quit()
    return movimento
