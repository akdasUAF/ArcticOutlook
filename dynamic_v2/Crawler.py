#
# Author: Darian Marvel
#
#

from time import sleep
from selenium.common import ElementNotInteractableException
from selenium.webdriver.common.by import By

import dynamic_v2.Debug as Debug

from dynamic_v2.CrawlerInstructionType import CrawlerInstructionType as CrawlerInstructionType

class Crawler(object):

    def __init__(self):
        self.current_element = None
        self.last_selected_element = self.current_element
        self.data = []
        self.live_mode = False
        self.webdriver = None

        self.parent_element = None
        self.item_element = None
        self.sub_item_element = None
        self.max_items = 10

        self.last_url = ""

    def set_web_driver(self, webdriver):
        self.webdriver = webdriver

    def activate_live_mode(self):
        self.live_mode = True

    def deactivate_live_mode(self):
        self.live_mode = False

    def set_max_items(self, param):
        self.max_items = param

    def set_parent_element(self, param):
        self.parent_element = param
        self.__debug("Set parent element selector to " + param)

    def set_item_element(self, param):
        self.item_element = param
        self.__debug("Set item element selector to " + param)

    def set_sub_item_element(self, param):
        self.sub_item_element = param
        self.__debug("Set sub item element selector to " + param)

    @staticmethod
    def __debug(param):
        Debug.debug("[CRAWLER] " + param.__str__())

    def back_to_beginning(self):
        self.current_element = self.webdriver.find_element(By.TAG_NAME, "html")

    def set_current_element(self, element):
        self.current_element = element
        self.__debug("Current element is now at " + self.current_element.location.__str__())

    def crawl_and_scrape(self, scraper):
        self.__debug("Crawling...")
        self.back_to_beginning()
        self.data = []

        for i in range(self.max_items):

            selector = self.create_selector_for_element_in_list(i)


            self.__debug(selector.__str__())

            elem = None
            try:
                elem = self.webdriver.find_element(By.CSS_SELECTOR, selector)
            except:
                continue

            for j in range(3):
                try:
                    elem.click()
                    break
                except ElementNotInteractableException:
                    # Sleep for a moment and try again
                    # This exception can be thrown if the web browser doesn't
                    # scroll down to the element fast enough
                    sleep(0.25)

            scraper_data = scraper.scrape()
            self.data.append(scraper_data)
            self.last_url = self.webdriver.current_url
            self.webdriver.back()
            self.back_to_beginning()


        return self.data

    def create_selector_for_element_in_list(self, i):
        return self.parent_element + " " + self.item_element + ":nth-of-type(" + i.__str__() + ") " + self.sub_item_element

    def set_last_selected_element(self):
        self.last_selected_element = self.current_element

    def did_selected_element_change(self):
        if self.last_selected_element is not self.current_element:
            return True
        return False
