from collections import defaultdict
import hashlib
import os
import sys
import csv
import time
import win32con
import win32api
import humanfriendly

args = None

# TODO:
#  Add regular expresions
#   - always delete
#   - never delete

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    #if iteration == total: 
    #	print()

#Other similar scripts
#https://github.com/philipbl/duplicate-images
#  -> image test
#https://github.com/michaelkrisper/duplicate-file-finder
#  1. Size 
#  2. adler32-CRC of the first 1024 Bytes
#  3. sha256-hash

def md5checksum(filepath,oneMegMultiple=0):
    #Memory intensive example
    #with open(filepath, "rb") as afile:
    #	return hashlib.md5(afile.read()).hexdigest()
    
    #other block read eddxample:
    read_size = 1024*1024 # You can make this bigger
    checksum1 = hashlib.md5()
    i = 0
    with open(filepath, 'rb') as afile:
        data = afile.read(read_size)
        while data:
            checksum1.update(data)
            data = afile.read(read_size)
            i = i + 1
            if i == oneMegMultiple:
                checksum1 = checksum1.hexdigest()
                return checksum1
    checksum1 = checksum1.hexdigest()
    return checksum1

def csvToList(csvFile = None):
    theList = []
    #Import Database to speedup calculations for MD5 hashes
    if csvFile is not None:
        sizeDatabase = os.path.getsize(csvFile)
        if sizeDatabase > 50:
            printProgressUpdate = int(sizeDatabase/50)
        else:
            printProgressUpdate = sizeDatabase
        progressPosition = 0
        progressLines = 0
        print ("Importing List: ",inputCSVdataBase)
        with open(csvFile) as f_csv:
            csvReader = csv.reader(f_csv,delimiter='\t')
            try:
                for row in csvReader:
                    lenRow = len(row)
                    if lenRow == 0:
                        progressPosition += 1
                        continue
                    if lenRow == 1:
                        if row[0].startswith('#'):
                            continue
                    theList.append([])	#Add List row Item List
                    progressPosition += lenRow + 1
                    progressLines += 1
                    for i in range(0,len(row)):
                        lenRow = len(row[i])
                        progressPosition += lenRow 
                        if lenRow == 0:
                            pass
                        else:
                            theList[-1].append(row[i]) #Add value 
                    if (progressLines%printProgressUpdate == 0):
                        printProgressBar(progressPosition,sizeDatabase)
            except (KeyboardInterrupt, SystemExit):
                print()
                print("Keyboard break / System Exit called")
                print ("Database Size: ",len(theList))
                return theList
        printProgressBar(progressPosition,sizeDatabase)
        print ()
        print (csvFile," Size: ",len(theList))
        print (theList)
        return theList
    else:
        return None
    
### Loads the database of stored previouse runs. This is done to speed things up.
def loadTheDataBase(inputCSVdataBase = None):
    database = defaultdict(list)
    #Import Database to speedup calculations for MD5 hashes
    if inputCSVdataBase is not None:
        sizeDatabase = os.path.getsize(inputCSVdataBase)
        progressPosition = 0
        progressLines = 0
        print ("Importing Database: ",inputCSVdataBase)
        with open(inputCSVdataBase) as f_csv:
            csvReader = csv.reader(f_csv,delimiter='\t')
            try:
                for row in csvReader:
                    lenRow = len(row)
                    if lenRow == 0:
                        progressPosition += 1
                        continue
                    progressPosition += lenRow + 1
                    path = None
                    md5 = None
                    md5_quick = None
                    mtime = None
                    size = None
                    mode = None
                    progressLines += 1
                    for i in range(0,len(row)):
                        lenRow = len(row[i])
                        progressPosition += lenRow 
                        if lenRow == 0:
                            pass
                        else:
                            if i == 0:
                                path = row[i]#.encode('ascii','ignore')
                            if i == 1:
                                md5 = row[i]
                            if i == 2:
                                size = int(row[i])
                            if i == 3:
                                mtime = float(row[i])
                            if i == 4:
                                md5_quick = row[i]
                            if i == 5:
                                mode = int(row[i])
                    if path is not None:
                        database[path] = (md5,size,mtime,md5_quick,mode)
                    else:
                        print (row) 
                    if (progressLines%20000 == 0): #Rows not sizes
                        printProgressBar(progressPosition,sizeDatabase)
            except (KeyboardInterrupt, SystemExit):
                print()
                print("Keyboard break / System Exit called")
                print ("Database Size: ",len(database))
                return database
        printProgressBar(progressPosition,sizeDatabase)
    print ()
    print ("Database Size: ",len(database))
    return database
    
