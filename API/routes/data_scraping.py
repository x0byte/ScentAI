import requests
from bs4 import BeautifulSoup

url = "https://www.fragrantica.com/perfume/masaki-matsushima/fleur-de-sansho-47873.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

print(soup.title.text)