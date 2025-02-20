import json
from dynamic_v2.ScraperInstructionType import ScraperInstructionType

# si.instructions.append((ScraperInstructionType(int(i)).name, params, si.instruct_num, instruct_name, notes))
# params = [param, tag, attribute, value, function_name]
def generate_list(instructions=None, functions=None):
    instr = json.loads(instructions)
    func = json.loads(functions)
    instructs = []
    
    # get the scraper name + remove last item in list (scraper name)
    url = instr[-1]['url']
    instr.pop()
    name = instr[-1]['scraper_name']
    instr.pop()
    num = 0
    # remove last item of function list
    if func:
        func.pop()
        f, num = instruct_pipeline(func, num)
        instructs.extend(f)

    # add functions to pipeline first, then add main scrape
    i, num = instruct_pipeline(instr, num)
    instructs.extend(i)
    return instructs, name, url

# Need to move functionality in here for recursive list generation
def instruct_pipeline(lst, num=0):
    instructs = []
    num = num
    for ls in lst:
        index = ls["id"]
        name = ls["name"]
        contents = ls["contents"]
        subs = ls["subs"]
        s = index.split('-')
        index = s[2]
        match(index):
            case "skip_to_tag":
                params = [contents[0]["contents"], "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "skip_to_class":
                params = [contents[0]["contents"], "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "save_value_as_property":
                params = [contents[0]["contents"], "", "", "", ""]
                print(params)
                instructs.append((index, params, num, name, ""))
            case "save_attribute_as_property":
                params = [contents[0]["contents"], contents[1]["contents"], "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "back_to_beginning":
                params = ["", "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "skip_to_element_with_attribute":
                params = ["", contents[0]["contents"], contents[1]["contents"], contents[2]["contents"], ""]
                instructs.append((index, params, num, name, ""))
            case "click_element":
                params = ["", "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "goto_previous_page":
                params = ["", "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "scrape_table":
                params = [contents[0]["contents"], "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "run_function":
                params = [contents[0]["contents"], "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "for_each":
                params = ["", contents[1]["contents"], contents[2]["contents"], contents[3]["contents"], contents[4]["contents"]]
                instructs.append((index, params, num, name, ""))
            case "create_function":
                params = [contents[0]["contents"], "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "end_function":
                params = ["", "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "special_for_each":
                print(contents)
                params = [contents[0]["contents"], contents[1]["contents"], contents[2]["contents"], contents[3]["contents"], contents[4]["contents"], contents[5]["contents"]]
                instructs.append((index, params, num, name, ""))
            case "form_send_keys":
                params = [contents[0]["contents"], contents[1]["contents"], contents[2]["contents"], contents[3]["contents"], ""]
                instructs.append((index, params, num, name, ""))
            case "form_submit":
                params = ["", contents[0]["contents"], contents[1]["contents"], contents[2]["contents"], ""]
                instructs.append((index, params, num, name, ""))
            case "delay":
                params = ["", "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "save_url":
                params = [contents[0]["contents"], "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "check_for_text":
                params = [contents[0]["contents"], "", "", contents[3]["contents"], ""]
                instructs.append((index, params, num, name, ""))
            case "for_list":
                params = [contents[0]["contents"], "", "", contents[3]["contents"], ""]
                instructs.append((index, params, num, name, ""))
        num += 1
        if subs:
            sub_steps, num = instruct_pipeline(subs, num)
            instructs.extend(sub_steps)
    return instructs, num

    # loop through functions first
    # if no end function, add one to end of children of parent function
    # then loop through scrape instructions
    # may need an additional helper recursive function to get all of kids
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
                scraper.special_for_each(params[0], params[1], params[2], params[3], params[4], params[5])
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
