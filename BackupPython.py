import distutils.dir_util 
import os
import sys
import time
from shutil import ignore_patterns, copytree, copy, copy2, Error, copystat
import ConfigParser
import io

#date = time.strftime(" %Y-%m-%d")
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





class Backup:
     def __init__(self):
         self.backupconfig = {
            'source': [],
            'destination': [] ,
            'preserve_attribute':[],
            'ignored_items': [],
            'update': [],
            'date_time':[]
         }
         self.check_list = ['source', 'destination',  'preserve_attribute', 'ignored_items', 'update', 'date_time']
         self.WINDOWS = "win32"
         self.iteration = 0


     def check_config_file(self, config):
          config = self.open_file_config(config)
          for section in config.sections():
               for options in config.options(section):
                    if options in self.check_list:
                         item = config.get(section, options)
                         if options == "source":
                              if not(os.path.isdir(config.get(section, options))):
                                   raise ValueError('The %s option in backup is not a folder. Check The Configuration File' %options)
                               
                         elif options == "destination":
                              item = os.path.split(os.path.abspath(options))[0]                 
                              if not(os.path.isdir(item)):
                                   raise ValueError('The %s option in backup is not a folder. Check The Configuration File' %options)
                         else:
                              if options == "update" or options == "date_time" or options == "preserve_attribute":
                                   if not(item == str(0) or item == str(1)or (not item)):
                                        raise ValueError('The %s option in %s is not 0 or 1. Check The Configuration File' %(options, section))
                    else:
                         raise ValueError('The %s in %s is not a valid option. Check The Configuration File' % (options, section))

     def open_file_config(self, config):
         with open(config) as f:
              sample_config = f.read()
         config = ConfigParser.RawConfigParser(allow_no_value=True)
         config.readfp(io.BytesIO(sample_config))
         return config

     def load_file_config (self, config):
         config = self.open_file_config(config)
         for section in config.sections():
             for options in config.options(section):
                 item = config.get(section, options)
                 if options in ("update", "date_time", "preserve_attribute"):
                     if not item:
                         self.backupconfig [options].append(1)
                     else:
                         self.backupconfig [options].append(int(item))
                 elif (options == "ignored_items"):
                     if type(item) is str:
                         self.backupconfig [options].append(item.split(","))
                     else:
                         self.backupconfig [options].append(None)                                  
                 else:
                     self.backupconfig [options].append(item)
                         




    # Print iterations progress
     def printProgressBar (self,iteration, total):
          percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
          filledLength = int(length * iteration // total)
          bar = fill * filledLength + '-' * (length - filledLength)
        #sys.stdout.write('\r')
          sys.stdout.write('\r %s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix))
          if iteration == total:
              print('\n \n')
        #sys.stdout.flush()


    # get folder size, file number and folder number 
     def get_attributes(self, path):
          folderAttributes = [0,0,0]
          for dirpath, dirnames, filenames in os.walk(path):
               folderAttributes[1]+= len(filenames)
               folderAttributes[2] += len(dirnames)
               for f in filenames:
                    fp = os.path.join(dirpath, f)
                    folderAttributes[0] += os.path.getsize(fp)
             #print   folderAttributes 
          return folderAttributes

     def ignoreFiles (self, src, ignore):
          names = os.listdir(src)
          if ignore is not None:
               ignored_names = ignore(src, names)
               #print ignored_names
          else:
               ignored_names = set()
          return ignored_names


     def checking_attributes(self, src, dst, ignore):
          names = os.listdir(src)
          if ignore is not None:
               ignored_names = ignore(src, names)
          else:
               ignored_names = set()
          for item in os.listdir(src):
               if item in ignored_names:
                   continue
               item_path = os.path.join(src, item)
               dest_path = os.path.join(dst, item)
             #check if item is directory
               if os.path.isdir(item_path):
                   print (" checking %s folder attributes \n" %item)
                   srcFolderAttributes = get_attributes(item_path)
                   print " Source folder attributes: size = %s byte, folder number = %s, files number %s" %(srcFolderAttributes[0], srcFolderAttributes[2], srcFolderAttributes[1])  
                   dstFolderAttributes = get_attributes(dest_path)
                   print " Destination folder attributes: size = %s byte, folder number = %s, files number %s" %(dstFolderAttributes[0], dstFolderAttributes[2], dstFolderAttributes[1])
                   if srcFolderAttributes == dstFolderAttributes:
                        print (" SUCCESS: The %s folder attributes are equal in source and destination \n \n" %item)
                   elif srcFolderAttributes[0] != dstFolderAttributes[0] and srcFolderAttributes[1] != dstFolderAttributes[1] and srcFolderAttributes[2] != dstFolderAttributes[2]:
                        raise (" ERROR: The %s has different size, files and folders number in source and destination \n" %item)
                
                   elif srcFolderAttributes[0] != dstFolderAttributes[0]:
                        raise (" ERROR: The %s has different size in source and destination \n \n " %item)

                   elif srcFolderAttributes[1] != dstFolderAttributes[1]:
                        raise (" ERROR: The %s has different files number in source and destination \n \n " %item)
              
                   else:
                        raise (" ERROR: The %s has different folders number in source and destination \n \n " %item)

               else:
                    print (" checking %s file attributes \n" %item)
                    if os.path.getsize (item_path) == os.path.getsize (dest_path):
                         print (" SUCCESS: The %s file attributes are equal in source and destination \n \n" %item)
                    else:
                         raise (" ERROR: The %s has different size in source and destination \n \n " %item)







     def copyFile (self, src, dst, preserve_attributes):
          if (preserve_attributes == 1):
               copy2(src, dst)
          else:
               copy(src, dst)
          self.iteration+=1
          printProgressBar(self.iteration, totalFiles)

        


     def copyOptionChecking(self, src, dst, preserve_attributes, update):
          if (update == 1):
               if os.path.isfile(dst):
                    if os.stat(src).st_mtime > os.stat(dst).st_mtime:
                         self.copyFile(src,dst, preserve_attributes)
               else:
                   self.copyFile(src,dst, preserve_attributes)
          else:
               self.copyFile(src,dst, preserve_attributes)
          self.iteration+=1
          printProgressBar(self.iteration, totalFiles)


    #A custom copytree
     def my_copytree(self, src, dst, symlinks=False, ignore=None, preserve_attributes = 1, update=0):
          names = os.listdir(src)
          if ignore is not None:
               ignored_names = ignore(src, names)
          else:
               ignored_names = set()
          if not os.path.isdir(dst):
               os.makedirs(dst)
          errors = []
          for name in names:
               if name in ignored_names:
                    continue
               srcname = os.path.join(src, name)
               dstname = os.path.join(dst, name)
               try:
                    if symlinks and os.path.islink(srcname):
                         linkto = os.readlink(srcname)
                         os.symlink(linkto, dstname)
                    elif os.path.isdir(srcname):
                         self.my_copytree(srcname, dstname, symlinks, ignore, preserve_attributes, update)
                    else:
                         self.copyOptionChecking(srcname, dstname, preserve_attributes, update)
                # XXX What about devices, sockets etc.?
               except (IOError, os.error) as why:
                    errors.append((srcname, dstname, str(why)))
            # catch the Error from the recursive copytree so that we can
            # continue with other files
               except Error as err:
                    errors.extend(err.args[0])
          try:
               copystat(src, dst)
          except WindowsError:
               # can't copy file access times on Windows
               pass
          except OSError as why:
               errors.extend((src, dst, str(why)))
          if errors:
               raise Error(errors)

     def start_backup (self):
          i = 0
          totalFiles = 0
          date = time.strftime(" %Y-%m-%d")

          for src, dst in zip (self.backupconfig['source'], self.backupconfig ['destination']):
               if len(self.backupconfig['ignored_items']) > 1:
                    ignored_names = ignoreFiles (src, ignore= my_ignore_patterns(self.backupconfig['ignored_items'][i]))
               else:
                    ignored_names = ignoreFiles (src, ignore= my_ignore_patterns(self.backupconfig['ignored_items'][0]))
                  
              
               for dirpath, dirnames, filenames in os.walk(src):
                    for f in filenames:
                         if not (f in ignored_names):
                              totalFiles += 1 
                  # Initial call to print 0% progress
              #totalFiles = totalFiles - len(ignoreFiles (src, ignore_patterns('.test*')))
               print " copying the %s folder... \n" % os.path.split(os.path.abspath(src))[0]
               print totalFiles
               print self.backupconfig ['date_time']

               if len(self.backupconfig ['date_time']) > 1:
                    if self.backupconfig ['date_time'][i] == 1:
                         dst = self.backupconfig ['destination'][i] + str(date)
               else:
                    if self.backupconfig ['date_time'][0] == 1:
                         dst = self.backupconfig ['destination'][i] + str(date)
                  

              
               printProgressBar(iteration, totalFiles)
               if len(self.backupconfig['preserve_attribute']) > 1:
                    my_copytree(src, dst, symlinks=False, ignore= my_ignore_patterns(self.backupconfig['ignored_items'][i]),preserve_attributes = self.backupconfig['preserve_attribute'][i], update = self.backupconfig['update'][i])
               else:
                    my_copytree(src, dst, symlinks=False, ignore= my_ignore_patterns(self.backupconfig['ignored_items'][0]),preserve_attributes = self.backupconfig['preserve_attribute'][0], update = self.backupconfig['update'][0])
               totalFiles = 0
               iteration = 0
               i += 1

         


     def check_backup (self):
          i = 0
          for src, dst in zip (source, destination):
               if len(self.backupconfig['ignored_items']) > 1:
                    checking_attributes(src, dst, ignore= self.backupconfig['ignored_items'][i])
               else:
                    checking_attributes(src, dst, ignore= self.backupconfig['ignored_items'][0])
               i +=1






myBackup = Backup ()


if not(os.path.isfile("config.ini")):
    config = str(0)
    while ((not(config == str(1))) and (not(os.path.isfile(config)))):
        config = raw_input("insert config file path or type 1 to exit \n")
    if config == str(1):
        sys.exit()
else:
    config = "config.ini"



print " Checking Config File \n \n"
try:
    myBackup.check_config_file(config)
except ValueError as err:
    print(err.args)
    sys.exit()

myBackup.load_file_config(config)

myBackup.start_backup()



print " Starting Backup \n \n"
start_time = time.time()








print " The backup has been completed, congratulations!!! \n \n"

print " Time to excute the backup: %s seconds \n \n" % ((time.time() - start_time))


raw_input (" Type something to continue \n \n")

print (" Starting backup checking \n \n ")


try:
     myBackup.check_backup ()
except ValueError as err:
    print(err.args)
    sys.exit()









print (" The backup checking has been completed successfully, congratulations!!! \n \n")

raw_input (" Type something to exit")
         