#Export Database to speedup calculations for MD5 hashes later
def saveTheDataBase(database,outputCSVdataBase=None):
    print ("Export Database to ",outputCSVdataBase)
    lenDatabase = len(database)
    lenProgressUpdate = int(lenDatabase/500)
    progressLines = 0
    if outputCSVdataBase is not None:
        with open(outputCSVdataBase,"w",newline='') as f_csv:
            csvWriter = csv.writer(f_csv,delimiter='\t')
            for row in database.items():
                path,values = row
                if len(values) == 0:
                    continue
                md5,size,mtime,md5_quick,mode = values
                csvWriter.writerow([path,md5,size,mtime,md5_quick,mode])
                progressLines += 1
                if progressLines%lenProgressUpdate == 0:
                    printProgressBar(progressLines,lenDatabase)
        printProgressBar(progressLines,lenDatabase)
        print()
                    

### Update size and modification time, which clears any checksums
### http://www.diveintopython3.net/comprehensions.html
### https://docs.python.org/3.0/library/stat.html
def updateStats(database, search_dirs,ignoreAboveSize=None):
    pathList = []
    #Traverse the File Tree and update size and modified time.
    #If any of these are modified, the checksums are cleared.
    lenDatabase = len(database)
    lenProgressUpdate = int(lenDatabase/500)
    tmpProgress = 0
    progress = 0
    strText = None
    for search_dir in search_dirs:
        print ("Reading stats from (progress expressed in terms existing database entries):",search_dir)
        for root, dirs, files in os.walk(search_dir):
            #if progress == 0:
            #	print (root, len(dirs), dirs)
            progress += len(dirs) 
            progress += len(files)
            tmpProgress += len(files)
            tmpProgress += len(dirs)
            if strText is None:
                strText = root.encode('ascii','ignore').decode('utf-8','ignore') + " "*100
            if lenDatabase != 0:
                if (progress%lenProgressUpdate) == 0 or (tmpProgress>lenProgressUpdate):
                    tmpProgress = 0
                    printProgressBar(progress,lenDatabase,suffix = strText[0:100])
            for filename in files:
                path = os.path.join(root, filename)
                if len(filename) <= 0:
                    continue
                try:
                    fileStats = os.stat(path)
                    mtime = fileStats.st_mtime
                    size = fileStats.st_size
                    if size < 256: #Always ignore files smaller than 256... File to keep link is larger.
                        continue
                    mode = fileStats.st_mode
                    if filename.startswith("."):
                        mode = mode | 0x020000
                    attrs = win32api.GetFileAttributes(path)
                    if ((attrs & win32con.FILE_ATTRIBUTE_READONLY) != 0):
                        mode = mode | 0x010000
                    if ((attrs & win32con.FILE_ATTRIBUTE_HIDDEN) != 0):
                        mode = mode | 0x020000
                    if ((attrs & win32con.FILE_ATTRIBUTE_SYSTEM) != 0):
                        mode = mode | 0x040000
                    if ((attrs & win32con.FILE_ATTRIBUTE_DIRECTORY) != 0):
                        mode = mode | 0x100000
                    if ((attrs & win32con.FILE_ATTRIBUTE_ARCHIVE) != 0):
                        mode = mode | 0x200000
                    if ((attrs & win32con.FILE_ATTRIBUTE_NORMAL) != 0):
                        mode = mode | 0x800000
                    
                except(KeyboardInterrupt, SystemExit):
                    print()
                    print("Keyboard Interupt or System Exit")
                    return database,pathList
                except:
                    print (hex(attrs), fileStats, " "*40)
                    print ("  ",path.encode('ascii','ignore').decode('utf-8','ignore'))
                    size = 0
                    mtime = 0.0
                    mode = 0
                if ignoreAboveSize is not None:
                    if size > ignoreAboveSize:
                        continue
                pathList.append(path)
                #try:
                #	size = os.path.getsize(path)
                #except:
                #	size = 0
                #try:
                #	#mtime = os.stat(path).st_mtime
                #	mtime = os.path.getmtime(path)	
                #except:
                #	mtime = None
                pathByteStr = path.encode('ascii','ignore')
                dbPath = pathByteStr.decode('utf-8','ignore')

                dbItem = database[dbPath]
                if len(dbItem) != 0:
                    dbMd5,dbSize,dbMtime,dBMd5_quick,dbMode = dbItem
                    if (dbSize != size) or (dbMtime != mtime):
                        #Different Time: Add
                        strText = "{}.".format(oct(mode))+" {}".format(dbPath) + "<>> {}".format(mtime)+" {}".format(size)+" "*100
                        database[dbPath] = (None,size,mtime,None,mode)
                    else:
                        #Nothing Changed, however update database to add new data from stats, i.e. mode updates
                        database[dbPath] = (dbMd5,size,mtime,dBMd5_quick,mode)
                        strText = None
                else:
                    #No previous data... add it.
                    strText = "{}.".format(oct(mode))+"{}".format(dbPath) + "--> {}".format(mtime)+" {}".format(size)+" "*100
                    database[dbPath] = (None,size,mtime,None,mode)
        print()
    return database,pathList
    
