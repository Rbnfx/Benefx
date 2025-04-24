import pandas as pd
import time
from scraper_tjal import analisar_processo_real

def aplicar_analise_em_lote(caminho_entrada, caminho_saida):
    df = pd.read_csv(caminho_entrada, sep=";", encoding="utf-8")

    resultados = []
    for i, processo in enumerate(df["numero_processo"]):
        print(f"({i+1}/{len(df)}) Analisando processo: {processo}")
        try:
            resultado = analisar_processo_real(str(processo))
            resultados.append(resultado.get("score", 50))  # default se falhar
        except Exception as e:
            print(f"Erro ao analisar {processo}: {e}")
            resultados.append(50)

        time.sleep(2)  # evita bloqueio por excesso de requisições

    df["score_juridico"] = resultados
    df.to_csv(caminho_saida, sep=";", encoding="utf-8", index=False)
    print("Análise concluída. Score jurídico salvo em:", caminho_saida)

if __name__ == "__main__":
    aplicar_analise_em_lote(
        caminho_entrada="data/base_completa_2024.csv",
        caminho_saida="data/base_completa_2024_com_score_juridico.csv"
    )