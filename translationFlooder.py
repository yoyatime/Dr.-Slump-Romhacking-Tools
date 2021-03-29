#Searches for duplicate translation entries and adds them to untranslated files
#

import sys    
import os
from pathlib import Path
import shutil



translatedLines = []
originalLines = []

def populateMap(translatedFolder, originalsFolder):
    for sourceFile in os.listdir(translatedFolder):
        translatedFile = open(translatedFolder + sourceFile, 'r', encoding='utf8')

        translatedFile.readline()

        for line in translatedFile:
            if '@' not in line and line != '':
                translatedLines.append(line)

        originalFile = open(originalsFolder + sourceFile, 'r', encoding='utf8')

        for line in originalFile:
            if '@' not in line and line != '':
                originalLines.append(line)

        translatedFile.close()
        originalFile.close()


def propagateTranslations(targetFolder, outputFolder):
    
    numberChanges = 0

    for root, dirs, files in os.walk(targetFolder):
        for targetFile in files:
            openTarget = open(targetFolder + targetFile, 'r', encoding='utf8')

            targetData = openTarget.readlines()

            for line in range(0, len(targetData)):
                if '@' not in targetData[line] and targetData[line] != '' and targetData[line] != '\n' and targetData[line] in originalLines:
                    index = originalLines.index(targetData[line])
                    targetData[line] = translatedLines[index]

                    
                    print(translatedLines[index])
                    print(' ')
                    numberChanges += 1

            outputFile = open(outputFolder + targetFile, 'w', encoding='utf8')
            outputFile.writelines(targetData)

            outputFile.close()
            openTarget.close()

        print(numberChanges)
        break
                
                

populateMap('translations/Done/', 'translations/Originals/')

propagateTranslations('translations/', 'translations/')