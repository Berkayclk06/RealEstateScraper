import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
import lxml
import os


class DataScraper:
    def __init__(self):
        self.data_url = os.environ["DATA_URL"]
        self.header = {
            "Accept-Language": "en-US,en-TR;q=0.9,en;q=0.8,tr-TR;q=0.7,tr;q=0.6",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                    }
        self.response = requests.get(self.data_url, headers=self.header)
        self.response.raise_for_status()
        self.web_page = self.response.text
        self.soup = BeautifulSoup(self.web_page, "lxml")
        self.link_list = []
        self.price_list = []
        self.address_list = []
        self.get_links()
        self.get_prices()
        self.get_address()

    def get_links(self):
        # Create list for 'href' links.
        self.link_list = [link["href"] for link in
                          self.soup.find_all(name="a", class_="property-card-link", tabindex="0")]
        # Add url at the beginning of the items if it's not an actual link.
        for index, link in enumerate(self.link_list):
            if not link.startswith("https:"):
                link2 = os.environ["DATA_MP"] + link
                self.link_list[index] = link2
            else:
                pass

    def get_prices(self):
        self.price_list = [price.text.removesuffix("+ 1 bd").removesuffix("/mo")
                           for price in self.soup.find_all(name="span") if "data-test" in price.attrs]

    def get_address(self):
        self.address_list = [address.text for address in self.soup.find_all(name="address")]


class FormFill:
    def __init__(self):
        self.chrome_driver_path = os.environ["CHROME_DRIVER_PATH"]
        self.s = Service(self.chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.s)
        self.data = DataScraper()

    def fill_form(self, url_input):
        for i in range(len(self.data.link_list)):
            self.driver.get(url_input)
            time.sleep(1)
            property_address = self.driver.find_elements("css selector", '.Xb9hP input')[0]
            price_pm = self.driver.find_elements("css selector", '.Xb9hP input')[1]
            link_prop = self.driver.find_elements("css selector", '.Xb9hP input')[2]
            property_address.send_keys(self.data.address_list[i])
            price_pm.send_keys(self.data.price_list[i])
            link_prop.send_keys(self.data.link_list[i])
            time.sleep(1)
            self.driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span').click()


if __name__ == "__main__":
    url = os.environ["FORM_URL"]
    form = FormFill()
    data = DataScraper()
    form.fill_form(url)
