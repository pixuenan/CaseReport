""" complete example of using MetaMap api """
import sys
import string
from se.sics.prologbeans import PrologSession
from gov.nih.nlm.nls.metamap import MetaMapApi, MetaMapApiImpl, Result


class TestApi:
    def __init__(self):
        self.api = MetaMapApiImpl()

    def display_utterances(self, result, display_pcmlist=False, output=sys.stdout):
        for utterance in result.getUtteranceList():
            output.write("Utterance:\n")
            output.write(" Utterance text: %s\n" % utterance.getString())
            output.write(" Position: %s\n" % utterance.getPosition())
            if display_pcmlist:
                for pcm in utterance.getPCMList():
                    output.write("Phrase:\n")
                    output.write(" text: %s\n" % pcm.getPhrase().getPhraseText())
                    output.write("Candidates:\n")
                    for ev in pcm.getCandidates():
                        output.write(" Candidate:\n")
                        output.write("  Score: %s\n" % ev.getScore())
                        output.write("  Concept Id: %s\n" % ev.getConceptId())
                        output.write("  Concept Name: %s\n" % ev.getConceptName())
                        output.write("  Semantic Types: %s\n" % ev.getSemanticTypes())
                        output.write("  Sources: %s\n" % ev.getSources())
                        output.write("  Positional Info: %s\n" % ev.getPositionalInfo())
                        output.write("  Negation Status: %s\n" % ev.getNegationStatus())
                    output.write("Mappings:\n")
                    for map in pcm.getMappings():
                        output.write(" Map Score:% s\n" % map.getScore())
                        for mapev in map.getEvList():
                            output.write("  Score: %s\n" % mapev.getScore())
                            output.write("  Concept Id: %s\n" % mapev.getConceptId())
                            output.write("  Concept Name: %s\n" % mapev.getConceptName())
                            output.write("  Semantic Types: %s\n" % mapev.getSemanticTypes())
                            output.write("  Sources: %s\n" % mapev.getSources())
                            output.write("  Positional Info: %s\n" % mapev.getPositionalInfo())
                            output.write("  Negation Status: %s\n" % mapev.getNegationStatus())

    def read_input(self, filename):
        file_content = open(filename)
        file_text = file_content.read()
        file_content.close()
        return file_text

    def process(self, input_file, output_file, server_options):

        input_text = self.read_input(input_file)

        if len(server_options):
            self.api.setOptions(server_options)

        result_list = self.api.processCitationsFromString(input_text)
        output_text = open(output_file, "a+")
        for result in result_list:
            if result:
                print "input text: "
                print " " + result.getInputText()
                self.display_utterances(result, display_pcmlist=True, output=output_text)
        output_text.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('input file and output file needed')
        exit(1)
    else:
        inst = TestApi()
        i = 0
        while i < len(sys.argv):
            if sys.argv[i] == "-i":
                input_file = sys.argv[i+1]
                i = i + 2
            else:
                i += 1
        output_file = input_file.split('.')[0] + 'result.txt'
        server_options = ["-R", "CHV,HPO,ICD10CM,MSH,RXNORM", "-V", "USAbase", "-A"]
        inst.process(input_file, output_file, server_options)
