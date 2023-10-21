from base_scraper import BaseScraper, BeautifulSoup
from helpers import is_valid, is_absolute, get_element_by_id_or_class, handle_session
from criterias import *

# is there something more we can do?
class HTMLScrapper(BaseScraper):
    def __init__(self, criteria: dict) -> None:
        super().__init__(criteria)

        self.target_tag = criteria.get("tag", None)

    def get_links_by_exploring(self, max_level: int = 1):
        explore_path = self._criteria.get("explore_path", None)
    
        if explore_path is None: 
            return self.get_sublinks_singlepage()
        
        # below 1 bad!!!
        max_level = max(max_level, 1)

        # print(self.seed_url, explore_path)
        fullpath = f"{self.seed_url}/{explore_path}"

        for i in range(1, max_level + 1):
            numpath = fullpath.replace("page_num", str(i), 1)
           #  print("Going to: ", numpath)
            self._connect_and_add_sublinks(numpath)

        return super().get_links_by_exploring(max_level)
    
    def _connect_and_add_sublinks(self, url: str):
        print("Passed URL: ", url)
        conn = self.handle_page_session(url=url)
        soup = BeautifulSoup(conn.text, "html.parser")

        element = get_element_by_id_or_class(self._criteria, soup)
    
        for link in element.find_all("a"):
            href = link.get("href")

            if (href is None) or self.is_forbidden_sublink(href): 
                continue

            if not is_absolute(href):
                href = f"{self.seed_url}{href}"
            
            # doesn't match with the seed url.
            if not is_valid(href, self.seed_url): 
                continue

            self.cached_links.add(href)

scrap = HTMLScrapper(CNNCHILE)
scrap.get_links_by_exploring(10)
scrap.save_news()