# Audiobook Filer
# version 0.1
# Greg Croasdill, 2022
#
# This script takes a CSV formatted output from OpenAudible and uses that data to
# create a proper directory structure for your audiobooks.  AudioBook library management
# tools like AudioBookshelf and Plex will use this structure to display your titles in 
# the proper groupings
#
# This script was written on a MacOSX system in python 3.9.12, but has been developed so it 
# should work on any OS that supports a python environment.
#

# importing support modules
import sys
import os
import getopt
import csv
import datetime
import shutil

version = "0.1"

def printHelp():
    print ('')
    print (f'Audiobook Filer - v {version}')
    print ('')
    print ('This tool works with OpenAudible to organize your audio books for AudioBookshelf or Plex')
    print ('')
    print ('Use the export books tool to create a csv file with all the entries downloaded by OA')
    print ('Using that CSV file as input, this scirpt will create properly formatted directories in your media library')
    print ('and then copy the audiobook files (m4b) to the correct destinations')
    print ('')
    print ('Options:')
    print ('')
    print ('-h --help : This help text')
    print ('-t --test : Run only the first 10 entries in the CSV file for testing')
    print ('-v --verbose : Print debugging information while running')
    print ('-f --format : p, plex - create plex formatted directories (default)')
    print ('              a, abs, audiobookshelf - create audiobookshelf formatted directories')
    print ('-b --booklist : The CSV file containing the book information (def books.csv)')
    print ('-i --inputdir : The Openaudible book directory (def OpenAudible/m4b)')
    print ('-o --outputdir : The directory to create the formatted library (def Formatted)')
    print ('')
    

options = "htvf:b:i:o:"
longopts = ["help","test","verbose","format=","booklist=","inputdir=","outputdir="]


#default runtime values
# csv file name
openAudibleDir = "OpenAudible/m4b"
bookDir = "m4b"
destinationDir = "Formatted"
#destinationDir = "/Volumes/AllMedia/FormattedAudiobooks"
filename = "books.csv"
#TBD - currently assuming files are in .m4b format not .mp3 or .aax
fileType = "m4b"
directoryFormat = "plex"
testMode = False
verboseMode = False

args = sys.argv[1:]
options = "htvf:b:i:o:"
longopts = ["help","test","verbose","format=","booklist=","inputdir=","outputdir="]

if len(args) > 0: 
    try:
        opts, args = getopt.getopt(args,options,longopts)
    except getopt.GetoptError as err:
        print (f"Error : {err}")
        printHelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printHelp()
            sys.exit()
        elif opt in ('-f', '--format'):
            if arg in ('p','plex','a','abs','audiobookshelf'):
                directoryFormat = arg
            else:
                print (f"Unknown directory format {arg}")
                printHelp()
                sys.exit()
        elif opt in ('-b', '--booklist'):
            filename = arg
        elif opt in ('-i', '--inputdir'):
            openAudibleDir = arg
        elif opt in ('-o', '--outputdir'):
            destinationDir = arg
        elif opt in ('-t', '--test'):
            testMode = True
        elif opt in ('-v', '--verbose'):
            verboseMode = True
        else:
            print (f"Unknown option {opt}")
            printHelp()
            sys.exit()

if verboseMode:
    print ('audiobook-filer inputs are:')         
    print (f'\tdirectoryFormat is {directoryFormat}')
    print (f'\tfilename is {filename} (aka the book list)')
    print (f'\topenAudibleDir is {openAudibleDir}')
    print (f'\tdestinationDir is {destinationDir}')
    print (f'\ttestMode is {testMode}')
    
# Standard column names are:
#     Product ID, ASIN, Book URL, Title, Author, Narrated By, Summary, Description, Duration, Ave. Rating, Rating Count, Release Date, Purchase Date, Publisher, Genre, sub_genre, Short Title, Copyright, Author URL, Download URL, File name, Key, Series URL, Series Name, Series Sequence, Link Error, Abridged, Book Language, BOOK_ELEM_IGNORED, BOOK_ELEM_PDF_URL, BOOK_ELEM_IMAGE_URL, BOOK_ELEM_DIR_PATH, BOOK_ELEM_REGION, BOOK_ELEM_CHAPTERS, BOOK_ELEM_LOCKED, BOOK_ELEM_AYCE, BOOK_ELEM_TAGS, Notes, BOOK_ELEM_PODCAST

