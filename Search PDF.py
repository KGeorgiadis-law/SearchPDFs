#!Py 3.5.2
# Search PDF. A script designed to search a folder of PDF files for a word or
# phrase and return all sentences containing that word of phrase.

# Started development 01/12/2016 by Konstantinos Georgiadis after lengthy discussion
# with Polis Georgiou @ Dublin, in a pub.

# Running commentary on 02/12/2016: the first results have been very encouraging
# with time to search reduced x100 in the second instance.

# Improvements: enable coverage of non-pdf sources like Word, and
# use regex to find word in a more efficient way.

'''Method'''
''' *Create list containing all txt files beginning with $pdfname 
 *for_loop through txt files in list, searching for $input
  *Append occurrences of sentences containing $input in a 'results' list, along with page found
 *Print name of PDF file, followed by list of occurrences (if no occurrences, print nothing and move on to next file)
except *file does not exist error*:
 *for_loop for every page in the PDF file, extracting text to a string
  *Create a new txt file ("$pdfname.*pageNo*.txt")
  *write string to txt file and close txt file
 *After done, try same process again.'''

###housekeeping###

import PyPDF2, os, re, time
from collections import OrderedDict #with help from http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-whilst-preserving-order



### FUNCTIONS ###

def searchPDF(filename, key):
    #function that searches through txt files representing the pages of the
    #PDF file. 
    #TO DO: Create a list with all txt files representing pages of the filename
    #TODO: Open each txt file in a for_loop
        #if the word exists in a text, find the previous and next punctuation
        #append to a 'results' list the sentence, also listing the page,
        #and maybe a \n character.
    #TODO: return list with results.
    pages = []
    results = []
    resultLists = []
    noDuplicates = []
    for file in os.listdir('Index'):
        if file.startswith(filename):
            pages.append(file)
    pageNo = 0
    if len(pages) == 0: raise FileNotFoundError
    for page in pages:
        pageNo += 1
        txtObj = open(os.path.join('Index', page), "r", encoding='utf8')#open each txt page
        text = txtObj.read()
        text = re.sub(r"\s{2,}", " ", text)
        if key in text: #this is very ugly and probably very inefficient. Will have to find a way to make it better - regex, probably
            keyIndexes = [m.start() for m in re.finditer(key, text)] #find iterations of key in the text
            for index in keyIndexes:
                punctuationSigns = ['.', '?', '!']
                punctuationIndexEnd = [] # list to save the indices of punctuation signs after the word
                punctuationIndexStart = [] # list to save the indices of punctuation signs before the word
                for p in punctuationSigns:
                    punctuationIndexEnd.append(text.find(p, index))
                    punctuationIndexStart.append(text.rfind(p, 0, index))
                if max(punctuationIndexEnd) == -1:
                    sentenceEnd = -1
                else:
                    punctuationIndexEnd = [x for x in punctuationIndexEnd if x != -1]
                    sentenceEnd = min(punctuationIndexEnd)+ 1
                sentenceStart = max(punctuationIndexStart) + 1
                results.append("[Page %s] '%s'" % (pageNo, text[sentenceStart:sentenceEnd]))
    noDuplicates = list(OrderedDict.fromkeys(results)) #removes dublicates - see 'housekeeping'          
    return noDuplicates
    

### START OF MAIN CODE ###
location = "."
pdfFiles = [] # list containing the file names of the files in the folder

for filename in os.listdir(location):
    if filename.endswith('.pdf'):
        pdfFiles.append(filename)
print(':: Welcome! %s PDF File(s) in this folder.' % (len(pdfFiles)))

while True: #Step 1: Take word or phrase from user
    print("\n\n\n\nNew Search\n=================================")
    firstTime = True
    noOfResults = 0
    ans = input("\nWould you like to save your results as a text file? This will overwrite the previous results. (y)\n") 
    key = input('\nPlease enter a word or phrase that you want to search for: ')
    if ans == "y":
        txtObj = open("results.txt", "w")
        txtObj.write("Results for '%s':\n" % key)
        txtObj.close()
    begin_time = time.time()
    for filename in pdfFiles:
        results = []
        try:
            results = searchPDF(filename, key)
        except IOError or FileNotFoundError:
            if firstTime:
                print("\nNon-indexed files have been found! Thank you for waiting while we index these files.")
                firstTime = False
            os.makedirs('Index', exist_ok="True")
            start_time = time.time()
            print("\nIndexing '%s'..." % filename)
            #Open PDF File
            pdfFileObj = open(os.path.join(location, filename), "rb")
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            #Extract the text from each page of the filename
            for pageNum in range(pdfReader.numPages): #for_loop for each page
                pageObj = pdfReader.getPage(pageNum)
                CurrentPageText = pageObj.extractText()
                CurrentPageText = CurrentPageText.replace('\n', ' ').replace('\r', '').replace('\t', '') # remove line breaks
                CurrentPageText = re.sub(r"\s{2,}", " ", CurrentPageText) #replace double/more spaces with single spaces
                #write text to a new txt file
                txtObj = open(os.path.join('Index', "%s.%s.txt" % (filename, pageNum)), "w", encoding='utf8')
                txtObj.write(CurrentPageText)
                txtObj.close()
            elapsed_time = round(time.time() - start_time, 4)
            print("Done! %s seconds." % elapsed_time)
            results = searchPDF(filename, key)
        if results == []: #if there are no results, move on to next file
            continue
        else:
            if ans == "y":
                txtObj = open("results.txt", "a", encoding="utf8")
                txtObj.write("\n\nResults found in '%s': \n-------------------------------------" % filename)
                for result in results:
                    txtObj.write("\n%s" % result)
                    noOfResults += 1
                txtObj.close()
            else:
                print("\n\nResults found in '%s': \n-------------------------------------" % filename)
                for result in results:
                    print(result)
                    noOfResults += 1
    total_time = round(time.time() - begin_time, 4)
    print("\n\nSearch finished. %s sentences containing '%s' have been found. The search has taken %s seconds overall (including indexing)." % (noOfResults, key, total_time))
