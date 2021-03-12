#########################################################################
# Separates .pac files into individual .lzss files for PS1 game         #
# "Dr. Slump"                                                           #
# Usage: pacUnpacker.py [INPUT FILE]                                    #
#########################################################################

# Dr. Slump uses 4 byte little endian pointers followed by 4 byte little 
# endian filesizes


import sys    
import os
from pathlib import Path
import uncompress
import xml.etree.ElementTree as ET



LZSS_IDENTIFIER = 1

#sys.argv = [sys.argv[0], "S01_M00C.PAC"]

root = ET.Element('source')

root.attrib['fileName']="S01_M00C.PAC"
root.attrib['offset']="0"
root.attrib['size']=str(Path("S01_M00C.PAC").stat().st_size)

def writeEntry(fileStream, node):
    #first 4 bytes form pointer to lzss data chunk or embedded .pac file
    lzssPtr = int.from_bytes(fileStream.read(4), "little", signed=False)
    #last 4 bytes form size of lzss data chunk or embedded .pac file
    lzssFileSize = int.from_bytes(fileStream.read(4), "little", signed=False)

    #Skip blank entries
    if lzssPtr + lzssFileSize != 0:
        returnPos = fileStream.tell()
        fileStream.seek(lzssPtr)
        
        #read identifying byte
        chunkID = int.from_bytes(fileStream.read(1), "little", signed = False)
        
        if chunkID == LZSS_IDENTIFIER:
            chunkType = "lzss"
        else:
            chunkType = "pac"

        #initialize leaf element
        elem = ET.SubElement(node, chunkType)
        #add offset attribute
        #elem.attrib['offset'] = str(returnPos - int(node.get("offset")) - 8)
        elem.attrib['offset'] = str(returnPos - 8)
        elem.attrib['fileName'] = node.get('fileName') + '.' + elem.get('offset') + '.' + chunkType
        elem.attrib['size'] = str(lzssFileSize)
        elem.attrib['dataOffset'] = str(lzssPtr)
        fileStream.seek(returnPos)

    return lzssPtr


def findData(currNode):
    inputFile = open(currNode.get("fileName"), "rb")

    dataOffset = 0
    indexCursor = 0
    
    #find first pointer in file to find end of pointer block
    while True:
        searchResult = writeEntry(inputFile, currNode)
        #Skip entries with values of 0
        if  searchResult != 0:
            dataOffset = searchResult
            indexCursor += 8
            break
        indexCursor += 8

    #iterate over all pointers in pointer block
    while indexCursor < dataOffset:
        writeEntry(inputFile, currNode)
        indexCursor += 8

    for node in currNode.findall('lzss'):
        print(node.get('fileName'))
        print(int(node.get('dataOffset')))
        uncompress.uncompressChunk(currNode.get('fileName'), int(node.get('dataOffset')), node.get('fileName'))

    for node in currNode.findall('pac'):
        print(node.get('fileName'))
        pacOutput = open(node.get('fileName'), "w+b")
        inputFile.seek(int(node.get('dataOffset')))
        pacOutput.write(inputFile.read(node.get('fileSize')))
        pacOutput.close()
        findData(node)
        


    #cleanup
    inputFile.close()



findData(root)
print(ET.tostring(root))

# Converting the xml data to byte object, 
# for allowing flushing data to file  
# stream 
b_xml = ET.tostring(root) 
  
# Opening a file under the name `items2.xml`, 
# with operation mode `wb` (write + binary) 
with open(root.get("fileName")+".xml", "wb") as f: 
    f.write(b_xml) 