def updatePathList(database, search_dirs,ignoreAboveSize=None):
    pathList = []
    for search_dir in search_dirs:
        for dbPath,dbItem in database.items():
            dbMd5,dbSize,dbMtime,dBMd5_quick,dbMode = dbItem
            if ignoreAboveSize is not None:
                if dbSize > ignoreAboveSize:
                    continue
            if search_dir in dbPath:
                pathList.append(dbPath)
    return database,pathList

def plotHistogram(sizes,duplicates=None,database=None,plotDistributionFile=None,plotTitle=None,log=True):
    #import numpy as np
    import matplotlib.pyplot as plt
    import math
    global args
    print()
    print("Setting up plots....")
    #n,bins,patches = plt.hist(x,50,normed=1,facecolor='g',alpha=0.75)
    x = []
    y = []
    bytesSaved = []

    maxSize = 0
    n_bins = 100
    for size, path in sizes.items():
        if size > maxSize:
            maxSize = size
    if log:
        print (maxSize)
        logSize = math.log10(maxSize)
        print (logSize)
        binSize = logSize/n_bins
        print (binSize)
        for bin in range(0,n_bins):
            x.append(10**(bin*binSize))
            y.append(0.0)
            bytesSaved.append(0)			
    else:
        binSize = maxSize/n_bins
        for bin in range(0,n_bins):
            x.append(bin*binSize)
            y.append(0.0)
            bytesSaved.append(0)
    for size, path in sizes.items():
        for  bin in range(0,n_bins):
            if x[bin] <= size:
                y[bin] = y[bin] + (len(path)*size)
                
    for md5, paths in duplicates.items():
        if len(paths) > 1:
            pathByteStr = paths[0].encode('ascii','ignore')
            dbPath = pathByteStr.decode('utf-8','ignore')
            dbItem = database[dbPath]
            dbMd5,dbSize,dbMtime,dBMd5_quick,dbMode = dbItem
            for  bin in range(0,n_bins):
                if x[bin] <= dbSize:
                    bytesSaved[bin] = bytesSaved[bin] + (len(paths)- 1)*dbSize
    
    #if plotDistributionFile is not None:
    #	plt.ion()		#Turn interactive mode on
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.semilogx(x,y,'b-',x,bytesSaved,'r.')
    #ax1.semilogx(x,y,'b-')
    #ax2.semilogx(x,bytesSaved,'r.')
    ax1.set_xlabel('Sizes of files')
    ax1.set_ylabel('Frequency of all files')
    ax2.set_ylabel('Frequency of duplicates space saving')
    if plotTitle is None:
        strText = 'Histogram of Sizes on Disk'
        #for arg in args:
        #	strText += "\n" + str(arg)
        plt.title(strText)	
        plt.suptitle(str(args), y=1.05, fontsize=8)		
    else:
        plt.title(title)
    #plt.text(60,0.25,r'$\mu=100,\ \sigma=15$')
    #plt.axis([40,160,0,0.03])
    plt.grid(True)
    if plotDistributionFile is not None:
        plt.savefig(plotDistributionFile)
    else:
        plt.show() #block = False
    print("Done")

