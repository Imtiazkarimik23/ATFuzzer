#!/usr/local/bin/python
# import packages
import PyPDF2
import re

# open the pdf file
object = PyPDF2.PdfFileReader("3GPP.pdf")

# get number of pages
NumPages = object.getNumPages()
print(NumPages)
# define keyterms
String = "Modification"

# extract text and do the search
for i in range(0, NumPages):
    PageObj = object.getPage(i)
    print("this is page " + str(i)) 
    Text = PageObj.extractText() 
    # print(Text)
    ResSearch = re.search(String, Text)
    print(ResSearch)
