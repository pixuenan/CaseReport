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
                           "[neop]": ["[Neoplastic Process]", ("ICD10CM")],
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

    def clean_re_mapping(self, mapping_list):
        cleaned_list = []
        for mapping in mapping_list:
            if mapping not in cleaned_list:
                cleaned_list += [mapping]
        return cleaned_list

    def group(self, result_list, break_word):
        """Group the result in the list between the break word together."""
        element_list = []
        element = []
        for result_idx, result in enumerate(result_list):
            if result.strip().startswith(break_word):
                element_list += [element]
                element = []
            elif result_idx == len(result_list) - 1:
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
        """"""
        result_list = self.read_file(input_file)
        # group the result from one sentence together
        grouped_utterance = []
        utterances = self.group(result_list, "Utterance:")
        for utterance in utterances:
            # group the result from one phrase together
            grouped_phrases = []
            phrases = self.group(utterance, "Phrase:")
            for phrase in phrases:
                grouped_mappings = []
                mappings = self.group(phrase, "Map Score:")
                # remove the repetitive mapping result
                for mapping in mappings:
                    terms = self.group(mapping, "Score:")
                    # convert the string into dictionary format
                    grouped_mappings += [[self.convert(term) for term in terms]]
                grouped_phrases += [grouped_mappings]
            grouped_utterance += [grouped_phrases]
        return grouped_utterance

    def prune(self, grouped_utterance):
        """ Prune the list of utterances into [[{'Utterance text:'...'},{'text':'...', 'mapping':[{'Concept Name':'...',
        'Semantic Types':'...', 'Sources':'...'}, {}]}, []].
         Only the phrases with mapping pruned_utterances are kept."""

        pruned_utterances = []
        for utterance in grouped_utterance:
            utterance_unit_list = []
            # the first element of the utterance list is the utterance text
            if "Utterance text" in utterance[0][0][0].keys():
                utterance_dict = dict()
                utterance_dict["Utterance text"] = utterance[0][0][0]["Utterance text"]
                utterance_unit_list += [utterance_dict]
                for phrase in utterance:
                    # check if the phrase has mapping result
                    if len(phrase) > 1:
                        phrase_dict = dict()
                        # the first element of the phrase list is the text of the phrase
                        phrase_dict["text"] = phrase[0][0]["text"]
                        phrase_dict["mapping"] = []
                        for mapping in phrase[1:]:
                            for term in mapping:
                                if term:
                                    term_dict = dict()
                                    for key in self.needed_keys:
                                        term_dict[key] = term[key]
                                    # check if the mapping pruned_utterances is already in the dictionary, repetitive
                                    # mapping case
                                    if term_dict not in phrase_dict["mapping"]:
                                        phrase_dict["mapping"] += [term_dict]
                                        # print phrase_dict
                        utterance_unit_list += [phrase_dict]
                pruned_utterances += [utterance_unit_list]
        return pruned_utterances

    def match_source(self, semantic_types, sources):
        required_sources = self.vocabulary[semantic_types][1]
        source_not_match = False
        for source in required_sources:
            if source not in sources:
                source_not_match = True
        return source_not_match

    def match(self, pruned_utterances):
        """ Further clean the result by match the semantic type and the correspond sources. Only keep the mapping result
        if the semantic type is in the vocabulary and the sources are also correct."""
        for utterance in pruned_utterances:
            phrase_idx = 0
            while phrase_idx < len(utterance[1:]):
                phrase = utterance[1:][phrase_idx]

                mapping_idx = 0
                while mapping_idx < len(phrase["mapping"]):
                    mapping = phrase["mapping"][mapping_idx]
                    if mapping["Semantic Types"] not in self.vocabulary.keys():
                        del phrase["mapping"][mapping_idx]
                    elif self.match_source(mapping["Semantic Types"], mapping["Sources"]):
                        del phrase["mapping"][mapping_idx]
                    else:
                        mapping_idx += 1

                if not phrase["mapping"]:
                    utterance.remove(phrase)
                else:
                    phrase_idx += 1
        return pruned_utterances

if __name__ == "__main__":
    test = MetamapParser()
    print "test"
    # process the case report to group the sentence, phrase and mapping result together
    processed_case = test.process("C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\case1result.txt")
    # turn the processed case from list into dictionary, and only keep the needed field for every mapping result
    pruned_case = test.prune(processed_case)
    matched_case = test.match(pruned_case)
    for i in matched_case:
        for j in i:
            print j
