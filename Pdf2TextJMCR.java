/**
    Copyright (C) 2016, Genome Institute of Singapore, A*STAR  

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.factpub.factify;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;

import org.factpub.factify.nlp.Sequence;
import org.factpub.factify.nlp.StanfordNLPLight;
import org.factpub.factify.pattern.Acronym;
import org.factpub.factify.pdf.converter.PDFConverter;
import org.factpub.factify.utility.Debug;
import org.factpub.factify.utility.Debug.DEBUG_CONFIG;
import org.factpub.factify.utility.Utility;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import at.knowcenter.code.pdf.structure.PDF;
import at.knowcenter.code.pdf.structure.Paragraph;

import java.io.File;
import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
/**
 * This is the main class for convert pdf to text from Journal of Medical reports
 */
public class Pdf2TextJMCR {
	
	public static void main(String[]  args) throws IOException {
		
		/*
		 * Use this main function for debugging purpose for the time being.
		 * Ideally, Unit test should be prepared as /src/test/java/org.factpub.factify.FactifyTest
		 */
	
		
		/* sample pdf file*/
		String input_folder = "C:\\Users\\pix1\\Downloads\\casereport\\JMCR\\";
//		String pdf_file = "art%3A10.1186%2Fs13256-016-1168-0.pdf";
//		String pdf_file = "art%3A10.1186%2Fs13256-016-1160-8.pdf";
//		String pdf_file = "art%3A10.1186%2Fs13256-016-1169-z.pdf";

		
//		String[] parameters = new String[4];
//		parameters[0] = input_folder + pdf_file;
//		parameters[1] = input_folder;
//		parameters[2] = input_folder;
//		parameters[3] = "";
//		
//		System.out.println(parameters[0]);
//		System.out.println(parameters[1]);
//		System.out.println(parameters[2]);
//		System.out.println(parameters[3]);
		
		File folder = new File("C:\\Users\\pix1\\Downloads\\casereport\\JMCR\\");
		File[] listOfFiles = folder.listFiles();

		    for (int i = 0; i < listOfFiles.length; i++) {
		      if (listOfFiles[i].isFile() && listOfFiles[i].getName().endsWith(".pdf")) {
		        System.out.println("File " + listOfFiles[i].getName());
		        String pdf_file = listOfFiles[i].getName();
		        String[] parameters = new String[4];
		        parameters[0] = input_folder + pdf_file;
		        parameters[1] = input_folder;
		        parameters[2] = input_folder;
		        parameters[3] = "";
		
		        int error = extractText(parameters);
		        Debug.println("Finished with errorcode " + error, DEBUG_CONFIG.debug_error);
		
		    }
		    }
		
	}
	
	/**
	 * 
	 * @param args Input parameters <br>
	 * 0: Input PDF Path <br>
	 * 1: Output directory <br>
	 * 2: Debug directory <br>
	 * 3: Output_log <br>
	 * @return ErrorCode<br>
	 * -1: input parameter error <br>
	 * 0: Input file does not exist<br>
	 * 1: Success<br>
	 * 2: PDF Converter failed<br>
	 * 3: PDF Converter succeeded, but no body text (or section heading)<br>
	 * @throws IOException 
	 */
	
