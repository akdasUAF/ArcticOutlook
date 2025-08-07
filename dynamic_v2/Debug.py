#
# Author: Darian Marvel
#
#

should_print_debug = True
import logging, colorlog
from colorlog import ColoredFormatter
import inspect
from pathlib import Path

class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level

def start_logging():
    logging.basicConfig(filename='./logs/dev.log', encoding='utf-8', level=logging.DEBUG)
    logger = logging.getLogger('logger')
    VALUE = 17
    SCRAPER = 16
    CRAWLER = 15
    logging.addLevelName(VALUE, 'VALUE SAVED')
    logging.addLevelName(SCRAPER, 'SCRAPER')
    logging.addLevelName(CRAWLER, 'CRAWLER')
    formatter = ColoredFormatter(
        "%(asctime)s - %(log_color)s[%(levelname)s] - %(log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
            'VALUE SAVED': 'bold_blue',
            'SCRAPER': 'black',
            'CRAWLER': 'purple'
        },
        secondary_log_colors={},
        style='%'
    )

    user_handler = logging.FileHandler("./logs/usr.log", mode="w")
    user_handler.setLevel(logging.DEBUG)
    logger.addHandler(user_handler)

    dev_handler = logging.FileHandler("./logs/job.log")
    dev_handler.setLevel(logging.ERROR) 
    logger.addHandler(dev_handler)

    logger.setLevel(logging.DEBUG)

    user_handler.addFilter(MyFilter(VALUE))
    user_handler.setFormatter(formatter)
    dev_handler.addFilter(MyFilter(logging.ERROR))
    return logger

def end_logging(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)

    logging.shutdown()

def debug(string, logger, log_lvl, show_caller = True):
    if should_print_debug:

        if show_caller:
            stack = inspect.stack()
            frame = stack[2][0]
            info = inspect.getframeinfo(frame)
            # TODO: Write to log file so it can then be read to a user
            #print("[DEBUG] " + info.function + ":" + info.lineno.__str__() + " " + string)
            #logger.debug("[DEBUG] " + info.function + ":" + info.lineno.__str__() + " " + string)
            match log_lvl:
                case 10: logger.debug(string)       # DEBUG
                case 17: logger.log(17, string)     # VALUE SAVED
                case 16: logger.log(16, string)     # SCRAPER
                case 15: logger.log(15, string)     # CRAWLER

        else:
            #print("[DEBUG] " + string)
            #logger.debug("[DEBUG] " + string)
            logger.debug(string)

def dump_stack():
    if should_print_debug:
        stack = inspect.stack()
        for stack_frame in stack:
            frame = stack_frame[0]
            info = inspect.getframeinfo(frame)

            frame_string = info.function + ":" + info.lineno.__str__()

            debug("at " + frame_string, show_caller = False)
