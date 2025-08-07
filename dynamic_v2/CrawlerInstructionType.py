#
# Author: Darian Marvel
#
#

from enum import Enum

class CrawlerInstructionType(Enum):
    click_element = 0
    skip_to_tag = 1
    skip_to_class = 2
    skip_to_element_with_attribute = 3
    goto_previous_page = 4
