#!/usr/bin/env python
from __future__ import print_function, absolute_import, division
import fuse 
import logging
import linecache
from collections import defaultdict
from errno import ENOENT,EROFS,ENOTEMPTY
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
class Node(object):
     def __init__(self,data):
             self.data=data
             self.child=[]
     def add(self,obj):
             self.child.append(obj)
def insert(node,parent,value):
    if parent=='/':
        q=Node(value)
        node.add(q) 
    else:
        if(len(node.child)!=0):
            for c in node.child:
                if c.data==parent:
                    val=Node(value)
                    c.add(val)
        
                else :
                    insert(c,parent,value) 
def replace(node,parent,new,old):
    if node.data==parent:
        for c in node.child:
            if c.data==old:
                c.data=new
                return               
    elif len(node.child)!=0:
            for j in node.child:
                return replace(j,parent,new,old) 
                  
def disp(node):
    print('parent',node.data)
    if(len(node.child)!=0):
        for i in node.child:
            print('child ',i.data)
        for i in node.child:
            if(len(i.child)!=0):
                print('\n')
                disp(i)       
def disp_child(node,parent):
        global li
        if node.data==parent:
            for c in node.child:
               li.append(c.data)
        
        elif len(node.child)!=0:
            for j in node.child:
                disp_child(j,parent)
def check_child(node,parent):
    if node.data==parent:
            j=0
            for c in node.child:
               j=+1
            if j>0:
                return 1
        
    elif len(node.child)!=0:
            for j in node.child:
                return check_child(j,parent)

def remove(node,parent,child):
       
        if parent=='/':
                print("HI")
                for c in node.child:
                    #print(c+"Hi")
                    if c.data==child:
                        print("HI")
                        node.child.remove(c)
        else :
            for c in node.child:
                if c.data==parent: 
                    for i in c.child:
                       if(i.data==child): 
                            c.child.remove(i)
                            return
                else :
                    remove(c,parent,child) 
if not hasattr(__builtins__, 'bytes'):
    bytes = str

