#!/usr/bin/env python3

#
# Author: Darian Marvel
#
#
import json, sys, os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import Crawler as Crawler
import Scraper as Scraper
import Debug as Debug 

# Definitions
#import ScraperDefinitions.WaterSystem
# import create_instruction as create_instruction

def setup_scraper(scraper, instructions, pwsids):
    for i in instructions:
        name = i[0]
        params = i[1]
        instr_name = i[3]
        match name:
            case "skip_to_tag":
                scraper.then_skip_to_element(params[0], params[5], instr_name)
            case "skip_to_class":
                scraper.then_skip_to_class(params[0], params[5], instr_name)
            case "save_value_as_property":
                scraper.then_save_value_as_property(params[0], instr_name)
            # tag, param
            case "save_attribute_as_property":
                scraper.then_save_attribute_as_property(params[1], params[0], instr_name)
            case "back_to_beginning":
                scraper.then_go_back_to_beginning(instr_name)
            # tag, attribute, value
            case "skip_to_element_with_attribute":
                scraper.then_skip_to_element_with_attribute(params[1], params[2], params[3], params[5], instr_name)
            case "click_element":
                scraper.then_click_element(instr_name)
            case "goto_previous_page":
                scraper.then_go_back(instr_name)
            case "scrape_table":
                scraper.then_scrape_table(params[0], instr_name)
            case "run_function":
                scraper.then_run_function(params[0], instr_name)
            # tag, attribute, value, function_name
            case "for_each":
                scraper.then_for_each(params[1], params[2], params[3], params[4], instr_name)
            case "create_function":
                scraper.create_function(params[0])
            case "end_function":
                scraper.end_function()
            case "special_for_each":
                scraper.special_for_each(params[0], params[1], params[2], params[3], params[4], params[5], instr_name)
            case "form_send_keys":
                scraper.then_send_keys(params[0], params[1], params[2], params[3], instr_name)
            case "form_submit":
                scraper.then_form_submit(params[1], params[2], params[3], instr_name)
            case "delay":
                scraper.then_delay(instr_name)
            case "save_url":
                scraper.then_save_url(params[0], instr_name)
            case "check_for_text":
                scraper.then_check_for_text(params[0], params[3], instr_name)
            case "for_list":
                scraper.then_for_list(pwsids, params[4], instr_name)
            case _:
                print("Invalid Instruction")

def setup_crawler(crawler):

    # The element that holds all of the item elements we really want
    # (table rows, etc)
    crawler.set_parent_element("table")

    # The elements that will be looped over
    crawler.set_item_element("tr")

    # Any sub-element(s) that have to be clicked on
    crawler.set_sub_item_element("a")

def main(url, instructs, pwsids):
    # TEMPORARY FOR TESTING
    logger = Debug.start_logging()
    crawler = Crawler.Crawler(logger)
    #ScraperDefinitions.WaterSystem.setup_crawler(crawler)
    setup_crawler(crawler)

    scrappy = Scraper.Scraper(logger)
    #ScraperDefinitions.WaterSystem.setup_scraper(scrappy)
    setup_scraper(scrappy, json.loads(instructs), json.loads(pwsids))

    #gecko_path = "/snap/bin/geckodriver"
    #service = webdriver.FirefoxService(executable_path=gecko_path)
    options = webdriver.FirefoxOptions()
    #options.add_argument("-headless")

    #driver = webdriver.Firefox(options=options, service=service)
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    driver.maximize_window() # Small edit to tell Selenium to maximize the window so that it may see all elements on the page.

    # Click the button to navigate to the water system list
    # If the webpage has a JSP button to navigate, this will create a temporary scraper to navigate through the form.
    # if jsp:
    #     temp_scraper = Scraper.Scraper()
    #     temp_scraper.activate_live_mode()
    #     temp_scraper.set_web_driver(driver)
    #     temp_scraper.then_go_back_to_beginning()
    #     temp_scraper.then_skip_to_element_with_attribute("input", "value", "Search For Water Systems")
    
    #     # Small edit to ensure that the scraper moves to the proper web element on the page
    #     actions = ActionChains(driver)
    #     actions.move_to_element(temp_scraper.current_element).perform()

    #     # Small edit to ensure that the scraper will wait until the element is clickable.
    #     WebDriverWait(driver, 1000).until(EC.element_to_be_clickable(temp_scraper.current_element)).click()
    #     #temp_scraper.current_element.click()

    scrappy.set_web_driver(driver)
    crawler.set_web_driver(driver)

    # If the user specifies that the first page is a list of links that needs to be scraper, 
    # if auto_list:
    #     max_items = 5
    #     crawler.set_max_items(max_items + 2)
    #     data = crawler.crawl_and_scrape(scrappy)
    #else:

    data = scrappy.scrape()
    #sleep(50)
    driver.close()

    file = os.path.join('../server/files', "output.json")
    output = open(file, "w") 
    json.dump(data, output, indent=2)
    output.close()
    #clear_logs()
    Debug.end_logging(logger)
    return data

if __name__ == "__main__":
    main(url=sys.argv[1], instructs=sys.argv[2], pwsids=sys.argv[3])