#test source directory
if not os.path.exists(openAudibleDir):
    print(f'Error: Input path {openAudibleDir} does not exist')
    print('\tcheck the input path argument')
    sys.exit();

if not os.path.exists(destinationDir):
    print(f'Error: Input path {destinationDir} does not exist')
    userInput = input('Do you want to create it? (y/n) ')
    if userInput.lower() not in ('y','yes'):
        sys.exit();

# reading csv file
try:
    csvfile = open(filename, 'r')
except OSError:
        print(f'Error: Unable to open {filename}')
        sys.exit(1)

with csvfile:
    # creating a csv reader object
    csvreader = csv.DictReader(csvfile)
    #check csv format/contents
    #TBD - Rework to minimize the required CSV columns
    requiredKeys = set(["Title", "Short Title", "Author", "Series Name", "Series Sequence", "File name", "Release Date", "BOOK_ELEM_AYCE", "Narrated By" ])
    if not requiredKeys.issubset(csvreader.fieldnames):
        print("Error: CSV bookfile is not in correct OpenAudible format")
        print(f"Fields should include: ({requiredKeys})")
        print(f"Fields found are ({csvreader.fieldnames})")
        printHelp()
        sys.exit()
    
    lineCount = 0
    
    for row in csvreader:
        lineCount += 1
        #if OpenAudible can not download the book, then this field will be empty, so skip it
        if row["BOOK_ELEM_AYCE"] == "":
            continue

        #if there is a series name, then capture it
        series =  row["Series Name"] if row["Series Name"] != "" else ""
        
        #if there is a volume/book number, then capture it, else leave blank
        vol = "Vol " + row["Series Sequence"] + ". "  if row["Series Sequence"] != "" else ""
        
        #format narrator name
        narrator = "{"+row["Narrated By"][:40]+"}"
    
# debug print(f'\t{row["Author"]}\\{series}\\{row["Release Date"][:4]} - {vol}{row["Short Title"]} {narrator}\\{row["File name"]}')

        filename = row["File name"] + "." + fileType
        #create full file path for source file
        srcFile =  os.path.join(openAudibleDir, filename)
        if verboseMode: print(f'{lineCount} - Processing Book : {row["File name"]}')

        #make sure the source really exists        
        if os.path.isfile(srcFile) == False:
            print (f'\tWARNING: {srcFile} is missing, skipping entry')
            continue
         
        
        if directoryFormat in ("a","abs","audiobookshelf"):
        #create path in audiobookself format
            destPath = os.path.join(destinationDir, row["Author"][:40], series, row["Release Date"][:4] + " - " + vol + row["Short Title"] + " " + narrator )
        elif directoryFormat in ("p","plex"):
        #create path in plex format
            destPath = os.path.join(destinationDir, row["Author"][:40], series, row["Short Title"] )
            #plex want simple filename, so just use sort title
            filename = row["Short Title"] + "." + fileType
        else:
            print(f'Error: Unknown output format {directoryFormat}')
            sys.exit(1)
    
    
        destFile = os.path.join(destPath, filename)
        if verboseMode:
            print (f'item {lineCount} - {destFile}')
        else:
            print (f'item {lineCount} - {row["Short Title"]}', end="")

        #skip if destination book already exists        
        if os.path.isfile(destFile) == True:
            if verboseMode:
                print (' - destination file already exists, skipping entry')
            else:
                print (' - skip')
            continue
    
    
        #TBD - Test to see if created
        os.makedirs(destPath, exist_ok=True)   
    
        destFileFinal = shutil.copy2(srcFile, destFile)

        if destFileFinal != "" :
            if verboseMode:
                print (f'\t{destFileFinal} created') 
            else:
                print (' - copied')
        else:
            print (f'\WARNING: {destFileFinal} NOT copied ') 

        if testMode and lineCount > 10 :
            break
        
    print(f'Processed {lineCount} lines.')
