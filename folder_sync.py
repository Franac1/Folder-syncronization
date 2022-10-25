import sys
import os
import shutil
import hashlib
import time


class FolderSync:
    def __init__(self, source, destination, log):
        self.source = source
        self.destination = destination
        self.sourceDirs = set()
        self.destDirs = set()
        self.sourceHashes = {}
        self.destHashes = {}
        self.f = open(log, "a")

    def scanSourceFolder(self):
        self.sourceHashes = {}
        self.sourceDirs = set()
        self.sourceHashes, self.sourceDirs = self.scanFiles(self.source)

    def scanDestFolder(self):
        self.destHashes = {}
        self.destDirs = set()
        self.destHashes, self.destDirs = self.scanFiles(self.destination)

    def scanFiles(self, path):
        hashes = {}
        dirs = set()
        for root, directories, files in os.walk(path):
            relRoot = root.removeprefix(path)
            for fileName in files:
                with open(root+"\\"+fileName, 'rb') as file:
                    data = file.read()
                    fileCheckSum = hashlib.md5(data).hexdigest()
                    if hashes.get(fileCheckSum) == None:
                        hashes[fileCheckSum] = [relRoot, fileName]
                    else:
                        fileCheckSum = fileCheckSum + relRoot
                        hashes[fileCheckSum] = [relRoot, fileName]
            dirs.add(relRoot)
        return [hashes, dirs]

    def checkForFolders(self):
        removeList = self.destDirs - self.sourceDirs
        addList = self.sourceDirs - self.sourceDirs.intersection(self.destDirs)
        for item in removeList:
            shutil.rmtree(self.destination+"\\"+item)
            print("Removed folder recursively:", item)
            self.f.write("Removed folder recursively: " + str(item) + "\n")
        removeListHashes = []
        for item in self.destHashes:
            if self.destHashes[item][0] in removeList:
                removeListHashes.append(item)
        for item in removeListHashes:
            del self.destHashes[item]
        for item in addList:
            os.makedirs(self.destination+"\\"+item, exist_ok=True)
            print("Added folder/s:", item)
            self.f.write("Added folder recursively: " + str(item) + "\n")

    def checkFilesForChanges(self):
        sourceHashesList = self.sourceHashes.keys()
        destHashesList = self.destHashes.keys()
        for key in destHashesList:
            if key in sourceHashesList:
                if self.destHashes[key] == self.sourceHashes[key]:
                    continue
                elif self.destHashes[key][0] != self.sourceHashes[key][0]:
                    self.deleteFile(self.destHashes[key])
                    print("Deleted file:", self.destHashes[key])
                    self.f.write("Deleted file: " +
                                 str(self.destHashes[key]) + "\n")
                    self.copyFile(self.sourceHashes[key])
                    print("Copied file from source to destination",
                          self.sourceHashes[key])
                    self.f.write("Copied file from source to destination" +
                                 str(self.sourceHashes[key]))
                elif self.destHashes[key][1] != self.sourceHashes[key][1]:
                    os.rename(self.destination+"\\"+self.destHashes[key][0]+"\\"+self.destHashes[key][1], self.destination+"\\"+self.destHashes[key][0]+"\\"+self.sourceHashes[key]
                              [1])
                    print("Renamed file from " +
                          self.destHashes[key][1] + " to " + self.sourceHashes[key][1])
                    self.f.write("Renamed file from " +
                                 self.destHashes[key][1] + " to " + self.sourceHashes[key][1])

            else:
                self.deleteFile(self.destHashes[key])
                print("Deleted file", self.destHashes[key])
                self.f.write("Deleted file" + str(self.destHashes[key]) + "\n")
        addSet = sourceHashesList - destHashesList
        for item in addSet:
            self.copyFile(self.sourceHashes[item])
            print("Copied file:", self.sourceHashes[item])
            self.f.write("Copied file: " + str(self.sourceHashes[item]) + "\n")

    def deleteFile(self, attrs):
        os.remove(self.destination+"\\"+attrs[0]+"\\"+attrs[1])

    def copyFile(self, attrs):
        shutil.copy2(
            self.source+"\\"+attrs[0]+"\\"+attrs[1], self.destination+"\\"+attrs[0]+"\\"+attrs[1])


folSync = FolderSync(sys.argv[1], sys.argv[2], "log.txt")

while(True):
    folSync.scanSourceFolder()
    folSync.scanDestFolder()
    folSync.checkForFolders()
    folSync.checkFilesForChanges()
    print("===============================")
    folSync.f.write("===============================\n")
    time.sleep(float(sys.argv[3]))
