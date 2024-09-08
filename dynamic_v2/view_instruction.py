# Slightly edited version of the Extract.py file. 
# This file will follow the instruction list to the current url and return it.

from dynamic_v2.Extract import main as dynamic_v2

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

import dynamic_v2.Crawler as Crawler
import dynamic_v2.Scraper as Scraper
import dynamic_v2.Debug as Debug

# Definitions
#import ScraperDefinitions.WaterSystem
import dynamic_v2.create_instruction as create_instruction

def main(url, instructs, jsp, auto_list):
    # TEMPORARY FOR TESTING

    crawler = Crawler.Crawler()
    #ScraperDefinitions.WaterSystem.setup_crawler(crawler)
    create_instruction.setup_crawler(crawler)

    scrappy = Scraper.Scraper()
    #ScraperDefinitions.WaterSystem.setup_scraper(scrappy)

    create_instruction.setup_scraper(scrappy, instructs)

    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
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
    
        actions = ActionChains(driver)
        actions.move_to_element(temp_scraper.current_element).perform()

        WebDriverWait(driver, 1000).until(EC.element_to_be_clickable(temp_scraper.current_element)).click()
        #temp_scraper.current_element.click()

    scrappy.set_web_driver(driver)
    crawler.set_web_driver(driver)
    max_items = 1
    crawler.set_max_items(max_items + 2)
    # If the user specifies that the first page is a list of links that needs to be scraper, 
    if auto_list:
        data = crawler.crawl_and_scrape(scrappy, True)
        url = crawler.last_url
        elem = crawler.last_instruction
    else:
        data = scrappy.scrape()
        url = driver.current_url
        elem = driver.switch_to.active_element
    js = 'arguments[0].style.backgroundColor = "blue";'
    # js = """const nodeList = document.querySelectorAll("table"); 
    #                 for (let i = 0; i < nodeList.length; i++) { //looping over each table
    #                 nodeList[i].style.backgroundColor = "red";
    #                 if(nodeList[i].text.includes("AK")){ 
    #                     nodeList[i].style.backgroundColor = "blue";
    #                 }
    #                 }"""
    #driver.execute_script(js, elem)

    # driver.execute_script(js, elem2)
    #sleep(15)
    driver.close()

    return url

if __name__ == "__main__":
    main()