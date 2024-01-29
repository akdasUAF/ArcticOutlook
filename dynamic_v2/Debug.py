#
# Author: Darian Marvel
#
#

should_print_debug = False

import inspect

def debug(string, show_caller = True):
    if should_print_debug:

        if show_caller:
            stack = inspect.stack()
            frame = stack[2][0]
            info = inspect.getframeinfo(frame)

            print("[DEBUG] " + info.function + ":" + info.lineno.__str__() + " " + string)

        else:
            print("[DEBUG] " + string)

def dump_stack():
    if should_print_debug:
        stack = inspect.stack()
        for stack_frame in stack:
            frame = stack_frame[0]
            info = inspect.getframeinfo(frame)

            frame_string = info.function + ":" + info.lineno.__str__()

            debug("at " + frame_string, show_caller = False)
