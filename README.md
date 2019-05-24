# Os-file-system-project
File system using fuse

command to run the file ---> python2 memory.py tmp
python2 -> i am using python 2 version
memory.py -> contains all thye logic part 
tmp -> empty directory on which the file system has to be mounted

My file system project is also persistent which is done using a txt file
for more details read the document file

discription of disk.txt file
line 1: super block with inode bit map
line 2:super block with data bit map
line 3:inode start and end addresses
line 4:data block start and end addresses
line 5:inode number that are free and they can be used to create new files
line 6:data block numbers that are free (these numbers are actually the line numbers of the file)

  
