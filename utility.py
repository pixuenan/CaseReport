#!usr/bin/python
"""
Utility functions.
Xuenan Pi
06/10/2017
"""


def index_in_the_list(result_list, text):
    """ Return the index of the regex result in the text."""
    index_list = []
    for result in result_list:
        index = text.index(result)
        index_list += [index]
    return index_list
