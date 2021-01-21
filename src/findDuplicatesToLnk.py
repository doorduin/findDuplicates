import os
import win32com.client
import sys
import argparse

def doMain(fileName):
	print (fileName)
	with open(fileName) as f:
		line1 = f.readline()
		print (line1,"!")
		if "duplicate can be found at" in line1:
			line2 = f.readline()
			targetFileName = line2[6:-1]
			print (targetFileName)
	#Create Shortcut
	if(False):
		shell = win32com.client.Dispatch('WScript.shell') 
		shorty = shell.CreateShortcut(fileName+'.lnk') 
		shorty.TargetPath = os.path.join(targetFileName)
		shorty.WindowStyle = 1 
		shorty.Hotkey = "CTRL+SHIFT+F" 
		shorty.Save() 
	
	#Copy Actual File
	if(True):
		destFileName = fileName.split(".findDuplicates")[0]
		copyCmdStr = "copy %s %s" % (targetFileName, destFileName)
		print (copyCmdStr)
		os.system (copyCmdStr)
		if os.path.isfile (destFileName): print ("...Success!")
	return True

if __name__ == '__main__':
	print( "Start")
	parser = argparse.ArgumentParser(description="Converts a .findDuplicates file into a windows link")
	# Positional Arguments
	parser.add_argument('fileNames', metavar='fileNames', default=None, nargs='+', help="Files to Convert")
	args = parser.parse_args()
	fileNames = args.fileNames
	for fileName in fileNames:
		if not doMain(fileName):
			break
	print( "End")