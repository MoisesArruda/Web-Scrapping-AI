import requests
from bs4 import BeautifulSoup
from functools import lru_cache

@lru_cache(maxsize=100)
def fetch_website_content(url: str) -> str:
    """
    Extrai o conteúdo textual de uma página web através de uma requisição HTTP com o método GET.
    Inclui cache para evitar requisições repetidas.

    Parametros:
        url (str): A URL da página web a ser extraída.

    Retorna:
        str: O conteúdo textual da página web.
    """
    try:
        response = requests.get(url, timeout= 10)
        # Busca a tela inicial da página
        # print("Response: ", response)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # print("Soup: ", soup)
            text = soup.get_text(separator=" ", strip=True)
            # print("Text: ", text)
            return text
        return f"Error: Unable to fetch website content (status {response.status_code})"
    except Exception as e:
        return f"Exception: {str(e)}" 

if __name__ == "__main__":
    url = "https://www.cleverdash.ai/"
    print(fetch_website_content(url))
