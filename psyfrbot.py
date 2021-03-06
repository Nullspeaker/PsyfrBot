import _thread
import shelve
import sys
import os
import traceback
from datetime import datetime

# There's a better way to do this, yes?
#  If so, someone please fork and request a pull/open an issue with the fix.
osp=sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pluginsys
sys.path=osp

isMatch=lambda x,y: x.lower()==y.lower()

class user:
  def __init__(self,lvl):
    self.level=lvl

class botprocessor:
  def __init__(self,
      commandSym="!", #Command symbol, like "!dothings"
      configlocation="config.cfg",
      userslocation="users.dat",
      defaultError="Exception occurred or no match detected.",
      respondFunc=None,
      doLogging=True):
    self._respondFunc=respondFunc
    self.defaultError=defaultError
    self.commandSym=commandSym
    self.doLogging=doLogging
    self._ignore=[]
    self._configloc=configlocation
    self._usersloc=userslocation
    self.pluginManager=pluginsys.pluginManager()
    self.users={}
    self.config={}
    
  def ignore(self,name):
    if name.lower() not in self._ignore:
      self._ignore.append(name.lower())
  
  def saveconfig(self):
    conffile=shelve.open(self._configloc,'n')
    for i in self.config:
      self.conffile[i]=self.config[i]
    conffile.close()
  
  def loadconfig(self):
    conffile=shelve.open(self._configloc)
    for i in conffile:
      self.config[i]=conffile[i]
    conffile.close()
  
  def saveusers(self):
    usrfile=shelve.open(self._usersloc,'n')
    for i in self.users:
      usrfile[i]=self.users[i]
    usrfile.close()
  
  def loadusers(self):
    usrfile=shelve.open(self._usersloc)
    for i in usrfile:
      self.users[i]=usrfile[i]
    usrfile.close()
    
  def MsgLog(self,msg):
    if self.doLogging:
      logF=open("logs/"+"LOG_"+datetime.now().strftime("%b-%d-%Y").upper()+".txt","a+")
      logF.write(datetime.now().strftime("{%H:%M:%S} ")+msg+"\n")
      logF.flush()
      logF.close()
  
  def Save(self):
    self.saveconfig()
    self.saveusers()
  
  def Load(self):
    self.loadconfig()
    self.loadusers()
  
  def getuser(self,usrname):
    usrname=usrname.lower()
    if usrname in self.users.keys():
      return self.users[usrname]
    else:
      return None
      
  def adduser(self,usrname,lvl=0):
    usrname=usrname.lower()
    if self.getuser(usrname):
      return None
    else:
      self.users[usrname]=user(lvl)
  
  def messageparser(self,message):
    #overriding encouraged
    return message.split(" ")
  
  def get_response(self,message,usrname):
    #probably want to override if messageparser is overridden.
    self.MsgLog("["+usrname+"]: "+message)
    if not message.startswith(self.commandSym):
      return None
    SplitMsg=self.messageparser(message)
    self.adduser(usrname)
    if usrname.lower() in self._ignore and self.getuser(usrname).level!=31337:
      return None
    for plugin in self.pluginManager.getPlugins():
      if isMatch(self.commandSym+plugin.trigger,SplitMsg[0]):
        if self.getuser(usrname).level>=plugin.reqlvl:
          returned=plugin.plugin_main(self.getuser(usrname),message,self)
          if returned==None:
            return self.defaultError
          else:
            return returned
        else:
          return "Invalid permission rank."
    return self.defaultError
  
  def reply(self,message,usrname):
    if self._respondFunc==None:
      return None
    else:
      _thread.start_new_thread(
        self._respondFunc,(self.get_response(message,usrname),)
      )
      
if __name__=="__main__":
  BOTPRC=botprocessor(commandSym="!",respondFunc=print)
  BOTPRC.pluginManager.loadPlugins()
  BOTPRC.adduser("Root",lvl=31337)
  #BOTPRC.loadusers()
  #BOTPRC.saveusers()
  NAME="Root"
  print("Ready.\n  Try starting with '%shelp'"%BOTPRC.commandSym)
  while True:
    x=input("")
    BOTPRC.reply(x,NAME)
    #print(BOTPRC.get_response(x,NAME))
