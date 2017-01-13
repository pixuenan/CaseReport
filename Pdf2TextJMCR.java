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

import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.StringTokenizer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.factpub.factify.knowledge_model.C_Facts;
import org.factpub.factify.knowledge_model.S_Facts;
import org.factpub.factify.nlp.Sequence;
import org.factpub.factify.nlp.StanfordNLPLight;
import org.factpub.factify.pattern.Acronym;
import org.factpub.factify.pattern.NGrams;
import org.factpub.factify.pattern.RootMatcher;
import org.factpub.factify.pdf.converter.PDFConverter;
import org.factpub.factify.utility.Debug;
import org.factpub.factify.utility.Debug.DEBUG_CONFIG;
import org.factpub.factify.utility.Utility;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import at.knowcenter.code.pdf.structure.PDF;
import at.knowcenter.code.pdf.structure.Paragraph;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
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
		String input_folder = "C:\\Users\\pix1\\Downloads\\casereport_JMCR\\";
		String pdf_file = "art%3A10.1186%2Fs13256-016-1168-0.pdf";
//		String pdf_file = "art%3A10.1186%2Fs13256-016-1160-8.pdf";
//		String pdf_file = "art%3A10.1186%2Fs13256-016-1169-z.pdf";

		
		String[] parameters = new String[6];
		parameters[0] = input_folder + pdf_file;
		parameters[1] = input_folder;
		parameters[2] = input_folder;
		parameters[3] = "";
		
		System.out.println(parameters[0]);
		System.out.println(parameters[1]);
		System.out.println(parameters[2]);
		System.out.println(parameters[3]);
		
		int error = extractText(parameters);
		Debug.println("Finished with errorcode " + error, DEBUG_CONFIG.debug_error);
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
	 * 4: Facts exist<br>
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
			String fact_file = output_dir + facts_name + "MJCR.txt";
			out = new BufferedWriter(new OutputStreamWriter(
					  new FileOutputStream(new File(fact_file), append), "UTF-8"));
			

			reportTxt.put("Title", pdf.candidateTitle.get(2).text);
//			out.write("Title:" + pdf.candidateTitle.get(2).text + "\n\r");
//			System.out.println("Title:" + pdf.candidateTitle.get(2).text);
			
			Utility.sewBrokenSentence(pdf.body_and_heading);
			boolean printFlag = false; 
			JSONArray paraArray = new JSONArray();
			for(int i = 0; i < pdf.body_and_heading.size(); i++) {
				Paragraph para = pdf.body_and_heading.get(i);
				
				if (para.text.startsWith("Received:")){
					reportTxt.put("Received Date", para.text);
//					System.out.println(para.text);
//					out.write(para.text);
//					out.write('\n');
				}
				
				if (para.text.replace("\n", "").replace("\r", "").equals("Case presentation")){
					printFlag = true; 
					continue;
				}
				if (para.text.replace("\n", "").replace("\r", "").equals("Discussion")){
					printFlag = false; 
				}
				if (printFlag){
					paraArray.add(para.text);
//					System.out.println(para.text);
				}
				
			}
			reportTxt.put("Case presentation", paraArray);
			out.write(reportTxt.toJSONString());
			out.flush();
			out.close();
		}

		
		/*
		 * End of runFactify
		 * If everything is okay, this returns 1.
		 */
		
		return 1;
	}
	
	
}
