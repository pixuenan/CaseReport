#!usr/bin/python
"""
Process the utterance output from MetaMap.
Xuenan Pi
11/01/2016
"""

import json

class BSON_report(object):

    def __init__(self):
        self.report = dict()
        self.report["Age"] = None
        self.report["Gender"] = None
        self.report["Terms"] = dict()
        self.report["Terms"]["Past"] = []
        self.report["Terms"]["Current"] = []

    def delete_consecutive_repetitive(self):
        """Only delete the consecutive repetitive terms in the current part
        Input: list of [mapped term, semantic types]"""
        idx = 0
        term_list = self.report["Terms"]["Current"]
        while idx < len(term_list)-1:
            term = term_list[idx]
            if term[0] == term_list[idx+1][0] and term[1] == term_list[idx+1][1]:
                term_list.remove(term)
            else:
                idx += 1

    def process_utterance(self, utterance):
        if "Age" in utterance.keys():
            self.report["Age"] = utterance["Age"]
        if "Gender" in utterance.keys():
            self.report["Gender"] = utterance["Gender"]
        for term in utterance["mapping_result"]:
            if term[0] == "Current":
                self.report["Terms"]["Current"] += [term[1]]
            else:
                self.report["Terms"]["Past"] += [tuple([term[0][1]]+list(term[1]))]

        self.delete_consecutive_repetitive()

    def generate_report(self, processed_case):
        for utterance in processed_case:
            self.process_utterance(utterance)
        print json.dumps(self.report)








