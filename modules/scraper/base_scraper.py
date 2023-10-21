from helpers import create_conn, get_base_url, is_valid, is_absolute, get_element_by_id_or_class
from scrapper_data import RobotsParser, NewsSaver, BeautifulSoup
from scraper_constants import EMPTY_LIST

# PARENT CLASS.
class BaseScraper:
    def __init__(self, criteria : dict) -> None:
        # private thing as we are scraping based on this.
        # protected as childs require it.
        self._criteria = criteria
        self.url = criteria.get("url", None)

        self.conn_delay = 0

        # should be like latercera.cl/
        self.seed_url = get_base_url(self.url)

        # try catch goofy aaa thing.
        if self.seed_url is None:
            raise ValueError(f"The seed URL has a null value.")
        
        # imagine using this, but we are doing it for the xml.
        self.__robot_parser = RobotsParser(self.seed_url)
        self.cached_links = set()

        self.news_saver = NewsSaver(self._criteria["news_selector"], "test")

    def set_connection_delay(self, delay : int):
        self.conn_delay = delay
    
    def is_forbidden_sublink(self, link : str):
        forbidden_paths = self._criteria.get("forbidden_paths", EMPTY_LIST)
    
        for path in forbidden_paths:
            if path in link:
                return True
            
        return False
    
    def save_news(self):
        for news_link in self.cached_links:
            conn = create_conn(news_link)

            if not conn: continue

            soup = BeautifulSoup(conn.text, "lxml", from_encoding="utf-8")
            self.news_saver.save_to_dict(soup)

        self.news_saver.save_to_json()

    # force to go to a single url.
    def _connect_and_add_sublinks(self, url : str):
        print("Passed URL: ", url)
        conn = create_conn(url, self.conn_delay)
        soup = BeautifulSoup(conn.text, "html.parser")

        element = get_element_by_id_or_class(self._criteria, soup)
    
        for link in element.find_all("a"):
            href = link.get("href")

            # has weird paths.
            if (href is None) or self.is_forbidden_sublink(href): 
                print("HREF NULL or FORBIDDEN: ", href)
                continue

            if not is_absolute(href):
                print("NOT ABSOULUTE: ", href)
                href = f"{self.seed_url}{href}"
            
            # doesn't match with the seed url.
            if not is_valid(href, self.seed_url): 
                print("URL is not valid according to the seed: ", href)
                continue

            self.cached_links.add(href)

    def get_sublinks_singlepage(self):
        return self._connect_and_add_sublinks(self.url)

    # this could vary in terms of fetching.
    # TODO: Implement it for another news sites.
    def get_links_by_exploring(self, max_level : int = 1):
        pass

    def get_news_links(self):
        return self.cached_links
        
    def get_links_by_sitemap(self):
        pass

    def get_sitemaps(self):
        # can return none.
        return self.__robot_parser.get_sitemaps()