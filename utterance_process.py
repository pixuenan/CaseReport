#!usr/bin/python
"""
Process the utterance output from MetaMap.
Xuenan Pi
06/01/2016
"""
import re
from utility import clean_mapping_result, label_mapping_result


class UtteranceProcess(object):

    def __init__(self, utterance):
        self.utterance = utterance

        self.vocabulary = {"[popg]": ["[Population Group]", ["CHV", "MSH"]],
                           "[aggp]": ["[Age Group]", ["CHV", "MSH"]],
                           "[dsyn]": ["[Disease or Syndrome]", ["ICD10CM"]],
                           "[neop]": ["[Neoplastic Process]", ["ICD10CM"]],
                           "[sosy]": ["[Sign or Symptom]", ["ICD10CM"]],
                           "[patf]": ["[Pathologic Function]", ["CHV", "ICD10CM"]],
                           "[fndg]": ["[Finding]", ["HPO", "ICD10CM"]],
                           "[mobd]": ["[Mental or Behavioral Dysfunction", ["MSH"]],
                           "[diap]": ["[Diagnostic Procedure]", ["MSH", "CHV"]],
                           "[lbpr]": ["[Laboratory Procedure]", ["MSH", "CHV"]],
                           "[phsu]": ["[Pharmacologic Substance]", ["MSH", "CHV", "RXNORM"]],
                           "[topp]": ["[Therapeutic or Preventive Procedure]", ["CHV", "MSH"]],
                           "[bpoc]": ["[Body Part, Organ, or Organ Component]", ["CHV", "MSH"]]
                           }

        self.needed_keys = ["Concept Name", "Semantic Types", "Sources", "Positional Info"]

    def check_semantic_type(self, semantic_types):
        """Check if the mapping result has semantic types needed."""
        # the semantic types can be multiple types
        semantic_type = False
        if semantic_types in self.vocabulary.keys():
            semantic_type = semantic_types
        elif "," in semantic_types:
            semantic_types_list = ["[%s]" % s_type.strip() for s_type in semantic_types[1:-1].split(",")]
            matched_semantic_type = [s_type for s_type in semantic_types_list if s_type in self.vocabulary.keys()]
            semantic_type = matched_semantic_type and matched_semantic_type[0] or False
        return semantic_type

    def match_source(self, semantic_type, sources):
        required_sources = self.vocabulary[semantic_type][1]
        matched_sources = [source for source in sources if source in required_sources]
        return len(required_sources) == len(matched_sources)

    def match_semantic_types(self, phrase):
        """ Match the semantic type and the correspond sources. Only keep the mapping result
        if the semantic type is in the vocabulary and the sources are also correct."""
        mapping_result = []
        for mapping in phrase[1:]:
            for term in mapping:
                term_dict = dict()
                if term and not int(term["Negation Status"].strip()):
                    semantic_type_needed = self.check_semantic_type(term["Semantic Types"])
                    sources = [source.strip() for source in term["Sources"][1:-1].split(",")]
                    source_matched = semantic_type_needed and self.match_source(semantic_type_needed, sources) or False
                    if source_matched:
                        term["Semantic Types"] = self.vocabulary[semantic_type_needed][0]
                        for key in self.needed_keys:
                            term_dict[key] = term[key]
                # check if the mapping pruned_utterances is already in the dictionary, repetitive
                # mapping case
                if term_dict not in mapping_result and term_dict:
                    mapping_result += [term_dict]
        return mapping_result

    def match(self):
        """ Prune the list of utterances into [[{'Utterance text:'...'},{'text':'...', 'mapping':[{'Concept Name':'...',
        'Semantic Types':'...', 'Sources':'...'}, {}]}, []].
         Only the phrases with mapping pruned_utterances are kept."""

        utterance_unit_list = []
        # the first element of the utterance list is the utterance text
        utterance_dict = dict()
        utterance_dict["Utterance text"] = self.utterance[0][0][0]["Utterance text"]
        utterance_dict["Utterance start index"] = self.utterance[0][0][0]["Position"]
        utterance_unit_list += [utterance_dict]
        for phrase in self.utterance:
            # check if the phrase has mapping result
            if len(phrase) > 1:
                phrase_dict = dict()
                # the first element of the phrase list is the text of the phrase
                phrase_dict["text"] = phrase[0][0]["text"]
                # print phrase
                phrase_dict["mapping"] = self.match_semantic_types(phrase)
                if phrase_dict["mapping"]:
                    utterance_unit_list += [phrase_dict]
        return utterance_unit_list

    def order_terms(self):
        """ Order the mapping terms by their location in the sentence.
        Return: {"Utterance text":,
        "Age":, "Gender":,
        "mapping result": [
        "Time Point", ("Concept Name","Semantic types")]}"""
        result_utterance = dict()
        result_utterance["Utterance text"] = self.utterance[0]["Utterance text"]
        text = self.utterance[0]["Utterance text"]
        print text
        utterance_start = int(self.utterance[0]["Utterance start index"][1:-1].split(",")[0])
        mapping_result = []
        term_index_dict = dict()
        for phrase in self.utterance[1:]:
            if "mapping" in phrase.keys():
                mapping = phrase["mapping"]
                for term in mapping:
                    # age and gender
                    if "Age" in term.keys():
                        result_utterance["Age"] = term["Age"]
                        if "Gender" not in term.keys():
                            result_utterance["Gender"] = "None"
                        else:
                            result_utterance["Gender"] = term["Gender"]
                    # concept term
                    else:
                        # avoid including repetitive mapping result
                        if not term_index_dict.values() or \
                                    term["Concept Name"] not in zip(*term_index_dict.values())[0]:
                            term_start = int(term["Positional Info"][2:-2].split(",")[0])
                            index = term_start - utterance_start
                            term_index_dict[index] = (term["Concept Name"], term["Semantic Types"])
            # time point
            elif "Time Point" in phrase.keys():
                for time in phrase["Time Point"]:
                    index = text.index(time)
                    term_index_dict[index] = (time, "[Time Point]")

        if term_index_dict:
            for key in sorted(term_index_dict.keys()):
                # [[index, (Concept time, Semantic types/Time Point)]]
                mapping_result += [[key, term_index_dict[key]]]

            # clean the mapping result
            mapping_result = clean_mapping_result(mapping_result)
        # label time point to the terms
        if mapping_result:
            # the following function will be replaced by a machine learning function
            label_mapping_result(mapping_result, text)

        result_utterance["mapping_result"] = mapping_result
        return result_utterance



