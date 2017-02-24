""" complete example of using MetaMap api """
import sys
import string
import json
from se.sics.prologbeans import PrologSession
from gov.nih.nlm.nls.metamap import MetaMapApi, MetaMapApiImpl, Result


class MetaMapCaseText:
    def __init__(self):
        self.api = MetaMapApiImpl()
        self.result = dict()
        self.result_text = []

    def display_utterances(self, result, display_pcmlist=False):
        for utterance in result.getUtteranceList():
            self.result_text += ["Utterance:\n"]
            self.result_text += [" Utterance text: %s\n" % utterance.getString()]
            self.result_text += [" Position: %s\n" % utterance.getPosition()]
            if display_pcmlist:
                for pcm in utterance.getPCMList():
                    self.result_text += ["Phrase:\n"]
                    self.result_text += [" text: %s\n" % pcm.getPhrase().getPhraseText()]
                    self.result_text += [" Syntax Unit: %s\n" % pcm.getPhrase().getMincoManAsString()]
                    self.result_text += ["Mappings:\n"]
                    for map in pcm.getMappings():
                        self.result_text += [" Map Score:% s\n" % map.getScore()]
                        for mapev in map.getEvList():
                            self.result_text += ["  Score: %s\n" % mapev.getScore()]
                            self.result_text += ["  Concept Id: %s\n" % mapev.getConceptId()]
                            self.result_text += ["  Concept Name: %s\n" % mapev.getConceptName()]
                            self.result_text += ["  Semantic Types: %s\n" % mapev.getSemanticTypes()]
                            self.result_text += ["  Sources: %s\n" % mapev.getSources()]
                            self.result_text += ["  Positional Info: %s\n" % mapev.getPositionalInfo()]
                            self.result_text += ["  Negation Status: %s\n" % mapev.getNegationStatus()]

    def read_input(self, filename):
        file_content = open(filename)
        file_text = json.loads(file_content.read())
        file_content.close()
        return file_text

    def process(self, input_file, output_file, server_options):

        input_json = self.read_input(input_file)

        input_text = "\n".join(input_json["Case presentation"]).encode("ascii","replace")

        if len(server_options):
            self.api.setOptions(server_options)

        result_list = self.api.processCitationsFromString(input_text)
        output_text = open(output_file, "w+")
        for result in result_list:
            if result:
                print "input text: "
                print " " + result.getInputText()
                self.display_utterances(result, display_pcmlist=True)

        input_json["MetaMap result"] = self.result_text
        output_text.write(json.dumps(input_json))
        output_text.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('input file needed')
        exit(1)
    else:
        inst = MetaMapCaseText()
        i = 0
        while i < len(sys.argv):
            if sys.argv[i] == "-i":
                input_file = sys.argv[i+1]
                i = i + 2
            else:
                i += 1
        output_file = input_file.split('.')[0] + '.MetaMap.json'
        server_options = ["-R", "CHV,HPO,ICD10CM,MSH,RXNORM", "-V", "USAbase", "-A"]
        inst.process(input_file, output_file, server_options)
