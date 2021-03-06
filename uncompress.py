#########################################################################
# Uncompresses LSZZ stored data in PS1 game "Dr. Slump"                 #
# Usage: uncompress.py [INPUT FILE] [OFFSET TO START OF COMPRESSED DATA]#
# Start of compressed data pattern: 01XX00YY                            #
# XX: number of uncompressed bytes                                      #
# YY: first control block                                               #
#########################################################################
import sys    
import os

#sys.argv = [sys.argv[0], "S01_M00C.PAC", 129252]
inputFile = open(sys.argv[1], "rb")

if os.path.exists(sys.argv[1]+".out.bin"):
  os.remove(sys.argv[1]+".out.bin")

output = open(sys.argv[1]+".out.bin", "w+b")
 
#clear data to start point
offset = sys.argv[2]
inputFile.read(offset+1)

#read filesize halfword
fileSize = int.from_bytes(inputFile.read(2), "little", signed=False)

#read 2 nonfunctional bytes
dummy = inputFile.read(2)

#loop until no bytes remaining
bytesLeft = fileSize
while bytesLeft > 0:
    
    #control block determines writing of reference(1) or raw byte(0)
    controlBlock = int.from_bytes(inputFile.read(2), "little", signed=False)
    controlBlockCursor = 1

    #iterate over 16 bit long control block
    while controlBlockCursor <= 32768:
        if (controlBlock & controlBlockCursor) == 0:
            #write 1 raw byte
            output.write(inputFile.read(1))
            bytesLeft -= 1
            
        else:
            #write from reference block
            referenceBlock = inputFile.read(2)
            #Offset = first 3 bits of byte 1 on byte 2
            offsetNibble1 = int.from_bytes(referenceBlock[0:1], "little", signed=False)

            offsetNibble2 = (int.from_bytes(referenceBlock[1:2], "little", signed=False) & 7) << 8
            seekOffset = offsetNibble1 + offsetNibble2 + 1

            #Number of bytes left to copy = last 5 bits of byte 1 + 3
            copyBytes = (int.from_bytes(referenceBlock[1:2], "little", signed=False) >> 3) + 3
            bytesLeft -= copyBytes
            
            #copy all bytes
            while copyBytes > 0:
                output.seek(-seekOffset, 2)
                writeByte = output.read(1)
                output.seek(0,2)
                output.write(writeByte)
                copyBytes -= 1

        controlBlockCursor *= 2
    
inputFile.close()
output.close()