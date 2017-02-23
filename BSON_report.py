#!usr/bin/python
"""
Process the utterance output from MetaMap.
Xuenan Pi
11/01/2016
"""

import json


class BSONReport(object):
    def __init__(self, test=False):
        self.test = test
        self.report = dict()
        self.report["Age"] = None
        self.report["Gender"] = None
        self.report["Terms"] = dict()
        self.report["Terms"]["Past"] = None
        self.report["Terms"]["Current"] = None

    def delete_repetitive(self, time_section):
        """ Delete the repetitive terms in the report
        Input: list of [mapped term, semantic types]"""
        for semantic_type in self.report["Terms"][time_section].keys():
            concept_list = self.report["Terms"][time_section][semantic_type]
            self.report["Terms"][time_section][semantic_type] = list(set(concept_list))

    def group_by_semantic_types(self, key):
        """Group the mapped terms by semantic types"""
        term_list = self.report["Terms"][key]
        term_dict = dict()
        for term in term_list:
            semantic_type = term[2]
            if semantic_type in term_dict:
                if self.test:
                    term_dict[semantic_type] += [term[0] and tuple(term[:2]+[term[-1]]) or tuple([term[1]]+[term[-1]])]
                else:
                    term_dict[semantic_type] += [term[0] and tuple(term[:2]) or tuple([term[1]])]
            else:
                if self.test:
                    term_dict[semantic_type] = [term[0] and tuple(term[:2]+[term[-1]]) or tuple([term[1]]+[term[-1]])]
                else:
                    term_dict[semantic_type] = [term[0] and tuple(term[:2]) or tuple([term[1]])]
        self.report["Terms"][key] = term_dict

    def process_utterance(self, utterance):
        """ Term output: {"Current": [("5 days later", "Edema", "[Finding]"), (0, "Edema", "[Finding]")],
                          "Past:[]"}"""
        if "Age" in utterance.keys():
            self.report["Age"] = utterance["Age"]
        if "Gender" in utterance.keys():
            self.report["Gender"] = utterance["Gender"]
        for term in utterance["mapping result"]:
            if term[0][0] == "Current":
                self.report["Terms"]["Current"] += [[term[0][1]] + list(term[1])]
            else:
                self.report["Terms"]["Past"] += [[term[0][1]] + list(term[1])]

    def generate_report(self, processed_case, output_file_name):
        output_file = open(output_file_name, "w+")
        self.report["Terms"]["Past"] = []
        self.report["Terms"]["Current"] = []
        for utterance in processed_case:
            self.process_utterance(utterance)
        self.group_by_semantic_types("Current")
        self.group_by_semantic_types("Past")
        self.delete_repetitive("Current")
        self.delete_repetitive("Past")
        output_file.write(json.dumps(self.report, indent=4))
        output_file.close()
