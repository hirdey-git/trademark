import requests
from bs4 import BeautifulSoup

def search_trademark_tess(term):
    search_url = "https://tmsearch.uspto.gov/search/search-information"
    params = {
        'f': 'toc',
        'state': '4802:qnn9gs.1.1',
        'p_search': 'searchstr',
        'p_L': '25',
        'BackReference': 'refine',
        'p_plural': 'yes',
        'p_s_ALL': term,
        'a_default': 'search',
        'p_s_PARA1': term
    }

    response = requests.get(search_url, params=params)
    soup = BeautifulSoup(response.content, "html.parser")

    result_links = soup.select('a[href^="showdoc"]')
    trademarks = []

    for link in result_links[:10]:  # limit to top 10 results
        row = link.find_parent("tr")
        if row:
            cols = row.find_all("td")
            if len(cols) >= 3:
                serial = cols[0].text.strip()
                mark = cols[1].text.strip()
                status = cols[2].text.strip()
                trademarks.append(f"{serial} - {mark} ({status})")

    return trademarks
