#!usr/bin/python
"""
Process the utterance output from MetaMap.
Xuenan Pi
11/01/2016
"""

import json


class BSONReport(object):
    def __init__(self):
        self.report = dict()
        self.report["Age"] = None
        self.report["Gender"] = None
        self.report["Terms"] = dict()
        self.report["Terms"]["Past"] = None
        self.report["Terms"]["Current"] = None

    def delete_consecutive_repetitive(self):
        """Only delete the consecutive repetitive terms in the current part
        Input: list of [mapped term, semantic types]"""
        idx = 0
        term_list = self.report["Terms"]["Current"]
        while idx < len(term_list) - 1:
            term = term_list[idx]
            if term[0] == term_list[idx + 1][0] and term[1] == term_list[idx + 1][1]:
                term_list.remove(term)
            else:
                idx += 1

    def group_by_semantic_types(self, key):
        """Group the mapped terms by semantic types"""
        term_list = self.report["Terms"][key]
        term_dict = dict()
        for term in term_list:
            past_term = len(term) == 3
            semantic_type = past_term and term[2] or term[1]
            if semantic_type in term_dict:
                term_dict[semantic_type] += past_term and [term[:2]] or [term[0]]
            else:
                term_dict[semantic_type] = [past_term and term[:2] or term[0]]
        self.report["Terms"][key] = term_dict

    def process_utterance(self, utterance):
        if "Age" in utterance.keys():
            self.report["Age"] = utterance["Age"]
        if "Gender" in utterance.keys():
            self.report["Gender"] = utterance["Gender"]
        for term in utterance["mapping result"]:
            if term[0] == "Current":
                self.report["Terms"]["Current"] += [term[1]]
            else:
                self.report["Terms"]["Past"] += [tuple([term[0][1]] + list(term[1]))]

        self.delete_consecutive_repetitive()

    def generate_report(self, processed_case, output_file_name):
        output_file = open(output_file_name, "w+")
        self.report["Terms"]["Past"] = []
        self.report["Terms"]["Current"] = []
        for utterance in processed_case:
            self.process_utterance(utterance)
        self.group_by_semantic_types("Current")
        self.group_by_semantic_types("Past")
        output_file.write(json.dumps(self.report, indent=4))
        output_file.close()
