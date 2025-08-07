import json
from dynamic_v2.ScraperInstructionType import ScraperInstructionType

# si.instructions.append((ScraperInstructionType(int(i)).name, params, si.instruct_num, instruct_name, notes))
# params = [param, tag, attribute, value, function_name]
def generate_list(instructions=None, functions=None):
    instr = json.loads(instructions)
    #func = json.loads(functions)
    instructs = []
    
    # get the scraper name + remove last item in list (scraper name)
    url = instr[-1]['url']
    instr.pop()
    name = instr[-1]['scraper_name']
    instr.pop()
    num = 0
    for funcs in functions:
        funcs.pop()
        f, num = instruct_pipeline(funcs, num)
        instructs.extend(f)
    # remove last item of function list
    # if func:
    #     func.pop()
    #     f, num = instruct_pipeline(func, num)
    #     instructs.extend(f)

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
                params = [contents[0]["contents"], "", "", "", "", contents[1]["contents"]]
                instructs.append((index, params, num, name, ""))
            case "skip_to_class":
                params = [contents[0]["contents"], "", "", "", "", contents[1]["contents"]]
                instructs.append((index, params, num, name, ""))
            case "save_value_as_property":
                params = [contents[0]["contents"], "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "save_attribute_as_property": 
                params = [contents[0]["contents"], contents[1]["contents"], "", "", "", contents[2]["contents"]]
                instructs.append((index, params, num, name, ""))
            case "back_to_beginning":
                params = ["", "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "skip_to_element_with_attribute":
                params = ["", contents[0]["contents"], contents[1]["contents"], contents[2]["contents"], "", contents[3]["contents"]]
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
                params = ["", contents[0]["contents"], contents[1]["contents"], contents[2]["contents"], contents[3]["contents"]]
                instructs.append((index, params, num, name, ""))
            case "create_function":
                params = [contents[0]["contents"], "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "end_function":
                params = ["", "", "", "", ""]
                instructs.append((index, params, num, name, ""))
            case "special_for_each":
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
