import requests
from bs4 import BeautifulSoup

url = "https://scholarlypublications.universiteitleiden.nl/handle/1887/92931"  # voorbeeld

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

print("Statuscode:", response.status_code)
print("Pagina-titel:", BeautifulSoup(response.text, "html.parser").title.string)