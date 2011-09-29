    '''
Created on Sep 29, 2011

@author: sebastian.treu@gmail.com
'''
import sys
import select
import multiprocessing
import time
import ConfigParser
import os
import re

configParser = ConfigParser.RawConfigParser({'ask':'no'})
configParser.optionxform = str
configParser.read(os.path.expanduser('~')+'/.pylogin')
timeout = int(configParser.get("general", "time"))
defaultSection = configParser.get("general", "default")
for section in [val for val in configParser.sections() if val != "general"]:
    if section == defaultSection:
        defaultIndex = configParser.sections().index(section) - 1

class Color(object):
    no_color     = '\033[0m'
    red_color    = '\033[1;31m'
    blue_color   = '\033[1;34m'
    yellow_color = '\033[1;32m'

    def colorPrint(self, color, s):
        print color + s + self.no_color

class Timer(multiprocessing.Process):
    def __init__(self, count, section):
        multiprocessing.Process.__init__(self, None)
        self.count  = count
        self.section = section

    def run(self):
        while(self.count > 0):
            sys.stdout.write("\b\b"+str(self.count)+"]")
            sys.stdout.flush()
            time.sleep(1)
            self.count -= 1
        launchDefault(self.section)

def launchDefault(section):
    if section is not None:
        defaultSection = section
    if bool(configParser.getboolean(defaultSection, "ask")):
        print "Are you sure? [y/N] "
        if re.match("[yY]|[Yy][eE][sS]\n", sys.stdin.readline()) is None:
            return
    cmd = configParser.get(defaultSection, "exec").split(' ')
    os.execvp(cmd[0], cmd[1:])

def main():
    color = Color()
    for section in [val for val in configParser.sections() if val != "general"]:
        index = configParser.sections().index(section) - 1
        color.colorPrint(getattr(color, configParser.get(section, "color")+"_color"),
                         str(index)+") "+section.capitalize()+ (" (default)" if index == defaultIndex else "")
                        )
    sys.stdout.write("\nChoose a session [Default is "+str(defaultIndex)+" in   ")
    sys.stdout.flush()
    work = Timer(timeout, defaultSection)
    work.start()
    r, w, e = select.select([sys.stdin], [], [], timeout)
    if len(r) != 0:
        work.terminate()
        index = sys.stdin.readline()
        if index == "\n":
            launchDefault(None)
        else:
            launchDefault(configParser.sections()[int(index) + 1])
    else:
        print "bye"


if __name__ == "__main__":
    main()
