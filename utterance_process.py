#!usr/bin/python
"""
Process the utterance output from MetaMap.
Xuenan Pi
06/01/2016
"""


class UtteranceProcess(object):

    def __init__(self, utterance):
        self.utterance = utterance

        self.vocabulary = {"[popg]": ["[Population Group]", ("CHV", "MSH")],
                           "[aggp]": ["[Age Group]", ("CHV", "MSH")],
                           "[dsyn]": ["[Disease or Syndrome]", ("ICD10CM")],
                           "[neop]": ["[Neoplastic Process]", ("ICD10CM")],
                           "[sosy]": ["[Sign or Symptom]", ("ICD10CM")],
                           "[patf]": ["[Pathologic Function]", ("CHV", "ICD10CM")],
                           "[fndg]": ["[Finding]", ("HPO", "ICD10CM")],
                           "[mobd]": ["[Mental or Behavioral Dysfunction", ("MSH")],
                           "[diap]": ["[Diagnostic Procedure]", ("MSH", "CHV")],
                           "[lbpr]": ["[Laboratory Procedure]", ("MSH", "CHV")],
                           "[phsu]": ["[Pharmacologic Substance]", ("MSH", "CHV", "RXNORM")],
                           "[topp]": ["[Therapeutic or Preventive Procedure]", ("CHV", "MSH")]
                           }

        self.needed_keys = ["Concept Name", "Semantic Types", "Sources"]

    def check_semantic_type(self, semantic_types):
        """Check if the mapping result has semantic types needed."""
        # the semantic types can be multiple types
        semantic_type = False
        if "," in semantic_types:
            semantic_types_list = ["[%s]" % s_type.strip() for s_type in semantic_types[1:-1].split(",")]
            for s_type in semantic_types_list:
                if s_type in self.vocabulary.keys():
                    semantic_type = s_type
                    break
        elif semantic_types in self.vocabulary.keys():
            semantic_type = semantic_types
        return semantic_type

    def match_source(self, semantic_type, sources):
        required_sources = self.vocabulary[semantic_type][1]
        source_not_match = False
        for source in required_sources:
            if source not in sources:
                source_not_match = True
        return source_not_match

    def match(self):
        """ Further clean the result by match the semantic type and the correspond sources. Only keep the mapping result
        if the semantic type is in the vocabulary and the sources are also correct."""
        phrase_idx = 0
        while phrase_idx < len(self.utterance[1:]):
            phrase = self.utterance[1:][phrase_idx]

            mapping_idx = 0
            while mapping_idx < len(phrase["mapping"]):
                mapping = phrase["mapping"][mapping_idx]
                semantic_type_needed = self.check_semantic_type(mapping["Semantic Types"])
                if not semantic_type_needed:
                    del phrase["mapping"][mapping_idx]
                elif self.match_source(semantic_type_needed, mapping["Sources"]):
                    del phrase["mapping"][mapping_idx]
                else:
                    mapping["Semantic Types"] = self.vocabulary[semantic_type_needed][0]
                    mapping_idx += 1

            if not phrase["mapping"]:
                self.utterance.remove(phrase)
            else:
                phrase_idx += 1

    def prune(self):
        """ Prune the list of utterances into [[{'Utterance text:'...'},{'text':'...', 'mapping':[{'Concept Name':'...',
        'Semantic Types':'...', 'Sources':'...'}, {}]}, []].
         Only the phrases with mapping pruned_utterances are kept."""

        utterance_unit_list = []
        # the first element of the utterance list is the utterance text
        utterance_dict = dict()
        utterance_dict["Utterance text"] = self.utterance[0][0][0]["Utterance text"]
        utterance_unit_list += [utterance_dict]
        for phrase in self.utterance:
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
                utterance_unit_list += [phrase_dict]
        self.utterance = utterance_unit_list

    def main(self):
        self.prune()
        self.match()
        return self.utterance



