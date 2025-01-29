"""
This module contains the class to measure and manipulate the time taken by a code block
"""

import time


class Stopwatch:
    """
    Class to measure the time taken by a code block to execute and log it

    For example:

    with Stopwatch(desc="Sleep", verbose=True):
        time.sleep(2)
    """

    def __init__(self, desc=None, verbose=True):
        self.desc = desc
        self.verbose = verbose

        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        end_time = time.time()
        elapsed_time = end_time - self.start_time

        if self.verbose:
            description = self.desc

            log_list = []

            if description:
                log_list.append(description)
            log_list.append(f"Exec time {round(1000 * elapsed_time)} ms")

            print(". ".join(log_list))


# class TimeDeceleration:
#     """
#     Class to slow down the execution of a code block by adding a delay between each line of code
#
#     For example: (Remove the backslashes before the quotes)
#
#     with TimeDeceleration(delay=0.5) as td:
#         td(\"""
#         print("Hello")
#         print("World")
#         \""")
#     """
#     def __init__(self, delay=0.5):
#         self.delay = delay
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc_value, traceback):
#         pass
#
#     def __call__(self, code_block):
#         lines = code_block.strip().split('\n')
#         for line in lines:
#             eval(line)
#             time.sleep(self.delay)
