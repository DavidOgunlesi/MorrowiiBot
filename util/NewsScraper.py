from bs4 import BeautifulSoup
import requests
import types

class WorldEventsScraper:

    def __init__(self, url: str, tags: str, attrs: dict = None) -> None:
        self.url = url
        self.tags = tags
        self.attrs = attrs

    '''Returns the html of the url on the object'''
    def get_html(self) -> str:
        r = requests.get(self.url)
        return r.text

    '''Returns a list of headlines from the url on the object'''
    def get_links(self) -> list[str]:
        html = self.get_html()
        soup = BeautifulSoup(html, 'html.parser')
        if self.attrs is None:
            headlines = soup.find_all(self.tags)
        else:
            headlines = soup.find_all(self.tags, attrs=self.attrs)
        return headlines
    
    '''Returns a list of headlines from the url on the object, without duplicates'''
    def get_text(self) -> list[str]:
        links = self.get_links()

        # remove duplicates
        links = list(set(links))

        return [link.text for link in links]


# example usage
# scraper = WorldEventsScraper('https://www.bbc.co.uk/news/topics/cjnwl8q4g7nt?page=1', 'span', {'aria-hidden': 'false'})
# print(scraper.get_text())