def findDuplicates(database,pathList,plotDistribution=False,plotDistributionFile=None):
    #Double checking file sizes
    sizes = defaultdict(list)
    print ()
    print ("Looking for same size files")
    print ()
    #Todo print hystogram
    lenPathList = len(pathList)
    lenProgressUpdate = int(lenPathList/50)
    progress = 0
    for path in pathList:
        pathByteStr = path.encode('ascii','ignore')
        dbPath = pathByteStr.decode('utf-8','ignore')
        dbItem = database[dbPath]
        if len(dbItem) == 5:
            dbMd5,dbSize,dbMtime,dBMd5_quick,dbMode = dbItem
        else:
            print ("Incorrect dbItemLength")
            print (dbItem)
            break
        sizes[dbSize].append(path)
        progress += 1
        if (progress%lenProgressUpdate==0):
            printProgressBar(progress,lenPathList)
    printProgressBar(progress,lenPathList)
    lenSize = len(sizes)
    lenProgressUpdate = int(lenSize/50)
    print ()
    print (" Sizes Matched --> ", lenSize)
    print ()
        
    #Do Quick MD5 Checksum on first batch
    md5Quicks = defaultdict(list)
    print ("Looking for same quick MD5s files...")
    print ()
    progress = 0
    strText = ""
    calculateMd5 = False
    for size,paths in sizes.items():
        progress += 1
        if len(paths) > 1:
            for path in paths:
                pathByteStr = path.encode('ascii','ignore')
                dbPath = pathByteStr.decode('utf-8','ignore')
                dbItem = database[dbPath]
                dbMd5,dbSize,dbMtime,dBMd5_quick,dbMode = dbItem
                calculateMd5 = False
                if dBMd5_quick is None:
                    calculateMd5 = True
                else:
                    if len(dBMd5_quick) <= 0:
                        calculateMd5 = True
                if calculateMd5:
                    try:
                        md5_quick = md5checksum(path,1)
                    except:
                        md5_quick = "00--00--00--00--00--00--00--00--"
                    strText = "{}".format(md5_quick) + "==> {}".format(dbPath)+ " "*100
                    database[dbPath] = (None,dbSize,dbMtime,md5_quick,dbMode)
                else:
                    strText = " "*100 
                    md5_quick = dBMd5_quick
                md5Quicks[md5_quick].append(path)
        if (progress%lenProgressUpdate==0) or calculateMd5:
            printProgressBar(progress,lenSize,suffix=strText[0:100]) 
    strText = " "*100
    printProgressBar(progress,lenSize,suffix=strText[0:100]) 
        
    print ()
    lenMd5Quicks = len(md5Quicks)
    lenProgressUpdate = int(lenMd5Quicks/500)
    print (" MD5Quick List Length --> ", lenMd5Quicks)
    print ()
    
    #Do Full MD5 Checksum on second batch
    print ("Looking for same Full MD5s files!")
    print ()
    md5database = defaultdict(list)
    progress = 0
    for md5,paths in md5Quicks.items():
        progress += 1
        if len(paths) > 1:
            for path in paths:
                pathByteStr = path.encode('ascii','ignore')
                dbPath = pathByteStr.decode('utf-8','ignore')
                dbItem = database[dbPath]
                dbMd5,dbSize,dbMtime,dBMd5_quick,dbMode = dbItem
                #Check if need to calculate.
                calculateMd5 = False
                if dbMd5 is None:
                    calculateMd5 = True
                else:
                    if len(dBMd5_quick) <= 0:
                        calculateMd5 = True
                    if calculateMd5:
                        if dbSize < 1024*1024:
                            calculateMd5 = False
                            dbMd5 = dBMd5_quick
                if calculateMd5:
                    try:
                        dbMd5 = md5checksum(path,0)
                    except:
                        dbMd5 = "00--00--00--00--00--00--00--00--"
                    strText = "{}".format(dbMd5) + "==> {}".format(dbPath)+ " "*100
                else:
                    strText = " "*100
                database[dbPath] = (dbMd5,dbSize,dbMtime,md5_quick,dbMode)
                md5database[dbMd5].append(path)
        if (progress%lenProgressUpdate==0) or calculateMd5:
            printProgressBar(progress,lenMd5Quicks,suffix=strText[0:100])
    strText = " "*100
    printProgressBar(progress,lenMd5Quicks,suffix=strText[0:100]) 		

    print ()
    lenMD5db = len(md5database)
    print (" MD5 Full List Length --> ", lenMD5db)
    print ()
    if (plotDistribution):
        plt = plotHistogram(sizes,md5database,database,plotDistributionFile)
    return database,md5database

def saveDuplicates(database, duplicates, outputCSV=None):
    deleteList = []
    lenDuplicates = len(duplicates)
    lenProgressUpdate = int(lenDuplicates/50)
    progressLines = 0
    duplicatesFound = 0
    duplicatesFilesFound = 0
    bytesToBeSaved = 0
    if outputCSV is not None:
        print ("Export Duplicates to ",outputCSV)
        with open(outputCSV,"w",newline='') as f_csv:
            csvWriter = csv.writer(f_csv,delimiter='\t')
            for md5, paths in duplicates.items():
                progressLines +=1
                if len(paths) > 1:
                    duplicatesFound += 1
                    for path in paths:
                        duplicatesFilesFound +=1
                        pathByteStr = path.encode('ascii','ignore')
                        dbPath = pathByteStr.decode('utf-8','ignore')
                        dbItem = database[dbPath]
                        #print (path,dbItem)
                        dbMd5,dbSize,dbMtime,dBMd5_quick,dbMode = dbItem
                        if dbMode is not None:
                            mode = oct(dbMode)
                        else:
                            mode = None
                        csvWriter.writerow([md5,mode,dbPath,dbSize,dbMtime,dBMd5_quick])
                        
                    bytesToBeSaved += (len(paths)- 1)*dbSize
                    if (progressLines%lenProgressUpdate==0):
                        printProgressBar(progressLines,lenDuplicates)
        printProgressBar(progressLines,lenDuplicates)
        print ()
        print (" Duplicates Found --> ", duplicatesFound)
        print (" Total Duplicates Files Found --> ", duplicatesFilesFound)
        print (" Estimated Saved Disk Space --> ", bytesToBeSaved)
        print (" Estimated Saved Disk Space --> ", humanfriendly.format_size(bytesToBeSaved,binary=True))
        print ()

