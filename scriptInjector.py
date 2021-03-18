############################################################################
# Injects script files into container files for PS1 game                   #
# "Dr. Slump"                                                              #
# Searches 'translations' folder and updates files in the 'script' folder  #                                                                     #
############################################################################

import sys    
import os
from pathlib import Path
import shutil
import xml
import xml.etree.ElementTree as ET
import xml.dom.minidom
import dataConversion


def injectScript:
    for script in os.listdir("translations/"):
        scriptFile = open("translations/" + script, 'rb')

    #firstline format: @@[FILENAME]@@[NUMBER OF ENTRIES]@@[DATA START]@@[DATA END]
    firstLine = scriptFile.readline().split('@@')

    fileName = firstLine[1]
    numEntries = firstLine[2]
    dataStart = firstLine[3]
    dataEnd = firstLine[4]

    