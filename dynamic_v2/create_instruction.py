from dynamic_v2.ScraperInstructionType import ScraperInstructionType

def setup_scraper(scraper, instructions, pwsids):
    for i in instructions:
        name = i[0]
        params = i[1]
        match name:
            case "skip_to_tag":
                scraper.then_skip_to_element(params[0])
            case "skip_to_class":
                scraper.then_skip_to_class(params[0])
            case "save_value_as_property":
                scraper.then_save_value_as_property(params[0])
            # tag, param
            case "save_attribute_as_property":
                scraper.then_save_attribute_as_property(params[1], params[0])
            case "back_to_beginning":
                scraper.then_go_back_to_beginning()
            # tag, attribute, value
            case "skip_to_element_with_attribute":
                scraper.then_skip_to_element_with_attribute(params[1], params[2], params[3])
            case "click_element":
                scraper.then_click_element()
            case "goto_previous_page":
                scraper.then_go_back()
            case "scrape_table":
                scraper.then_scrape_table(params[0])
            case "run_function":
                scraper.then_run_function(params[0])
            # tag, attribute, value, function_name
            case "for_each":
                scraper.then_for_each(params[1], params[2], params[3], params[4])
            case "create_function":
                scraper.create_function(params[0])
            case "end_function":
                scraper.end_function()
            case "special_for_each":
                scraper.special_for_each(params[0], params[1], params[2], params[3], params[4])
            case "form_send_keys":
                scraper.then_send_keys(params[0], params[1], params[2], params[3])
            case "form_submit":
                scraper.then_form_submit(params[1], params[2], params[3])
            case "delay":
                scraper.then_delay()
            case "save_url":
                scraper.then_save_url(params[0])
            case "check_for_text":
                scraper.then_check_for_text(params[0], params[3])
            case "for_list":
                scraper.then_for_list(pwsids, params[4])
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