def loadDuplicates(duplicates=None, inputCSV=None):
    deleteList = []
    progressLines = 0
    duplicatesFound = 0
    duplicatesFilesFound = 0
    deleteItemsCount = 0
    bytesToBeSaved = 0
    if inputCSV is not None:
        print ("Import Duplicates from ",inputCSV)
        print ("Loading MD5s duplicates only --> overwriting existing MD5 duplicate structure")
        print ()
        md5database = defaultdict(list)
        progress = 0
        
        with open(inputCSV) as f_csv:
            csvReader = csv.reader(f_csv,delimiter='\t')
            try:
                for row in csvReader:
                    lenRow = len(row)
                    if lenRow == 0:
                        continue
                    if lenRow == 1:
                        if row[0].startswith('#'):
                            continue	
                    if lenRow != 6:
                        print (lenRow)
                        return None
                        continue
                    dbItem = row
                    md5,mode,dbPath,dbSize,dbMtime,dBMd5_quick = dbItem
                    md5database[md5].append(dbPath)
                    duplicatesFilesFound += 1

            except (KeyboardInterrupt, SystemExit):
                print()
                print("Keyboard break / System Exit called")
                print("Using original duplicates and not loaded ones!!!")
                return duplicates
        lenMd5database = len(md5database)
        print ()
        print (" Duplicates CSV Len --> ", lenMd5database)
        print (" Total Duplicates Files Found --> ", duplicatesFilesFound)
        print ()
        return md5database
    return duplicates

def generateDeleteList(duplicates, outputDeleteCSV=None,doNotDeleteList=None,priorityList=None,verbose = False):
    print ("Applying rule to duplicates for deleting ")
    if duplicates is None:
        print ("Error! No Diplicates in generateDeleteList(...)")
        return
    deleteList = defaultdict(list)
    lenDuplicates = len(duplicates)
    lenProgressUpdate = int(lenDuplicates/50)
    progressLines = 0
    
    # TODO: Add progress bar + cleanup
    for md5, paths in duplicates.items():
        progressLines +=1
        if len(paths) > 1:
            keepitPath = None
            # Determine if a path should be kept.
            if (keepitPath is None):
                if doNotDeleteList is not None:
                    for doNotDeletePath in doNotDeleteList:
                        if (keepitPath is None):
                            for path in paths:
                                if path.startswith(doNotDeletePath[0]):
                                    keepitPath = path
                                    if verbose:
                                        print ("\tKeepDoNotDelete:", keepitPath)
                                    break
            # Sort through priority list for preference of kept.
            if (keepitPath is None):
                for priorityPath in priorityList:
                    if (keepitPath is None):
                        for path in paths:
                            if path.startswith(priorityPath[0]):
                                keepitPath = path
                                if verbose:
                                    print ("\tKeepPriority:", keepitPath)
                                break
            # Search through all duplicates
            maxLenPath = 0
            tmpList = defaultdict(list)
            for path in paths:
                lenPath = len(path.split('\\'))
                tmpList[lenPath].append(path)
                if lenPath > maxLenPath:
                    maxLenPath = lenPath
                #print (maxLenPath,lenPath,path)

            #Look for highest up in folder structure, since this is the one we need to worry about.
            for lenPath in range(0, maxLenPath+1): 
                for path in tmpList[lenPath]:
                    # Check do not delete list.
                    for doNotDelete in doNotDeleteList:
                        if path.startswith(doNotDelete[0]):
                            if verbose:
                                print ("\t\tSkipped:",path)
                            continue
                    #If no priorty assinged, assign with smaller path length index
                    if keepitPath is None:
                        keepitPath = path
                        if verbose:
                            print ("\tKeep:", keepitPath)
                        continue
                    #If the keepit path have been defined, and this is the current poth, do not add it.
                    if keepitPath == path:
                        continue
                    #All checks done... and no exceptions. Add to list
                    deleteList[keepitPath].append(path)
                    if verbose:
                        print ("\t\t",path)
            if verbose:
                print ("-------------Next---------------")
        if (progressLines%lenProgressUpdate==0):
            printProgressBar(progressLines,lenDuplicates)
    printProgressBar(progressLines,lenDuplicates)
    print (" Items to be deleted -->", len(deleteList))

    print ("Export Duplicates to ",outputCSV)
    print ("Writing Files to be deleted CSV File:", outputDeleteCSV)
    progressLines = 0
    lenDeleteList = len(deleteList)
    lenProgressUpdate = int(lenDeleteList/50)
    if outputDeleteCSV is not None:
        with open(outputDeleteCSV,"w",newline='') as f_csv:
            csvWriter = csv.writer(f_csv,delimiter='\t')
            for keepItPath, paths in deleteList.items():
                progressLines +=1
                for path in paths:
                    if verbose:
                        print (path, "-->", keepItPath)
                    try:
                        csvWriter.writerow([keepItPath, path])
                    except:
                        print ("Error",path.encode('ascii','ignore').decode('utf-8','ignore'), "-->", keepItPath.encode('ascii','ignore').decode('utf-8','ignore'))
                        csvWriter.writerow([keepItPath.encode('ascii','ignore').decode('utf-8','ignore'), path.encode('ascii','ignore').decode('utf-8','ignore')])
                if (progressLines%lenProgressUpdate==0):
                    printProgressBar(progressLines,lenDeleteList)
        printProgressBar(progressLines,lenDeleteList)
    print (" Done!")
    return deleteList

