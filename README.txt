
ETAPA 3 - Scraper TJAL (Consulta Processos Online)
---------------------------------------------------
1. Requisitos:
   - Python 3.11+
   - Selenium
   - Google Chrome + ChromeDriver

2. Instale as dependências com:
   pip install selenium

3. Execute com:
   from scraper_tjal import consultar_processo
   html = consultar_processo("0700001-85.2022.8.02.0001")
   print(html[:1000])
