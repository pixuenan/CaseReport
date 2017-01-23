#!usr/bin/python
"""
Process the utterance output from MetaMap.
Xuenan Pi
06/01/2016
"""

import ast

class UtteranceProcess(object):

    def __init__(self, utterance):
        self.utterance = utterance

        self.vocabulary = {"[popg]": ["[Population Group]", ["CHV", "MSH"]],
                           "[aggp]": ["[Age Group]", ["CHV"]],
                           "[dsyn]": ["[Disease or Syndrome]", ["ICD10CM"]],
                           "[neop]": ["[Neoplastic Process]", ["ICD10CM"]],
                           "[sosy]": ["[Sign or Symptom]", ["ICD10CM"]],
                           "[patf]": ["[Pathologic Function]", ["CHV", "ICD10CM"], ["CHV", "MSH"]],
                           "[fndg]": ["[Finding]", ["HPO", "ICD10CM"]],
                           "[mobd]": ["[Mental or Behavioral Dysfunction", ["MSH"]],
                           "[diap]": ["[Diagnostic Procedure]", ["MSH", "CHV"]],
                           "[lbpr]": ["[Laboratory Procedure]", ["MSH", "CHV"]],
                           "[phsu]": ["[Pharmacologic Substance]", ["MSH", "CHV", "RXNORM"]],
                           "[topp]": ["[Therapeutic or Preventive Procedure]", ["CHV", "MSH"], ["MSH"]]
                           }

        self.needed_keys = ["Concept Name", "Semantic Types", "Sources", "Positional Info"]

    def check_semantic_type(self, semantic_types):
        """Check if the mapping result has semantic types needed."""
        # the semantic types can be multiple types
        matched_semantic_type = [s_type for s_type in semantic_types if s_type in self.vocabulary.keys()]
        semantic_type = matched_semantic_type and matched_semantic_type[0] or False
        return semantic_type

    def construct_term_dict(self, key, value):
        """Construct the term dict."""
        term_dict = dict()
        term_dict["Concept Name"] = key
        term_dict["Positional Info"] = value[0]
        term_dict["Semantic Types"] = self.vocabulary[value[1]][0]
        term_dict["Sources"] = value[2]
        return term_dict

    def mapping_collection(self, phrase):
        """Collect all the mapped terms and their info."""
        mapping_term_dict = dict()
        for mapping in phrase[1:]:
            for term in mapping:
                concept_name = term["Concept Name"].capitalize()
                negation = int(term["Negation Status"].strip()) and True or False
                semantic_types = ["[%s]" % s_type.strip() for s_type in term["Semantic Types"][1:-1].split(",")]
                sources = [source.strip() for source in term["Sources"][1:-1].split(",")]
                position = ast.literal_eval(term["Positional Info"])[0]
                if not negation:
                    if concept_name.capitalize() not in mapping_term_dict.keys():
                        mapping_term_dict[concept_name] = [position, semantic_types, sources]
                    # add source if there is multiple mapping result for the same term
                    elif semantic_types == mapping_term_dict[concept_name][1]:
                        mapping_term_dict[concept_name][2] += sources
        return mapping_term_dict

    def match_source(self, semantic_type, sources):
        """Match the given sources and required sources. The number of matched sources need to be equal to the required
        sources.
        Return: 1, matched; 2, not matched. The result has to be a true boolean value to be used in anther function."""
        if len(self.vocabulary[semantic_type]) > 2:
            required_sources1 = self.vocabulary[semantic_type][1]
            required_sources2 = self.vocabulary[semantic_type][2]
            matched_sources1 = [source for source in sources if source in required_sources1]
            matched_sources2 = [source for source in sources if source in required_sources2]
            return (len(required_sources1) == len(matched_sources1)) or \
                   (len(required_sources2) == len(matched_sources2)) and 1 or 2
        else:
            required_sources = self.vocabulary[semantic_type][1]
            matched_sources = [source for source in sources if source in required_sources]
            return len(required_sources) == len(matched_sources) and 1 or 2

    def match_semantic_types(self, mapping_term_dict):
        """Match the semantic type and the correspond sources. Only keep the mapping result
        if the semantic type is in the vocabulary and the sources are also correct.

        Input: all mapped term for the phrase, {concept name : [position, semantic type, source]}
        Return: list of dict for matched terms, [{"Concept Name", "Positional Info", "Semantic Types", "Sources"}]"""
        mapping_result = []
        position_list = []
        # set the semantic types list
        for concept_name, info in mapping_term_dict.items():
            source_set = list(set(info[2]))
            # check if the term is needed and matched
            semantic_type_needed = self.check_semantic_type(mapping_term_dict[concept_name][1])
            source_matched = semantic_type_needed and self.match_source(semantic_type_needed, source_set) or False
            mapping_term_dict[concept_name][1] = semantic_type_needed
            mapping_term_dict[concept_name][2] = source_set
            # keep one mapping result for one term
            position_info = mapping_term_dict[concept_name][0]
            if source_matched == 1 and position_info not in position_list:
                position_list += [position_info]
                mapping_result += [self.construct_term_dict(concept_name, mapping_term_dict[concept_name])]
        return mapping_result

    def match(self):
        """ Prune the list of utterances into [[{'Utterance text:'...'},{'text':'...', 'mapping':[{'Concept Name':'...',
        'Semantic Types':'...', 'Sources':'...'}, {}]}, []].
         Only the phrases with mapping pruned_utterances are kept."""

        utterance_unit_list = []
        # the first element of the utterance list is the utterance text
        utterance_dict = dict()
        utterance_dict["Utterance text"] = self.utterance[0][0][0]["Utterance text"]
        utterance_dict["Utterance start index"] = self.utterance[0][0][0]["Position"][1:-1].split(",")
        utterance_dict["Utterance syntax unit"] = self.get_lexical_type()
        utterance_unit_list += [utterance_dict]
        for phrase in self.utterance:
            # check if the phrase has mapping result
            if len(phrase) > 1:
                phrase_dict = dict()
                # the first element of the phrase list is the text of the phrase
                phrase_dict["text"] = phrase[0][0]["text"]
                phrase_mapping_result_dict = self.mapping_collection(phrase)
                phrase_dict["mapping"] = self.match_semantic_types(phrase_mapping_result_dict)
                if phrase_dict["mapping"]:
                    utterance_unit_list += [phrase_dict]
        return utterance_unit_list

    def get_lexical_type(self):
        """Return a list of (word, lexical type) of the utterance."""
        unit_list = []
        for phrase in self.utterance:
            if "Syntax Unit" in phrase[0][0].keys():
                syntax_string = phrase[0][0]["Syntax Unit"]
                # syntax_string example
                # +++ ([An]),tag(det),tokens([an])]),    shapes([
                # +++ ([,]),tokens([])])]
                for unit_info in syntax_string.split("inputmatch")[1:]:
                    # DO NOT use "," to split the string since comma could also be one unit
                    unit = unit_info.split("),")
                    # unit = ["([input_text]", "tag(lexical category", "tokens([])", "syntax cat(["]
                    unit_list += [(unit[0][2:-1], unit[1].startswith("tag(") and unit[1][4:] or None)]
        return unit_list