def loadDeleteList(outputDeleteList = None):
    #Clear any previous deleteList
    deleteList = defaultdict(list)
    if outputDeleteList is not None:
        sizeDatabase = os.path.getsize(outputDeleteList)
        progressPosition = 0
        progressLines = 0
        print ("Importing Delete List: ",outputDeleteList)
        with open(outputDeleteList) as f_csv:
            csvReader = csv.reader(f_csv,delimiter='\t')
            try:
                for row in csvReader:
                    lenRow = len(row)
                    if lenRow != 2:
                        progressPosition += 1
                        continue						
                    progressPosition += lenRow + 1
                    keepItPath = row[0]
                    path = row[1]
                    deleteList[keepItPath].append(path)
                    #print(keepItPath, "==> ",path)
            except (KeyboardInterrupt, SystemExit):
                print()
                print("Keyboard break / System Exit called")
                print ("Database Size: ",len(deleteList))
                return None				
    return deleteList

def processDeleteList(deleteList,processDeleteListLog,processDeleteListErrorLog,dryRun = True):
    printOn = False
    if deleteList is None:
        return None
    if processDeleteListLog is None:
        print ("Will not process deleted files without a log file")
        return None
    if processDeleteListErrorLog is None:
        print ("Will not process deleted files without a log file")
        return None

    progressLines = 0
    lenDeleteList = len(deleteList)
    lenProgressUpdate = int(lenDeleteList/5000)	
    print ("lenDeleteList=",lenDeleteList)
    for keepItPath in deleteList:
        #Interlocking / Failsafe for to be set true before deleting the file.
        __can_delete = False
        progressLines +=1
        if (progressLines%lenProgressUpdate==0) or dryRun:
            strText = keepItPath.encode('ascii','ignore').decode('utf-8','ignore')
            strText = strText + " "*100
            if dryRun:
                strText = ">DryRun< " +strText
            printProgressBar(progressLines,lenDeleteList,suffix = strText[0:100])
        if progressLines < 0:
            #Get out of jail... for debugging
            break
        if printOn:
            print ("="*80)
            print ("File to Keep:", keepItPath.encode('ascii','ignore').decode('utf-8','ignore'))
        
        #Check if file to keep is still valid.
        try:
            fileToKeepStats = os.stat(keepItPath)
            if printOn:
                print ("	StatsSize:",fileToKeepStats.st_size)
        except:
            if printOn:
                print ("	Error Loading this file... skip all entries for this file")
            try:
                with open(processDeleteListErrorLog,"a") as f:
                    f.write("Error Loaded\t"+keepItPath+"\n")
                    f.close()
            except:
                print ("Error writing Error log!!")
                return None
            continue
        if "findDuplicates" in keepItPath:
            continue
        if ".lnk" in keepItPath:
            continue
        if dryRun:
            keepItPathMd5 = "00--00--00--00--00--00--00--00--"
        else:
            keepItPathMd5 = md5checksum(keepItPath,0)
        if printOn:
            print ("	MD5:",keepItPathMd5)
            
        for fileToDelete in deleteList[keepItPath]:
            __can_delete = False
            #The file is now about to be deleted.
            #1. Check if file is still present
            if printOn:
                print ("	File to Delete:", fileToDelete)
            try:
                fileToDeleteStats = os.stat(fileToDelete)
                if printOn:
                    print ("		StatsSize:",fileToDeleteStats.st_size)
            except:
                if printOn:
                    print ("		Error Loading this file... skip")
                try:
                    with open(processDeleteListErrorLog,"a") as f:
                        f.write("Error Loading\t"+keepItPath+"\t"+fileToDelete+"\n")
                        f.close()
                except:
                    print ("Error writing Error log!!")
                    return None
                continue
            if (fileToKeepStats.st_size == fileToDeleteStats.st_size):
                if dryRun:
                    fileToDeleteMd5 = "00--00--00--00--00--00--00--00--"
                else:
                    fileToDeleteMd5 = md5checksum(fileToDelete,0)
                if keepItPathMd5 == fileToDeleteMd5:
                    __can_delete = False
                    #2. Create a file / link to the file that is kept.
                    if printOn:
                        print ("			==>", fileToDelete)
                    linkOfDeletedFile = fileToDelete+".findDuplicates"
                    if printOn:
                        print ("				==>", linkOfDeletedFile)
                    if not dryRun:
                        try:
                            with open(linkOfDeletedFile,"a") as f_text:
                                f_text.write("duplicate can be found at\n")
                                f_text.write("  ==> "+keepItPath+"\n")
                                f_text.close()
                            __can_delete = True
                        except:
                            print ("Error writing text link")
                            continue # Skip any futher processing, since no point in deleteing when the link file cannot be created.
                    else:
                        if dryRun:
                            __can_delete = True
                            if printOn:
                                print ("----->DryRun<------")
                    if __can_delete:
                        try:
                            if not dryRun:
                                os.remove(fileToDelete)
                                if printOn:
                                    print ("				==> Done!")
                            else:
                                if printOn:
                                    print ("				==> ----->DryRun<------")
                            try:
                                with open(processDeleteListLog,"a") as f:
                                    f.write("Delete\t"+keepItPath+"\t"+fileToDelete+"\n")
                                    f.close()
                            except:
                                print ("Error writing Error log!!")
                                return None

                        except:
                            try:
                                with open(processDeleteListErrorLog,"a") as f:
                                    f.write("Error to Delete\t"+keepItPath+"\t"+fileToDelete+"\n")
                                    f.close()
                            except:
                                print ("Error writing Error log!!")
                                return None
                            print ("				==> Error Deleting File!")
                else:
                    try:
                        with open(processDeleteListErrorLog,"a") as f:
                            f.write("Error: MD5\t"+keepItPath+"\t"+fileToDelete+"\n")
                            f.close()
                    except:
                        print ("Error writing Error log!!")
                        return None
            else:
                try:
                    with open(processDeleteListErrorLog,"a") as f:
                        f.write("Error: Size\t"+keepItPath+"\t"+fileToDelete+"\n")
                        f.close()
                except:
                    print ("Error writing Error log!!")
                    return None
    printProgressBar(progressLines,lenDeleteList)
                        


