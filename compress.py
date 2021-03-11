#########################################################################
# Compresses LZSS data for PS1 game "Dr. Slump"                         #
# Usage: compress.py [INPUT FILE]                                       #
#########################################################################

# Dr. Slump uses references with 11-bit offsets and 5-bit lengths,
# corresponding to a 2048-byte window, and reference lengths in the range
# 3..34 bytes.

import sys    
import os
from pathlib import Path

#sys.argv = [sys.argv[0], "S01_M00C.PAC.out.bin"]

inputFile = open(sys.argv[1], "rb")

if os.path.exists(sys.argv[1]+".slump"):
  os.remove(sys.argv[1]+".slump")

outputFile = open(sys.argv[1]+".slump", "w+b")

WSIZE = 0b100000000000 + 1   # window size

MAX_REF_LEN = 34  # maximum copy length
MIN_REF_LEN = 3   # minimum copy length

#write header - '01 [2 BYTE LITTLE ENDIAN UNCOMPRESSED FILESIZE] 00 00'
outputFile.write(b'\x01')
fileSize = Path(inputFile.name).stat().st_size
outputFile.write(bytes([fileSize & 0xFF]))
outputFile.write(bytes([(fileSize & 0xFF00)>>8]))
outputFile.write(b'\x00\x00')

#create input stream
input = inputFile.read()

#write compressed blocks until file size reached
bytesWritten = 0
windowLeft = 0
windowRight = 0
while bytesWritten < fileSize:
  controlBlock = 0
  controlBlockCursor = 1

  writeBuffer = b''

  #write chunk of 16 references and/or literals
  while controlBlockCursor <= 0b1000000000000000 and  bytesWritten < fileSize:

    referenceFound = False
    #check all valid upcoming string lengths for matches in our dictionary window
    for copyLength in range(MAX_REF_LEN, MIN_REF_LEN, -1):
      
      #Check if search window extends past EOF
      if bytesWritten + copyLength >= fileSize:
        #windowRight = fileSize
        continue
      else:
        windowRight = bytesWritten + copyLength

      searchString = input[bytesWritten:windowRight]

      #Search valid window for result
      searchResult = input.find(searchString, windowLeft, windowRight - 1)

      if searchResult != -1:
        
        #create reference block with pattern XXXXXYYYYYYYYYYY (X is copy length, Y is reference offset)
        referenceBlock = (bytesWritten - searchResult - 1) | ((copyLength-3) << 11)

        writeBuffer += bytes([referenceBlock & 0xFF]) + bytes([(referenceBlock & 0xFF00)>>8])
        referenceFound = True

        #add reference bit to control block
        controlBlock |= controlBlockCursor
        bytesWritten += copyLength
        break

    #write 1 literal byte from cursor if no match found    
    if referenceFound == False:
      writeByte = bytes([input[bytesWritten]])
      writeBuffer += writeByte
      bytesWritten += 1

    #update window
    if bytesWritten > WSIZE:
      windowLeft = bytesWritten - WSIZE
    
    controlBlockCursor <<= 1

  #write control block and buffer
  outputFile.write(bytes([controlBlock & 0xFF]) + bytes([(controlBlock & 0xFF00)>>8]) + writeBuffer)

#cleanup
outputFile.close()
inputFile.close()