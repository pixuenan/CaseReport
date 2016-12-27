#!usr/bin/python
"""
Parse the result from MetaMap.
Xuenan Pi
23/12/2016
"""


class MetamapParser:
    def __init__(self):
        # the vocabulary to mined out the terms, key is abbreviation, value is name and source
        # if and only if both sources are in the result sources, the term will be extracted
        self.vocabulary = {"[popg]": ["[Population Group]", ("CHV", "MSH")],
                           "[dsyn]": ["[Disease or Syndrome]", ("ICD10CM")],
                           "[neop]": ["[Neoplastic Process]", ("HPO", "ICD10CM")],
                           "[sosy]": ["[Sign or Symptom]", ("ICD10CM")],
                           "[patf]": ["[Pathologic Function]", ("CHV", "ICD10CM")],
                           "[fndg]": ["[Finding]", ("HPO", "ICD10CM")],
                           "[mobd]": ["[Mental or Behavioral Dysfunction", ("MSH")],
                           "[diap]": ["[Diagnostic Procedure]", ("MSH", "CHV")],
                           "[lbpr]": ["[Laboratory Procedure]", ("MSH", "CHV")],
                           "[phsu]": ["[Pharmacologic Substance]", ("RXNORM")],
                           "[topp]": ["[Therapeutic or Preventive Procedure]", ("CHV", "MSH")]
                           }

        # the needed keys in every mapping result
        self.needed_keys = ["Concept Name", "Semantic Types", "Sources"]

    def read_file(self, input_file):
        file_content = open(input_file)
        result_list = file_content.readlines()
        file_content.close()
        return result_list

    def group(self, result_list, break_word):
        """Group the result in the list between the break word together."""
        element_list = []
        element = []
        for result_idx, result in enumerate(result_list):
            if result.strip().startswith(break_word):
                element_list += [element]
                element = []
            elif result_idx == len(result_list)-1:
                element += [result.strip()]
                element_list += [element]
            else:
                element += [result.strip()]
        return element_list

    def convert(self, element):
        """Convert the element string "Id: 1" to dictionary {"Id": "1"}."""
        element_dict = {}
        for item in element:
            item_key, item_value = item.split(':')
            element_dict[item_key] = item_value.strip()
        return element_dict

    def process(self, input_file):
        result_list = self.read_file(input_file)
        # group the result from one sentence together
        utterances = self.group(result_list, "Utterance:")
        grouped_utterance = []
        for utterance in utterances:
            # group the result from one phrase together
            grouped_phrases = []
            phrases = self.group(utterance, "Phrase:")
            for phrase in phrases:
                mappings = self.group(phrase, "Mappings:")
                # convert the string into dictionary format
                grouped_phrases += [[self.convert(mapping) for mapping in mappings]]
            grouped_utterance += [[grouped_phrases]]
        return grouped_utterance

if __name__ == "__main__":
    test = MetamapParser()
    print "test"
    # process the case report to group the sentence, phrase and mapping result together
    processed_case = test.process("C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\resulttest.txt")