if __name__ == "__main__":
    # https://docs.python.org/3/library/argparse.html
    import argparse
    parser = argparse.ArgumentParser(description="Find Duplicates in various directories and try to optimize for easy management")
    # Positional Arguments
    parser.add_argument('search_dirs', metavar='dirs', default=None, nargs='+', help="List of directories to search for duplicates. May be one or may. If the first value passe here is None, then no directories will be searched, and only stored databases will be used.")
    # Option Arguments
    parser.add_argument('--outputCSV',dest='outputCSV',default=None, help="File for storing output results, i.e. list of duplicates")
    parser.add_argument('--inputCSV',dest='inputCSV',default=None, help="Use stored output to speedup delete list generation") 
    parser.add_argument('--outputCSVdataBase',dest='outputCSVdataBase',default=None, help="File for storing various data for keeping files states, i.e. does not have to calculate MD5 checksums, etc")
    parser.add_argument('--inputCSVdataBase',dest='inputCSVdataBase',default=None, help="File for to be used for references on new searches.") 
    parser.add_argument('--ignoreAboveSize',dest='ignoreAboveSize',type=int,default=None, help="If size is above this value in bytes then ignoreMD5checksum calculation") 
    parser.add_argument('--skipStatsUpdate',dest='skipStatsUpdate',action='store_true', help="If Stats should not be updated, then skip this part.") 
    parser.add_argument('--plotDistribution',dest='plotDistribution',action='store_true', help="Plot sizes in Hystrogram") 
    parser.add_argument('--plotDistributionFile',dest='plotDistributionFile',default=None, help="Save Hystorgam to file") 
    parser.add_argument('--doNotDeleteList',dest='doNotDeleteList',default=None, help="List of files or directories which may never be deleted") 
    parser.add_argument('--priorityList',dest='priorityList',default=None, help="List of files or directories which determines priorities, i.e. the earlier in the list the higher the priority of not deleting files in this structure. Priority in general is determined as follows: 1. doNotDeleteList, 2. priorityList 3. Closeness to root.") 
    parser.add_argument('--outputDeleteList',dest='outputDeleteCSV',default=None, help="List of files or directories Can be deleted based on rules and priorities.") 
    parser.add_argument('--inputDeleteList',dest='inputDeleteCSV',default=None, help="Populate Delete List from CSV file. Will overwrite any other delete list") 
    parser.add_argument('--processDeleteListLog',dest='processDeleteListLog',default=None, help="Log file for deleted files") 
    parser.add_argument('--processDeleteListErrorLog',dest='processDeleteListErrorLog',default=None, help="Error Log file for deleted files") 
    parser.add_argument('--notDryRun',dest='notDryRun',action='store_true', help="If this is not set then no files will be deleted. This is a failsafe to check deleted items before commiting") 

    args = parser.parse_args()
    print (args)
    
    search_dirs = args.search_dirs
    if search_dirs[0].upper() == "NONE":
        search_dirs = None
    inputCSVdataBase = args.inputCSVdataBase
    outputCSVdataBase = args.outputCSVdataBase
    outputCSV = args.outputCSV
    inputCSV = args.inputCSV
    skipStatsUpdate = args.skipStatsUpdate
    plotDistribution = args.plotDistribution
    plotDistributionFile = args.plotDistributionFile
    ignoreAboveSize = args.ignoreAboveSize
    doNotDeleteList = args.doNotDeleteList
    priorityList = args.priorityList
    outputDeleteCSV = args.outputDeleteCSV
    inputDeleteCSV = args.inputDeleteCSV
    processDeleteListLog = args.processDeleteListLog
    processDeleteListErrorLog = args.processDeleteListErrorLog
    dryRun = not args.notDryRun

    #######################################################################################################
    timeProgress = []
    duplicates = None
    theDataBase = None
    pathList = None

    #Loading Existing databases
    timeProgress.append(("Start", time.time()))
    theDataBase = loadTheDataBase(inputCSVdataBase)
    
    #Add to database if directories are added
    if search_dirs is not None:
        if len(search_dirs) > 0:
            timeProgress.append(("DatabaseLoad", time.time()))
            if not skipStatsUpdate:
                theDataBase,pathList = updateStats(theDataBase, search_dirs,ignoreAboveSize)
                timeProgress.append(("UpdateStats",time.time()))
            else:
                theDataBase,pathList = updatePathList(theDataBase, search_dirs,ignoreAboveSize)
                timeProgress.append(("UpdatePathListFromDB",time.time()))

    #Find duplicates
    if theDataBase is not None:
        if pathList is not None:
            theDataBase,duplicates = findDuplicates(theDataBase,pathList,plotDistribution,plotDistributionFile)
            timeProgress.append(("FindingDuplicate",time.time()))
            saveTheDataBase(theDataBase, outputCSVdataBase) 
            timeProgress.append(("DatabaseSave", time.time()))
            saveDuplicates(theDataBase, duplicates, outputCSV)
            timeProgress.append(("DuplicatesSave", time.time()))

    #Load / Add Duplicates from CSV file
    duplicates = loadDuplicates(duplicates, inputCSV)
    timeProgress.append(("DuplicatesLoad", time.time()))
    
    #Generate Delete List from duplicates
    if duplicates is not None:
        doNotDeleteList = csvToList(doNotDeleteList)
        priorityList = csvToList(priorityList)
        timeProgress.append(("LoadingOfLists", time.time()))
        generateDeleteList(duplicates, outputDeleteCSV,doNotDeleteList,priorityList)
        timeProgress.append(("GenerateDeleteList", time.time()))
    if inputDeleteCSV is not None:
        deleteList = loadDeleteList(inputDeleteCSV)
        timeProgress.append(("LoadDeleteList", time.time()))
        processDeleteList(deleteList,processDeleteListLog,processDeleteListErrorLog,dryRun)
        timeProgress.append(("ProcessDeleteList", time.time()))	
    #Display analysis stats	
    for i in range(0,len(timeProgress)):
        (description,time) = timeProgress[i]
        if i == 0:
            timePrev = time
            continue
        dTime = time-timePrev
        print(description,humanfriendly.format_timespan(dTime))
        timePrev = time
    exit()
