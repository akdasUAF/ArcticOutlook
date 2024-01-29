#!/usr/bin/env python3

#
# Author: Darian Marvel
#
#

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import dynamic_v2.Crawler as Crawler
import dynamic_v2.Scraper as Scraper
import dynamic_v2.Debug as Debug

# Definitions
#import ScraperDefinitions.WaterSystem
import dynamic_v2.create_instruction as create_instruction

def main(url, instructs, jsp):
    # TEMPORARY FOR TESTING

    crawler = Crawler.Crawler()
    #ScraperDefinitions.WaterSystem.setup_crawler(crawler)
    create_instruction.setup_crawler(crawler)

    scrappy = Scraper.Scraper()
    #ScraperDefinitions.WaterSystem.setup_scraper(scrappy)

    # Test file
    # inst = [(1, ["table"]), (1, ["td"]), (3, ["system_number"]), (1, ["td"]), (1, ["td"]), (3, ["system_name"]), (1, ["td"]), (3, ["federal_type"]),
    #         (1, ["td"]), (3, ["county_served"]), (1, ["td"]), (3, ["primary_source"]), (1, ["td"]), (3, ["status"]), (1, ["td"]), (3, ["activity_date"]),
    #         (1, ["table"]), (9, ["points_of_contact"])]
    create_instruction.setup_scraper(scrappy, instructs)


    driver = webdriver.Firefox()
    driver.get(url)
    driver.maximize_window() # My Edit

    # Click the button to navigate to the water system list
    # If the user specifies that there is a specific JSP button to press, handle this case
    if jsp:
        temp_scraper = Scraper.Scraper()
        temp_scraper.activate_live_mode()
        temp_scraper.set_web_driver(driver)
        temp_scraper.then_go_back_to_beginning()
        temp_scraper.then_skip_to_element_with_attribute("input", "value", "Search For Water Systems")
    
        # My Edit
        actions = ActionChains(driver)
        actions.move_to_element(temp_scraper.current_element).perform()

        # My Edit
        WebDriverWait(driver, 1000).until(EC.element_to_be_clickable(temp_scraper.current_element)).click()
        #temp_scraper.current_element.click()

    scrappy.set_web_driver(driver)
    crawler.set_web_driver(driver)
    max_items = 5
    crawler.set_max_items(max_items + 2)
    # data = scrappy.scrape()
    data = crawler.crawl_and_scrape(scrappy)

    driver.close()

    return data

if __name__ == "__main__":
    main()