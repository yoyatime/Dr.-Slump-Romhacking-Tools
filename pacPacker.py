#########################################################################
# Combines files specified in an xml file into a .PAC files for PS1     #
# game "Dr. Slump"                                                      #
# Place .PAC files into sourceDump folder                               #
# Place xml files in same folder as this script                         #
#########################################################################

# Dr. Slump uses 4 byte little endian pointers followed by 4 byte little 
# endian filesizes


import sys    
import os
import io
from pathlib import Path
import compress
import xml.etree.ElementTree as ET


def byteAlign(value):
    ret = value + ((4 - (value % 4) % 4)) 
    return ret

def packPac(node):
    #Size of table section for this node
    tableSize = int(node[0].get('dataOffset'))

    outputStream = io.BytesIO(bytes(tableSize))

    #Current data insertion position
    dataCursor = tableSize

    #recurse into embedded pac files
    for subNode in node.findall('pac'):
        packPac(subNode)

    #compress subnode and add to this node's table and data section
    for subNode in node:
        if subNode.tag == 'lzss':


            lzssPacked = compress.compressChunk("gen/" + subNode.get('fileName') + '.uncomp')
            
            #Update XML

            subNode.attrib['dataOffset'] = str(dataCursor)
            dataOffset = str(dataCursor)
            subNode.attrib['size'] = str(len(lzssPacked))
            compressedSize = str(len(lzssPacked))
            subNode.attrib['uncompressedSize'] = str(Path("gen/" + subNode.get('fileName') + '.uncomp').stat().st_size)
            uncompressedSize = str(Path("gen/" + subNode.get('fileName') + '.uncomp').stat().st_size)
            tableOffset = subNode.get('tableOffset')


            #write table entry
            outputStream.seek(int(tableOffset))
            outputStream.write(bytes([int(dataOffset) & 0xFF]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF00) >> 8]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF0000) >> 16]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF000000) >> 24]))

            outputStream.write(bytes([int(compressedSize) & 0xFF]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF00) >> 8]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF0000) >> 16]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF000000) >> 24]))


            #write data
            outputStream.seek(dataCursor)
            outputStream.write(lzssPacked + bytes((4 - (int(compressedSize) % 4)) % 4))

            #update cursor,  Align data offset to 4 byte grid
            dataCursor += byteAlign(int(compressedSize))

        else:
            rawToWrite = open("gen/" + subNode.get('fileName'), "rb").read()

            subNode.attrib['dataOffset'] = str(dataCursor)
            dataOffset =  str(dataCursor)
            subNode.attrib['size'] = str(len(rawToWrite))
            compressedSize = str(len(rawToWrite))
            tableOffset = subNode.get('tableOffset')

            #write table entry
            outputStream.seek(int(tableOffset))
            outputStream.write(bytes([int(dataOffset) & 0xFF]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF00) >> 8]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF0000) >> 16]))
            outputStream.write(bytes([(int(dataOffset) & 0xFF000000) >> 24]))

            outputStream.write(bytes([int(compressedSize) & 0xFF]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF00) >> 8]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF0000) >> 16]))
            outputStream.write(bytes([(int(compressedSize) & 0xFF000000) >> 24]))


            #write data
            outputStream.seek(dataCursor)
            outputStream.write(rawToWrite + bytes((4 - (int(compressedSize) % 4)) % 4))

            #update cursor,  Align data offset to 4 byte grid
            dataCursor += byteAlign(int(compressedSize))

    #write output file
    
    if os.path.exists("gen/" + node.get('fileName')):
        os.remove("gen/" + node.get('fileName'))


    pacOutput = open("gen/" + node.get('fileName'), "w+b")
    outputStream.seek(0)
    pacOutput.write(outputStream.read())  


for sourceFile in os.listdir("sourceDump/"):
    
    if sourceFile.endswith(".PAC"):#$DEBUG
        tree = ET.parse('xml/' + sourceFile + ".xml")
        root = tree.getroot()
    
        packPac(root)