class Memory(LoggingMixIn,Operations):
    def __init__(self):
        self.files = {}
        self.data = defaultdict(bytes)
        self.fd = 0
        self.path_inode={}
        now = time()
        ino=writeDiskInode('/')
        blk=getBlock('/')
        attr = {
            'st_ino': ino,
            'st_mode': S_IFDIR | 0o755,
            'st_nlink': 2,
            'st_uid': 1000,
            'st_gid': 1000,
            'st_atime': now,
            'st_mtime': now,
            'st_ctime': now,
            'st_blk':blk,
            'st_size':4096
            }

        self.files['/'] = attr
                                                                                                                                                                                                                                                                                                                                                                                                                                        
        writeInodeMetaData(self.files['/'],1,'/')
        self.persistent()
        
    def persistent(self):
        global n
        with open('disk.txt','r') as file:
            data=file.readlines()
        file_name_disk=[]
        inode_addr=int(data[2].strip('\n').split()[1])
        data_addr=int(data[3].strip('\n').split()[1])
        while inode_addr<38:
            stat=data[inode_addr].strip('\n').split()
            if(len(stat)>5):
                attr={
                'st_ino': int(stat[0]),
                'st_mode': int(stat[1]),
                'st_nlink': int(stat[2]),
                'st_uid': int(stat[3]),
                'st_gid': int(stat[4]),
                'st_atime': float(stat[5]),
                'st_mtime': float(stat[6]),
                'st_ctime': float(stat[7]),
                'st_blk':int(stat[8]),
                'st_size':int(stat[9])
                }
                unicod=unicode(stat[10],'utf-8')
                self.files[unicod]=attr
                self.data[unicod]=''
                file_name_disk.append(unicod)
                self.path_inode[unicod]=int(stat[0])
            inode_addr+=1
        while data_addr<70:
            block=data[data_addr].strip('\n').split()
            if len(block)>2:
                value=block[1].replace('$','\n')
                self.data[unicode(block[2],'utf-8')]=value
                print("HEEE",value)
            data_addr+=1
        i=1
        
        print("file_disk_name",file_name_disk)
        while(len(file_name_disk)!=1):
            file_name=[]
            file_name.extend(file_name_disk[i].lstrip('/').split('/'))
            if len(file_name)==1:
                insert(n,'/',file_name[0])
            else:
                leng=len(file_name)
                insert(n,file_name[leng-2],file_name[leng-1])
            file_name_disk.remove(file_name_disk[i])
            
        disp(n)    
          
         
       
    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid

    def create(self, path, mode):
        pa=path.split('/')
        global n    
        if len(pa)==2:
            insert(n,'/',pa[len(pa)-1])
        else :
            insert(n,pa[len(pa)-2],pa[len(pa)-1])  
        ino=writeDiskInode(path)
        blk=getBlock(path)
        now=time()
        attr = {
            'st_ino': ino,
            'st_mode': S_IFREG | mode,
            'st_nlink': 1,
            'st_uid': 1000,
            'st_gid': 1000,
            'st_atime': now,
            'st_mtime': now,
            'st_ctime': now,
            'st_blk':blk,
            'st_size':0
            }

        self.files[path] = attr
        self.data[path]=''
        writeInodeMetaData(self.files[path],ino,path)
        self.fd += 1
        self.path_inode[path]=ino
        return self.fd

    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(ENOENT)

        return self.files[path]

    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

    def mkdir(self, path, mode):
        pa=path.split('/')
        global n    
        if len(pa)==2:
            insert(n,'/',pa[len(pa)-1])
        else :
            insert(n,pa[len(pa)-2],pa[len(pa)-1])  
        now=time()    
        ino=writeDiskInode(path)
        blk=getBlock(path)
        attr = {
            'st_ino': ino,
            'st_mode': S_IFDIR | mode,
            'st_nlink': 2,
            'st_uid': 1000,
            'st_gid': 1000,
            'st_atime': now,
            'st_mtime': now,
            'st_ctime': now,
            'st_blk':blk,
            'st_size':4096
            }

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        self.files[path] = attr
        self.files[path]['st_ino']=ino
        self.data[path]=''
        #self.files[path]['st_gid']='root'
        self.files['/']['st_nlink'] += 1
        self.files[path]['st_blk']=blk
        self.path_inode[path]=ino
        writeInodeMetaData(self.files[path],ino,path)
        
        

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        self.files[path]['st_size']=len(self.data[path])
        return self.data[path][offset:offset + size]
        
    def readdir(self, path, fh):
        global li
        global n
        if path=="/":
            li=[]
            disp_child(n,'/')
            cp=li[:]
            li=[]   
        else:
            pa=path.split('/')
            li=[]
            disp_child(n,pa[len(pa)-1])
            print("parent  =  ",pa[len(pa)-1])
            cp=li[:]
            print("cp=",cp)
            li=[]
        disp(n)
        
        return ['.', '..'] + cp

    def readlink(self, path):
        return self.data[path]

    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
        
        self.files[new] = self.files.pop(old)
        self.data[new]=self.data.pop(old)
        self.path_inode[new]=self.path_inode.pop(old)
        global n
        pa=old.split('/')
        pa1=new.split('/')
        global n    
        if len(pa)==2:
            replace(n,'/',pa1[len(pa1)-1],pa[len(pa)-1])
        else :
            replace(n,pa[len(pa)-2], pa1[len(pa1)-1] ,pa[len(pa)-1])
              
        writeInodeMetaData(self.files[new],self.files[new]['st_ino'],new)
        writeBlock(self.files[new],self.data[new],new)	
        res=check_child(n,pa1[len(pa1)-1])
        if res==1:
          for key in self.files:
            if pa[len(pa)-1] in key:
                temp=key.replace(pa[len(pa)-1],pa1[len(pa1)-1])
                print(temp)                     
                self.files[temp]=self.files.pop(key)
                writeInodeMetaData(self.files[temp],self.files[temp]['st_ino'],temp)
                writeBlock(self.files[temp],self.data[temp],temp)
    
    def rmdir(self, path):
        pa=path.split('/')
        global n
        if (len(pa)== 2) :
            res=check_child(n,pa[len(pa)-1])
            print(res)
            if res!=1:
                remove(n,'/',pa[len(pa)-1])
            
        else:
            res=check_child(n,pa[len(pa)-1])
            if res!=1:
                remove(n,pa[len(pa)-2],pa[len(pa)-1])
        if res!=1:
            ino=self.path_inode[path]
            addBackInode(ino,self.files[path]['st_blk'])
            self.files.pop(path)
            self.files['/']['st_nlink'] -= 1
        else:
            raise FuseOSError(ENOTEMPTY)

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        pa=target.split('/')
        global n    
        if len(pa)==2:
            insert(n,'/',pa[len(pa)-1])
        else :
            insert(n,pa[len(pa)-2],pa[len(pa)-1])
        now=time()    
        ino=writeDiskInode(target)
        blk=getBlock(target)
        attr = {
            'st_ino': ino,
            'st_mode': S_IFLNK | 0o777,
            'st_nlink': 2,
            'st_uid': 1000,
            'st_gid': 1000,
            'st_atime': now,
            'st_mtime': now,
            'st_ctime': now,
            'st_blk':blk,
            'st_size':len(source)
            }
        self.files[target]=attr
        
        self.data[target]=source
        self.path_inode[target]=ino
        writeBlock(self.files[target],self.data[target],target)
        writeInodeMetaData(self.files[target],ino,target)

    def truncate(self, path, length, fh=None):
        self.data[path] = self.data[path][:length]
        self.files[path]['st_size'] = length

    def unlink(self, path):
        pa=path.split('/')
        global n
        if (len(pa)== 2) :
            remove(n,'/',pa[len(pa)-1])
        else:
            remove(n,pa[len(pa)-2],pa[len(pa)-1])
        ino=self.path_inode[path]
        addBackInode(ino,self.files[path]['st_blk'])
        remove_block(path,self.files[path])
        self.files.pop(path)
        
    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):
        self.data[path] = self.data[path][:offset] + data
        self.files[path]['st_size'] = len(self.data[path])
        ino=self.files[path]['st_ino']
        writeInodeMetaData(self.files[path],ino,path)
        writeBlock(self.files[path],self.data[path],path)
        
        return len(data)
        
