#
# Author: Darian Marvel
#
#

from enum import Enum

class ScraperInstructionType(Enum):
    skip_to_tag = 1
    skip_to_class = 2
    save_value_as_property = 3
    save_attribute_as_property = 4
    back_to_beginning = 5
    skip_to_element_with_attribute = 6
    click_element = 7
    goto_previous_page = 8
    scrape_table = 9
    run_function = 10
    for_each = 11
    create_function = 12
    end_function = 13
