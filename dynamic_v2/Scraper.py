#
# Author: Darian Marvel
#
#

import dynamic_v2.Debug as Debug
from dynamic_v2.ScraperInstructionType import ScraperInstructionType

from time import sleep
import time
from selenium.common import StaleElementReferenceException
from selenium.common import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select


# PSEUDOCODE Usage
#
# Scraper scrappy
# scrappy.thenSkipToClass( ".something-after-the-header" )
# scrappy.thenSkipToElement( "p" )
# scrappy.thenSelectElement( "p" ) # This would be the first "p" element after the one we just skipped to
# scrappy.thenSaveValueAsProperty( "employee.name" )
# scrappy.thenScrapeTable( "employee.contactInfo" )
#
# JsonData data = scrappy.scrape( HTML_Feeder_or_something )

class Scraper(object):

    def __init__(self):
        self.instructions = []
        self.current_element = None
        self.data = dict()
        self.functions = dict()
        self.function_writing = None
        self.live_mode = False
        self.webdriver = None
        self.max_items = 50
        self.loop_list = False
        self.curr_list_item = None

    def set_web_driver(self, webdriver):
        self.webdriver = webdriver

    def activate_live_mode(self):
        self.live_mode = True

    def deactivate_live_mode(self):
        self.live_mode = False

    @staticmethod
    def __debug(param):
        Debug.debug("[SCRAPER] " + param.__str__())

    def back_to_beginning(self):
        self.current_element = self.webdriver.find_element(By.TAG_NAME, "html")

    @staticmethod
    def is_after(element, other_element):
        if other_element.location.get('y') < element.location.get('y'):
            return False
        if other_element.location.get('y') > element.location.get('y'):
            return True
        if other_element.location.get('x') > element.location.get('x'):
            return True

    @staticmethod
    def is_before(element, other_element):
        if other_element.location.get('y') > element.location.get('y'):
            return False
        if other_element.location.get('y') < element.location.get('y'):
            return True
        if other_element.location.get('x') < element.location.get('x'):
            return True

    def next_closest_element_in_list(self, elems):
        self.__debug("next_closest_element_in_list")
        closest = self.current_element
        for elem in elems:
            if closest is self.current_element:
                if self.is_after(self.current_element, elem):
                    closest = elem
            else:
                if self.is_after(self.current_element, elem) and self.is_before(closest, elem):
                    closest = elem
        return closest

    def next_closest_element_in_list_with_attribute_and_value(self, elems, attribute, value):
        self.__debug("next_closest_element_in_list_with_attribute_and_value")
        closest = self.current_element

        if attribute is None or value is None:
            for elem in elems:
                if closest is self.current_element and self.is_after(self.current_element, elem):
                    closest = elem
                elif self.is_after(self.current_element, elem) and self.is_before(closest, elem):
                    closest = elem
        else:
            for elem in elems:
                if closest is self.current_element and self.is_after(self.current_element, elem) and elem.get_attribute(attribute) == value:
                    closest = elem
                elif self.is_after(self.current_element, elem) and self.is_before(closest, elem) and elem.get_attribute(attribute) == value:
                    closest = elem

            if closest is self.current_element or closest.get_attribute(attribute) != value:
                # Didn't really find a match - set back to current element before return
                closest = self.current_element

        return closest

    def get_instructions(self):
        return self.instructions

    def get_data(self):
        return self.data

    def create_function(self, param):
        self.functions[param] = []
        self.function_writing = param

        self.__debug("Now writing function " + self.function_writing)

    def end_function(self):
        if self.function_writing is not None:
            self.__debug("Ending function " + self.function_writing)
        self.function_writing = None

    def handle_instruction(self, param):
        self.__debug("Handling instruction \"" + param.__str__() + "\"")

        if self.function_writing is not None:
            self.functions[self.function_writing].append(param)
        elif self.live_mode:
            self.execute_instruction(self.data, param)
        else:
            self.instructions.append(param)

    def then_for_each(self, tag, attribute, value, function_name):
        instruction = [ScraperInstructionType.for_each, tag, attribute, value, function_name]
        self.handle_instruction(instruction)

    def then_for_list(self, parameter, function_name):
        instruction = [ScraperInstructionType.for_list, parameter, function_name]
        self.handle_instruction(instruction)

    def then_run_function(self, param):
        instruction = [ScraperInstructionType.run_function, param]
        self.handle_instruction(instruction)

    def then_skip_to_class(self, param):
        instruction = [ScraperInstructionType.skip_to_class, param]
        self.handle_instruction(instruction)

    def then_skip_to_element(self, param):
        instruction = [ScraperInstructionType.skip_to_tag, param]
        self.handle_instruction(instruction)

    def then_save_value_as_property(self, param):
        instruction = [ScraperInstructionType.save_value_as_property, param]
        self.handle_instruction(instruction)

    def then_save_attribute_as_property(self, tag, param):
        instruction = [ScraperInstructionType.save_attribute_as_property, tag, param]
        self.handle_instruction(instruction)

    def then_go_back_to_beginning(self):
        instruction = [ScraperInstructionType.back_to_beginning]
        self.handle_instruction(instruction)

    def then_skip_to_element_with_attribute(self, tag, attribute, value):
        instruction = [ScraperInstructionType.skip_to_element_with_attribute, tag, attribute, value]
        self.handle_instruction(instruction)

    def then_click_element(self):
        instruction = [ScraperInstructionType.click_element]
        self.handle_instruction(instruction)

    def then_go_back(self):
        instruction = [ScraperInstructionType.goto_previous_page]
        self.handle_instruction(instruction)

    def set_current_element(self, element):
        self.current_element = element
        self.__debug("Current element is now at " + self.current_element.location.__str__())

    def then_scrape_table(self, param):
        instruction = [ScraperInstructionType.scrape_table, param]
        self.handle_instruction(instruction)

    def scrape_table(self):
        rows = self.current_element.find_elements(By.TAG_NAME, "tr")
        if len(rows) < 1:
            return None
        header_row = rows[0]
        columns = header_row.find_elements(By.TAG_NAME, "th")
        names = []
        row_dictionary_list = []
        for column in columns:
            names.append(column.get_attribute("innerText"))

        for row in rows[1:]:
            row_dictionary = dict()
            row_values = row.find_elements(By.TAG_NAME, "td")
            for index, column_value in enumerate(row_values):
                row_dictionary[names[index]] = column_value.get_attribute("innerText")

            row_dictionary_list.append(row_dictionary)

        self.__debug(names.__str__())
        self.__debug(row_dictionary_list.__str__())
        return row_dictionary_list
    
    def then_send_keys(self, parameter, tag, attribute, value):
        instruction = [ScraperInstructionType.form_send_keys, tag, attribute, value, parameter]
        self.handle_instruction(instruction)
    
    def then_form_submit(self, tag, attribute, value):
        # Instruction type, 
        instruction = [ScraperInstructionType.form_submit, tag, attribute, value]
        self.handle_instruction(instruction)
    
    def then_delay(self):
        instruction = [ScraperInstructionType.delay]
        self.handle_instruction(instruction)

    def then_save_url(self, parameter):
        # save url under name
        instruction = [ScraperInstructionType.save_url, parameter]
        self.handle_instruction(instruction)
    
    def then_check_for_text(self, parameter, value):
        # parameter => specific text
        instruction = [ScraperInstructionType.check_for_text, parameter, value]
        self.handle_instruction(instruction)
    
    # WIP: Instruction to scrape a table of links / perform action on subpages?
    def create_selector_for_element_in_list(self, i, start_ele, tag, sub_tag):
        return start_ele + " " + tag + ":nth-of-type(" + i.__str__() + ") " + sub_tag

    def special_for_each(self, param, tag, attribute, value, function_name, r):
        instruction = [ScraperInstructionType.special_for_each, param, tag, attribute, value, function_name, r]
        self.handle_instruction(instruction)

    def scroll_to_current_element(self):
        self.webdriver.execute_script("arguments[0].scrollIntoView();", self.current_element)
        WebDriverWait(self.webdriver, .5)
        
    def wait_for_visibility(self, selector_type, selector):
        return WebDriverWait(self.webdriver, 20).until(EC.visibility_of_element_located((selector_type, selector)))

    def scrape(self):
        self.__debug("Scraping...")
        self.back_to_beginning()
        self.data = {}
        for instruction in self.instructions:

            self.execute_instruction(self.data, instruction)

        return self.data

    def execute_function(self, name, data):
        instructions = self.functions[name]
        self.__debug("Running function " + name)
        for instr in instructions:
            self.__debug("Function " + name + " executing " + instr.__str__())
            self.execute_instruction(data, instr)
        time.sleep(2)

    def check_if_list(self, instruction):
        self.__debug("Checking for $list...")
        instr = instruction
        for x, i in enumerate(instruction):
            if i == "$list":
                instr = list(instruction)
                self.__debug("$list replaced with " + self.curr_list_item)
                instr[x] = self.curr_list_item
        self.__debug(instr)
        return instr

    def execute_instruction(self, data, instruction):
        self.__debug("Running instruction: " + instruction.__str__())
        
        time_start = time.time()

        if self.loop_list:
            instruction = self.check_if_list(instruction)

        if instruction[0] is ScraperInstructionType.skip_to_class:
            self.set_current_element(self.next_closest_element_in_list(self.webdriver.find_elements(By.CLASS_NAME, instruction[1])))

        if instruction[0] is ScraperInstructionType.skip_to_tag:
            self.set_current_element(self.next_closest_element_in_list(self.webdriver.find_elements(By.TAG_NAME, instruction[1])))

        if instruction[0] is ScraperInstructionType.save_value_as_property:
            data[instruction[1]] = self.current_element.get_attribute('innerText')

        if instruction[0] is ScraperInstructionType.save_attribute_as_property:
            data[instruction[2]] = self.current_element.get_attribute(instruction[1])

        if instruction[0] is ScraperInstructionType.back_to_beginning:
            self.back_to_beginning()

        if instruction[0] is ScraperInstructionType.skip_to_element_with_attribute:
            selector = instruction[1] + "[" + instruction[2] + "='" + instruction[3] + "']"
            self.__debug(selector)
            elements = self.webdriver.find_elements(By.CSS_SELECTOR, selector)
            self.set_current_element(self.next_closest_element_in_list_with_attribute_and_value(elements, instruction[2], instruction[3]))

        if instruction[0] is ScraperInstructionType.click_element:
            actions = ActionChains(self.webdriver)
            actions.move_to_element(self.current_element).perform()
            for j in range(3):
                try:
                    #self.current_element.click()
                    WebDriverWait(self.webdriver, 1000).until(EC.element_to_be_clickable(self.current_element)).click()
                    break
                except ElementNotInteractableException:
                    # Sleep for a moment and try again
                    # This exception can be thrown if the web browser doesn't
                    # scroll down to the element fast enough
                    sleep(0.25)

            self.back_to_beginning()

        if instruction[0] is ScraperInstructionType.goto_previous_page:
            #self.webdriver.back()
            self.webdriver.execute_script("window.history.go(-1)")
            self.back_to_beginning()

        if instruction[0] is ScraperInstructionType.scrape_table:
            data[instruction[1]] = self.scrape_table()

        if instruction[0] is ScraperInstructionType.run_function:
            self.execute_function(instruction[1], data)

        if instruction[0] is ScraperInstructionType.for_each:
            selector = instruction[1] + "[" + instruction[2] + "='" + instruction[3] + "']"
            self.__debug(selector)
            elements = self.webdriver.find_elements(By.CSS_SELECTOR, selector)
            objects = []
            for index, val in enumerate(elements):
                elements = self.webdriver.find_elements(By.CSS_SELECTOR, selector)

            #for elem in elements:
                item = dict()
                self.set_current_element(elements[index])
                self.execute_function(instruction[4], item)
                objects.append(item)

            data[instruction[4]] = objects
        
        if instruction[0] is ScraperInstructionType.special_for_each:
            # user passes css selector for 1st item
            # change end of css selector to be enumerated
            # keep the rest, should work
            selector = instruction[2] + "[" + instruction[3] + "='" + instruction[4] + "']"
            self.__debug(selector)
            # elements = self.webdriver.find_elements(By.CSS_SELECTOR, selector)
            objects = []
            if instruction[6]:
                split_range = instruction[6].split(':')
                min_range = int(split_range[0])
                max_range = int(split_range[1])
                if not min_range:
                    min_range = 0
                if not max_range:
                    max_range = self.max_items

            else:
                max_range = self.max_items
                min_range = 0
                
            for i in range(min_range, max_range):
                #print("Loop")
                #print(f"{i}, {instruction[1]}, {instruction[2]}, {instruction[3]}, {instruction[4]}, {instruction[5]}, {instruction[6]} ")
                # table tr:nth-of-type(0) a
                # #ctl00_ContentPlaceHolder1_pnlContent > a:nth-child(3)
                # div.row:nth-child(5) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)
                # div.row:nth-child(5) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(1) > a:nth-child(1)
                # iterator, parent_selector, tag
                selector = self.create_selector_for_element_in_list(i, instruction[1], instruction[2], instruction[3])
                # - .col-md-12 > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > a:nth-child(1)
                # .col-md-12 > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(1) > a:nth-child(1)
                #print(selector)
                try:
                    elem = self.webdriver.find_element(By.CSS_SELECTOR, selector)
                    item = dict()
                    self.set_current_element(elem)
                    self.execute_function(instruction[5], item)
                    objects.append(item)
                except:
                    continue

            data[instruction[4]] = objects
        
        if instruction[0] is ScraperInstructionType.form_send_keys:
            # Set our webdriver to look at current element
            selector = instruction[1] + "[" + instruction[2] + "='" + instruction[3] + "']"
            self.__debug(selector)
            if self.wait_for_visibility(By.CSS_SELECTOR, selector):
                elements = self.webdriver.find_elements(By.CSS_SELECTOR, selector)
                self.set_current_element(self.next_closest_element_in_list_with_attribute_and_value(elements, instruction[2], instruction[3]))
                
                self.scroll_to_current_element()

                # TODO: If there are more form options, implement them
                if instruction[1] == 'select':
                    select = Select(self.current_element)
                    WebDriverWait(self.webdriver, 15).until(EC.element_to_be_clickable(self.current_element))
                    select.select_by_value(instruction[4])
                else:
                    if instruction[4] == 'Keys.BACKSPACE':
                        self.current_element.send_keys(Keys.COMMAND + 'a')
                        self.current_element.send_keys(Keys.BACKSPACE)
                    else:
                        self.current_element.send_keys(instruction[4])

        if instruction[0] is ScraperInstructionType.form_submit:
            selector = instruction[1] + "[" + instruction[2] + "='" + instruction[3] + "']"
            self.__debug(selector)
            elements = self.webdriver.find_elements(By.CSS_SELECTOR, selector)
            self.set_current_element(self.next_closest_element_in_list_with_attribute_and_value(elements, instruction[2], instruction[3]))
            self.scroll_to_current_element()
            self.current_element.click()
            self.back_to_beginning()
        
        if instruction[0] is ScraperInstructionType.delay:
            # TODO: Allow user to set the delay 
            WebDriverWait(self.webdriver, 5)

        if instruction[0] is ScraperInstructionType.save_url:
            data[instruction[1]] = self.webdriver.current_url

        if instruction[0] is ScraperInstructionType.check_for_text:
            # temp hardcode so if text exists, save url
            time.sleep(2)
            if instruction[1] not in self.webdriver.page_source:
                data[instruction[2]] = self.webdriver.current_url

        if instruction[0] is ScraperInstructionType.for_list:
            objects = []
            self.loop_list = True
            for pwsid in instruction[1]:
                self.__debug("Executing function with item: " + pwsid)
                item = dict()
                self.curr_list_item = pwsid
                self.execute_function(instruction[2], item)
                objects.append(item)

            data[instruction[2]] = objects
            self.loop_list = False

        time_end = time.time()
        self.__debug("Executed instruction in " + (time_end - time_start).__str__() + " seconds: " + instruction.__str__())

