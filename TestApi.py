""" complete example of using MetaMap api """
import sys
import string
from se.sics.prologbeans import PrologSession
from gov.nih.nlm.nls.metamap import MetaMapApi, MetaMapApiImpl, Result


class TestApi:
    def __init__(self):
        self.api = MetaMapApiImpl()

    def display_aas(self, result, output=sys.stdout):
        aalist = result.getAcronymsAbbrevs()
        if len(aalist) > 0:
            for e in aalist:
                output.write('Acronym: %s\n' % e.getAcronym())
                output.write('Expansion: %s\n' % e.getExpansion())
                output.write('Count list: %s\n' % e.getCountList())
                output.write('CUI list: %s\n' % e.getCUIList())
        else:
            output.write('None.')

    def display_negations(self, result, output=sys.stdout):
        neglist = result.getNegations()
        if len(neglist) > 0:
            for e in neglist:
                output.write("type: %s, " % e.getType())
                output.write("Trigger: %s: [ " % e.getTrigger())
                for pos in  e.getTriggerPositionList():
                    output.write('%s,' % pos)
                output.write('], ')
                output.write("ConceptPairs: %s: [ " % e.getConceptPairList())
                for pair in  e.getTriggerPositionList():
                    output.write('%s,' % pair)
                output.write('], ')
                output.write("Concept Positions: %s: [ " % e.getConceptPositionList())
                for pos in  e.getTriggerPositionList():
                    output.write('%s,' % pos)
                output.write(']\n')

    def display_utterances(self, result, display_pcmlist=False, output=sys.stdout):
        for utterance in result.getUtteranceList():
            output.write("Utterance:\n")
            output.write(" Id: %s\n" % utterance.getId())
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
                        output.write("  Preferred Name: %s\n" % ev.getPreferredName())
                        output.write("  Matched Words: %s\n" % ev.getMatchedWords())
                        output.write("  Semantic Types: %s\n" % ev.getSemanticTypes())
                        output.write("  is Head?: %s\n" % ev.isHead())
                        output.write("  is Overmatch?: %s\n" % ev.isOvermatch())
                        output.write("  Sources: %s\n" % ev.getSources())
                        output.write("  Positional Info: %s\n" % ev.getPositionalInfo())
                    output.write("Mappings:\n")
                    for map in pcm.getMappings():
                        output.write(" Map Score:% s\n" % map.getScore())
                        for mapev in map.getEvList():
                            output.write("  Score: %s\n" % mapev.getScore())
                            output.write("  Concept Id: %s\n" % mapev.getConceptId())
                            output.write("  Concept Name: %s\n" % mapev.getConceptName())
                            output.write("  Preferred Name: %s\n" % mapev.getPreferredName())
                            output.write("  Matched Words: %s\n" % mapev.getMatchedWords())
                            output.write("  Semantic Types: %s\n" % mapev.getSemanticTypes())
                            output.write("  is Head?: %s\n" % mapev.isHead())
                            output.write("  is Overmatch?: %s\n" % mapev.isOvermatch())
                            output.write("  Sources: %s\n" % mapev.getSources())
                            output.write("  Positional Info: %s\n" % mapev.getPositionalInfo())

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
                self.display_aas(result, output_text)
                self.display_negations(result, output_text)
                self.display_utterances(result, output=output_text)
        output_text.close()

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('input file and output file needed')
        exit(1)
    else:
        inst = TestApi()
        i = 0
        while i < len(sys.argv):
            if sys.argv[i] == "-i":
                input_file = sys.argv[i+1]
                i = i + 2
            elif sys.argv[i] == "-o":
                output_file = sys.argv[i+1]
                i = i + 2
            else:
                i += 1
        server_options = ["-R", "CHV,HPO,ICD10CM,MSH,RXNORM", "-V", "USAbase", "-A"]
        inst.process(input_file, output_file, server_options)
