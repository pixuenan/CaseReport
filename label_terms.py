#!usr/bin/python
"""
Process the utterance output from MetaMap.
Xuenan Pi
11/01/2016
"""

from time_point import past_regex


class LabelTerms(object):
    def __init__(self, utterance, test=False):
        self.input_utterance = utterance
        self.test = test

        self.utterance_start = int(self.input_utterance[0]["Utterance start index"][0])
        self.text = self.input_utterance[0]["Utterance text"]
        self.syntax_unit = self.input_utterance[0]["Utterance syntax unit"]

        self.utterance_dict = dict()
        self.utterance_dict["Utterance text"] = self.text
        self.utterance_dict["Utterance syntax unit"] = self.syntax_unit
        self.mapping_result = []
        self.utterance_dict["mapping result"] = self.mapping_result

        self.term_index_dict = dict()

        self.wrong_mapping_list = [("procedure", "interventional procedure"), ("therapy", "therapeutics"),
                                   ("treatment", "therapeutics"), ("cavity", "dental caries"),
                                   ("aggressive", "aggressive behavior"), ("water", "water"), ("condition", "disease"),
                                   ("immersion", "immersion"), ("sterile", "infertility"), ("syndrome", "syndrome")]

    def get_age_and_gender(self, term):
        self.utterance_dict["Age"] = term["Age"]
        if "Gender" not in term.keys():
            self.utterance_dict["Gender"] = None
        else:
            self.utterance_dict["Gender"] = term["Gender"]

    def part_of_speech_noun(self, term_word):
        """ For the word that can be found in the syntax unit, only keep the word if the word is a noun."""
        term_list, part_of_speech_list = zip(*self.syntax_unit)[0], zip(*self.syntax_unit)[1]
        if term_word not in term_list:
            term_index = None
            # sometimes the term word is a phrase
            # select the last word in the phrase, as usually noun is the last word
            term_word = term_word.split()[-1]
            for term in term_list:
                if term_word in term:
                    term_index = term_list.index(term)
            # skip the word that cannot be found in the syntax unit
            if not term_index:
                return True
        else:
            term_index = term_list.index(term_word)
        tag = part_of_speech_list[term_index]
        return tag == "noun" and True or False

    def get_concept(self, term):
        # avoid including repetitive mapping result
        if not self.term_index_dict.values() or \
                        term["Concept Name"] not in zip(*self.term_index_dict.values())[0]:
            position_list = term["Positional Info"]
            term_start = position_list[0]
            term_length = position_list[1]
            index = term_start - self.utterance_start
            term_word = self.text[index:index + term_length]
            if not self.wrong_mapping_test(term["Concept Name"], term_word) and self.part_of_speech_noun(term_word) and\
                    term["Semantic Types"] not in ["[Population Group]", "[Age Group]"]:
                if self.test:
                    self.term_index_dict[index] = (term["Concept Name"], term["Semantic Types"], term_word)
                else:
                    self.term_index_dict[index] = (term["Concept Name"], term["Semantic Types"])

    def get_time_point(self, phrase):
        for time in phrase["Time Point"]:
            index = self.text.index(time)
            self.term_index_dict[index] = (time, "[Time Point]")

    def wrong_mapping_test(self, term_concept, term_word):
        return (term_word.lower(), term_concept.lower()) in self.wrong_mapping_list

    def clean_mapping_result(self):
        """Empty the utterance mapping result if there is only time point information there."""
        if self.mapping_result:
            semantic_types_list = zip(*zip(*self.mapping_result)[1])[1]
            if set(semantic_types_list) == {"[Time Point]"}:
                del self.mapping_result[:]

    def process(self):
        for phrase in self.input_utterance[1:]:
            if "mapping" in phrase.keys():
                mapping = phrase["mapping"]
                for term in mapping:
                    # age and gender
                    if "Age" in term.keys():
                        self.get_age_and_gender(term)
                    # concept term
                    else:
                        self.get_concept(term)
            # time point
            elif "Time Point" in phrase.keys():
                self.get_time_point(phrase)

        if self.term_index_dict:
            for key in sorted(self.term_index_dict.keys()):
                # [[index, (Concept time, Semantic types/Time Point)]]
                self.mapping_result += [[key, self.term_index_dict[key]]]
            self.clean_mapping_result()

    def label_mapping_result(self):
        # print self.mapping_result, self.text, self.syntax_unit
        term_list = zip(*zip(*self.mapping_result)[1])[0]
        semantic_types_list = zip(*zip(*self.mapping_result)[1])[1]
        if "[Time Point]" in semantic_types_list:
            time_index = semantic_types_list.index("[Time Point]")
            term_idx = 0
            while term_idx < len(self.mapping_result):
                term = self.mapping_result[term_idx]
                if term[1][1] != "[Time Point]":
                    if past_regex(term_list[time_index]):
                        term[0] = ("Past", term_list[time_index])
                    # only label time point for the current part when the semantic types is sign or symptom
                    elif term[1][1] == "[Sign or Symptom]":
                        term[0] = ("Current", term_list[time_index])
                    else:
                        term[0] = ("Current", 0)
                    term_idx += 1
                else:
                    self.mapping_result.remove(term)
        else:
            for term in self.mapping_result:
                term[0] = ("Current", 0)

    def main(self):
        self.process()
        if self.mapping_result:
            self.label_mapping_result()
        return self.utterance_dict
