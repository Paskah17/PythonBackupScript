__author__ = "Pasquale Scola"
__copyright__ = "Copyright 2017, Backup Project"
__license__ = "MIT License https://opensource.org/licenses/MIT"
__version__ = "1.0"
__maintainer__ = "Pasquale Scola"
__email__ = "Pasquale.scola@telecomitalia.it"


import distutils.dir_util 
import os
import sys
import time

date = time.strftime(" %Y-%m-%d")

#src= "C:\\mySourcePath"
#dst = "C:\\myDestinationPath"+str(date)
thresholdString ="."
#The zero value indicate the first char
subStringCheck = 0


#Process bar 
"""
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        percent     - Optional  : percent iteration(float)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
"""
decimals = 1
prefix = 'Progress:'
suffix = 'Complete'
fill = '#'
length = 50

# Print iterations progress
def printProgressBar (iteration, total):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    #sys.stdout.write('\r')
    sys.stdout.write('\r %s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix))
    print ('\n')
    if iteration == total:
        print('\n')
    #sys.stdout.flush()

# get folder size, file number and folder number 
def get_attributes(path):
    folderAttributes = [0,0,0]
    for dirpath, dirnames, filenames in os.walk(path):
        folderAttributes[1]+= len(filenames)
        folderAttributes[2] += len(dirnames)
        for f in filenames:
            fp = os.path.join(dirpath, f)
            folderAttributes[0] += os.path.getsize(fp)
    print   folderAttributes 
    return folderAttributes



#Backup
print (" Starting Pasquale Backup \n \n")
start_time = time.time()
iteration = 0
totalFolders = len([name for name in os.listdir(src) if os.path.isdir(os.path.join(src, name)) and name[subStringCheck] != thresholdString])
# Initial call to print 0% progress
printProgressBar(iteration, totalFolders)

for item in os.listdir(src):
    #get item path ---> src + item ("item" contain the name of the element)... join example --> C:\\mypath + dirname = C:\\mypath\\dirname
    item_path = os.path.join(src, item)
    #check if item is directory and the item name doesn't start with "."
    if os.path.isdir(item_path) and item[subStringCheck] != thresholdString:
        dest_path = os.path.join(dst, item)
        #To Windows is better to use xcopy function
        if sys.platform == "win32":
            #in xcopy function if the folder name has some spaces the function doen't copy the folder. Adding " " the above problem is resolted 
            item_path = '"'+item_path+'"'
            dest_path = '"'+dest_path+'"'
            #os.system (doc->https://docs.python.org/2/library/os.html) is a function to run operative system command (in this case for windows)
            #xcopy is a windows machine function to copy file (doc -> https://ss64.com/nt/xcopy.html)
            print(" copying the %s folder... \n" % item)
            os.system('xcopy'+' '+str(item_path)+' '+str(dest_path)+' /s  /i  /y /q /e > nul')
            iteration += 1
        else:
            #copy the folder to destination doc --> https://docs.python.org/2/distutils/apiref.html
            distutils.dir_util.copy_tree(item_path, dest_path)
        #Process bar update
        printProgressBar(iteration, totalFolders)
        
print (" The backup has been completed, congratulations!!! \n \n")

print (" Time to excute the backup: %s seconds \n \n" % ((time.time() - start_time)))


raw_input (" Type something to continue \n \n")

print (" Starting backup checking \n \n ")

totalFoldersDst = len([name for name in os.listdir(dst) if os.path.isdir(os.path.join(dst, name)) and name[subStringCheck] != thresholdString])

if (totalFolders  != totalFoldersDst):
    print (" ERROR: the number of source folder is different respect to backup destination folder number !!!!")
    raw_input (" ERROR: Type something to exit")
    sys.exit()

for item in os.listdir(src):
    item_path = os.path.join(src, item)
    #check if item is directory and the item name doesn't start with "."
    if os.path.isdir(item_path) and item[subStringCheck] != thresholdString:
        print (" checking %s folder attributes \n" %item)
        dest_path = os.path.join(dst, item)
        srcFolderAttributes = get_attributes(item_path)
        print " Source folder attributes: size = %s byte, folder number = %s, files number %s" srcFolderAttributes[0] srcFolderAttributes[2] srcFolderAttributes[1]  
        dstFolderAttributes = get_attributes(dest_path)
        print " Destination folder attributes: size = %s byte, folder number = %s, files number %s" dstFolderAttributes[0] dstFolderAttributes[2] dstFolderAttributes[1]
        if srcFolderAttributes == dstFolderAttributes:
            print (" SUCCESS: The %s folder attributes are equal in source and destination \n \n" %item)
        elif srcFolderAttributes[0] != dstFolderAttributes[0] and srcFolderAttributes[1] != dstFolderAttributes[1] and srcFolderAttributes[2] != dstFolderAttributes[2]:
            print (" ERROR: The %s has different size, files and folders number in source and destination \n" %item)
            raw_input (" ERROR: Type something to exit")
            sys.exit()
        elif srcFolderAttributes[0] != dstFolderAttributes[0]:
            print (" ERROR: The %s has different size in source and destination \n \n " %item)
            raw_input (" ERROR: Type something to exit")
            sys.exit()
        elif srcFolderAttributes[1] != dstFolderAttributes[1]:
            print (" ERROR: The %s has different files number in source and destination \n \n " %item)
            raw_input (" ERROR: Type something to exit")
            sys.exit()
        else:
            print (" ERROR: The %s has different folders number in source and destination \n \n " %item)
            raw_input (" ERROR: Type something to exit")
            sys.exit()

print (" The backup checking has been completed successfully, congratulations!!! \n \n")

raw_input (" Type something to exit")




