#!usr/bin/python
"""
Parse the result from MetaMap.
Xuenan Pi
23/12/2016
"""


class MetamapParser:
    def __init__(self):
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

    def read_file(self, input_file):
        file_content = open(input_file)
        result_list = file_content.readlines()
        file_content.close()
        return result_list

    def group(self, result_list, break_word):
        """Group the result in the list between the break word together."""
        utterance_list = []
        utterance = []
        for result_idx, result in enumerate(result_list):
            if result.strip().startswith(break_word):
                utterance_list += [utterance]
                utterance = []
            elif result_idx == len(result_list)-1:
                utterance += [result.strip()]
                utterance_list += [utterance]
            else:
                utterance += [result.strip()]
        return utterance_list

    def convert(self, utterance_list):
        """Convert the utterance string "Id: 1" to dictionary {"Id": "1"}."""
        list_utterance_dict = []
        for utterance in utterance_list:
            utterance_dict = {}
            for item in utterance:
                item_key, item_value = item.split(':')
                utterance_dict[item_key] = item_value.strip()
            if len(utterance_dict) != len(utterance):
                print "+++:"
                print utterance
                print "---:"
                print utterance_dict
            list_utterance_dict += utterance_dict
        return list_utterance_dict

    # def process(self, input_file):
    #     result_list = self.read_file(input_file)
    #     # group the result from one sentence together
    #     utterances = self.group(result_list, "Utterance:")
    #     processed = []
    #     for utterance in utterances:
    #         # group the result from one phrase together
    #         phrases = self.group(utterance, "Phrase:")
    #         # print phrases
    #         list_phrase_dict = []
    #         for phrase in phrases:
    #             print phrase
    #             # convert the result string into dictionary
    #             list_phrase_dict += [self.convert(phrase)]
    #         processed += [list_phrase_dict]
    #     print "final"
    #     for i in processed:
    #         print i

    def process(self, input_file):
        result_list = self.read_file(input_file)
        # group the result from one sentence together
        utterances = self.group(result_list, "Utterance:")
        processed = []
        for utterance in utterances:
            # group the result from one phrase together
            phrases = self.group(utterance, "Phrase:")
            # print phrases
            # print "+++++++"
            # print self.convert(phrases)
            # print "======="
            processed += [self.convert(phrases)]

if __name__ == "__main__":
    test = MetamapParser()
    print "test"
    test.process("C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\case1result.txt")