	public static int extractText(String...args) throws IOException {
		
		/*
		 * Step0-0: Check JRE version
		 */
		{
			String[] javaVersionElements = System.getProperty("java.runtime.version").split("\\.");//1.8.0_45-b14
			try {
				int major = Integer.parseInt(javaVersionElements[1]);
				if (major < 8) System.exit(-33);
			}
			catch (Exception e ){
				
			}
		}
		
		/*
		 * Step0-1: Check if the arguments are okay
		 */
		if(args.length < 4) {
			Debug.println("Please input PDF path, output directory, debug directory and debug_log file!", DEBUG_CONFIG.debug_error);
			Debug.println("*If debug_log=\"\", then debug info will print to the screen.", DEBUG_CONFIG.debug_error);
			Debug.println("*Please add slash to folder path.", DEBUG_CONFIG.debug_error);
			
			Debug.println("Parameters are :" , DEBUG_CONFIG.debug_error);
			for(String s : args) Debug.println(s, DEBUG_CONFIG.debug_error);
			return -1;
		}
		
		/*
		 * Step0-2: Configure Debug file
		 */
		{
				DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss");
				Calendar cal = Calendar.getInstance();
				Debug.debugFile = args[3];
				if(Debug.debugFile.trim().equals("")) {
					Debug.debugFile = null;
					Debug.init();
				}else {
					Debug.init();
				}
				Debug.print("========" + dateFormat.format(cal.getTime()) + "==========\r\n", DEBUG_CONFIG.debug_timeline);
		}
		
		
		/*
		 * Step0-3: Check each arguments.
		 */
		String path = args[0];
		File file = new File(path);
		if (!file.exists()) {
			Debug.print("Input File " + path + " does not exist!", DEBUG_CONFIG.debug_error);
			return 0;
		}
		String output_dir = args[1];
		
		String debug_dir = args[2];
		
		
		
		/*
		 * Step1: pdf-extraction
		 * Given PDF file is parsed and structuralized by PdfExtractionPipeline.
		 * The extracted texts are organized as a PDF instance.
		 */
		PDFConverter converter = new PDFConverter();
		PDF pdf =  converter.run(file, file.getName(), output_dir, debug_dir);
		if(pdf == null) {
			Debug.println("PDF Converter Failed!",DEBUG_CONFIG.debug_error);
			Debug.println("File Path: " + path,DEBUG_CONFIG.debug_error);
			return 2;
		}
		
		/* Write by Xuenan Pi
		 * Solve the unexpected sentence break by pages or columns problem.
		 */
		else if(new File(path).canWrite()) {
			JSONObject reportTxt = new JSONObject();
			Writer out; 
			boolean append = false;
			String facts_name = Utility.MD5(path);
			String fact_file = output_dir + facts_name + "JMCR.json";
			out = new BufferedWriter(new OutputStreamWriter(
					  new FileOutputStream(new File(fact_file), append), "US-ASCII"));
			

			reportTxt.put("DOI", pdf.doi);
//			System.out.println("###PDF Name:" + path);
//			System.out.println("###Title:" + pdf.candidateTitle.get(2).text);
//			System.out.println("###JSon Name:" + fact_file);
			
			Utility.sewBrokenSentence(pdf.body_and_heading);
			boolean introPrintFlag = false; 
			boolean casePrintFlag = false; 
			JSONArray caseParaArray = new JSONArray();
			List<Sequence> introSequences = new ArrayList<Sequence>();
			List<Sequence> caseSequences = new ArrayList<Sequence>();
			for(int i = 0; i < pdf.body_and_heading.size(); i++) {
				Paragraph para = pdf.body_and_heading.get(i);
				
				if (para.text.startsWith("Received:")){
					reportTxt.put("Received Date", para.text);
//					System.out.println(para.text);
				}
				String paraText = para.text.replace("\n", "").replace("\r", "");
				if (paraText.equals("Introduction") || paraText.equals("Background")){
					introPrintFlag = true; 
					continue;
				}
				if (paraText.startsWith("Case")){
					casePrintFlag = true; 
					introPrintFlag = false; 
					continue;
				}
				if (paraText.equals("Discussion")){
					casePrintFlag = false; 
				}
				if (introPrintFlag){
					List<Sequence> para_seq = StanfordNLPLight.INSTANCE.textToSequence(para.text, true);
					introSequences.addAll(para_seq);
				}
				if (casePrintFlag){
					List<Sequence> para_seq = StanfordNLPLight.INSTANCE.textToSequence(para.text, true);
					caseSequences.addAll(para_seq);
				}
				
			}
			if (!introSequences.isEmpty()) {
				Map<String, Sequence> acronyms = Acronym.findAcronyms(introSequences);
			
				for (Sequence sentence: caseSequences) {
					String sentenceText = sentence.getSourceString();
					caseParaArray.add(acronymReplace(sentenceText, acronyms));
				}
			} else {
				for (Sequence sentence: caseSequences) {
					String sentenceText = sentence.getSourceString();
					caseParaArray.add(sentenceText);
				}
			}
			
			reportTxt.put("Case presentation", caseParaArray);
			out.write(reportTxt.toJSONString());
			out.flush();
			out.close();
		}

		
		/*
		 * If everything is okay, this returns 1.
		 */
		
		return 1;
	}
	
	/*
	 * Replace the acronym in the sentences with the full name.
	 */
	private static String acronymReplace(String text, Map<String, Sequence> acronymDict) {
		for (String s: acronymDict.keySet()) {
			if (text.contains(s)) {
				text = text.replace(s, acronymDict.get(s).getSourceString());
			}
		}
		return text;
	}
	
	
}
