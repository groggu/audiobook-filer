#the purpose of this script is to utilize the 

# importing support modules
import csv
import datetime
import os
import shutil
 
# csv file name
filename = "audiobooks.csv"
openAudibleDir = "/Volumes/Untitled/OpenAudible"
bookDir = "m4b"
#destinationDir = "/Volumes/Untitled/OpenAudible/Formatted"
destinationDir = "/Volumes/AllMedia/FormattedAudiobooks"
 
# Column names are:Product ID, ASIN, Book URL, Title, Author, Narrated By, Summary, Description, Duration, Ave. Rating, Rating Count, Release Date, Purchase Date, Publisher, Genre, sub_genre, Short Title, Copyright, Author URL, Download URL, File name, Key, Series URL, Series Name, Series Sequence, Link Error, Abridged, Book Language, BOOK_ELEM_IGNORED, BOOK_ELEM_PDF_URL, BOOK_ELEM_IMAGE_URL, BOOK_ELEM_DIR_PATH, BOOK_ELEM_REGION, BOOK_ELEM_CHAPTERS, BOOK_ELEM_LOCKED, BOOK_ELEM_AYCE, BOOK_ELEM_TAGS, Notes, BOOK_ELEM_PODCAST
 
# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.DictReader(csvfile)
    line_count = 0
    for row in csvreader:
#        if line_count == 0:
#            print(f'Column names are {", ".join(row)}')
#        print(f'\t{row["Short Title"]} was written by {row["Author"]} and is narrated by {row["Narrated By"]}.')

#if not downloaded, skip		
        if row["BOOK_ELEM_AYCE"] == "":
        	continue
        
        line_count += 1

#if there is a series name, then capture it, else use the short name
        series =  row["Series Name"] if row["Series Name"] != "" else ""
        	
#if there is a volume/book number, then capture it, else leave blank
        vol = "Vol " + row["Series Sequence"] + ". "  if row["Series Sequence"] != "" else ""
#cant figure out yet how to get curly brackets in the print f format
        narrator = "{"+row["Narrated By"][:40]+"}"
        
#        print(f'\t{row["Author"]}\\{series}\\{row["Release Date"][:4]} - {vol}{row["Short Title"]} {narrator}\\{row["File name"]}')

#copy the file to full path
        filename = row["File name"] + ".m4b"
        srcFile =  os.path.join(openAudibleDir, bookDir, filename)
        print(f'{line_count} - Processing Book : {row["File name"]}')

#make sure the source really exists        
        if os.path.isfile(srcFile) == False:
            print (f'\tWARNING {srcFile} is missing, skipping entry')
            continue
             
# Path
        destPath = os.path.join(destinationDir, row["Author"][:40], series, row["Release Date"][:4] + " - " + vol + row["Short Title"] + " " + narrator )
#        print (destPath)
        destFile = os.path.join(destPath, filename)
#skip if destination book already exists        
        if os.path.isfile(destFile) == True:
            print (f'\tWARNING {destFile} already exists, skipping entry')
            continue
        
        
        os.makedirs(destPath, exist_ok=True)   
#        print ("Directory '%s' created", destPath)
        
        destFileFinal = shutil.copy2(srcFile, destPath)
        print (f'\t{destFileFinal} created') if destFileFinal != "" else  print (f'\tERROR: {destFileFinal} NOT copied ') 
#        if line_count > 10 :
#        	break
        
    print(f'Processed {line_count} lines.')    