def writeBlock(files,dataa,path):
        with open('disk.txt','r') as file:
            data=file.readlines()
        blk=files['st_blk']
        block_addr=(data[3].strip('\n').split())
        block_start=int(block_addr[1])
        dataa=dataa.replace('\n','$')
        data[block_start+blk-1]=str(blk)+" "+dataa+' '+path+"\n"
        with open('disk.txt','w') as file:
            file.writelines(data)
        
def remove_block(path,files):
        with open('disk.txt','r') as file:
            data=file.readlines()
        blk=files['st_blk']
        block_addr=(data[3].strip('\n').split())
        block_start=int(block_addr[1])
        data[block_start+blk-1]=str(blk)+'\n'
        with open('disk.txt','w') as file:
            file.writelines(data)
            
def writeDiskInode(path):
        with open('disk.txt','r') as file:
                data=file.readlines()
        ino=0
        ino_bit_map_addr=data[0].strip('\n').split()
        ino_bit_map_addr=int(ino_bit_map_addr[1]) 
        inode_list=data[ino_bit_map_addr].strip('\n').split()
        if path != '/' :
                ino=inode_list.pop(0)
        else:
                ino=1
        data[ino_bit_map_addr]=' '.join(inode_list)+'\n'
       
        with open('disk.txt','w') as file:
            file.writelines(data)
        return int(ino)
        
def writeInodeMetaData(files,ino,path):
        with open('disk.txt','r') as file:
            data=file.readlines()
            inode_addr=data[2].split(' ')[1]
            string=str(ino)+' '+str(files['st_mode'])+' '+str(files['st_nlink'])+' '+str(files['st_uid'])+' '+str(files['st_gid'])+' '+str(files['st_mtime'])+' '+str(files['st_atime'])+' '+str(files['st_ctime'])+' '+str(files['st_blk'])+' '+str(files['st_size'])+' '+path+' '+'\n'
            data[ino+int(inode_addr)-1]=string
        with open('disk.txt','w') as file:
            file.writelines(data)
        return 0
        
def addBackInode(ino,blk):
        with open('disk.txt','r') as file:
            data=file.readlines()
        ino_bit_map_addr=int(data[0].strip('\n').split()[1]) 
        data_bit_map_addr=int(data[1].strip('\n').split()[1])
        inode_list=data[ino_bit_map_addr].strip('\n').split(' ')
        inode_list.append(str(ino)+'\n')
        
        data[ino_bit_map_addr]=' '.join(inode_list)
        inode_addr=data[2].split(' ')[1]
        data[ino+int(inode_addr)-1]=str(ino)+'\n'
        
        block_list=data[data_bit_map_addr].strip('\n').split(' ')
        block_list.append(str(blk)+'\n')
        
        data[data_bit_map_addr]=' '.join(block_list)
        block_addr=data[3].split(' ')[1]
        data[blk+int(block_addr)-1]=str(blk)+'\n'
        with open('disk.txt','w') as file:
            file.writelines(data)
      
def getBlock(path):
        with open('disk.txt','r') as file:
            data=file.readlines()
        data_bit_map_addr=int(data[1].strip('\n').split()[1]) 
        block_list=data[data_bit_map_addr].strip('\n').split(' ')
        if path!='/':
        	blk=block_list.pop(0)
        else:
                blk=1
        data[data_bit_map_addr]=' '.join(block_list)+'\n'
       
        with open('disk.txt','w') as file:
            file.writelines(data)
        return int(blk)

  
        
if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)
    n=Node('/')
    li=[]
    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(Memory(), argv[1], foreground=True)
 
