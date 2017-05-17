'''
Created on Jan 7, 2011

@author: Staats

Class representing simple test coverage data, with each test being mapped to
numbered obligations.
'''

import sys
from CsvFile import *

import copy
import random
import math

class TestCoverageData(object):
    __coverageDic = {}
    __numObligations = 0
    __satisfiableObligations = set()
    __satisfyingTests = {}
    __fileName = ""

    #Reads a formula file, resticting itself to the tests contained in (lowerBound, upperBound) if specified
    def __init__(self, fileName):
        self.__satisfyingTests = {}
        self.__coverageDic = {}
        self.__satisfiableObligations = set()
        
        if isinstance(fileName, basestring):
            if not fileName == None:
                self.__fileName = fileName
                self.readFormulaFile(fileName)
        elif isinstance(fileName, file):
                self.readOpenFormulaFile(fileName)

    def readOpenFormulaFile(self, f):
        
        line = f.readline()
        
        # counting possible obligations        
        self.__numObligations = len(line.strip().split(","))
        
        for i in range(self.__numObligations):
            self.__satisfyingTests[i] = []
        
        currentTest = 0        
        while (line != ""):
            line = line.strip().split(",")
            
            flist = []
            for i in range(len(line)):
                if line[i].lower() == "true" or line[i] == "1":
                    flist.append(i)
                    self.__satisfiableObligations.add(i)
            self.__coverageDic[currentTest] = frozenset(flist)
            
            for i in flist:
                self.__satisfyingTests[i].append(currentTest)
            
            currentTest += 1
            line = f.readline()
            
        f.close()

    #Reads a CSV representing coverage information for a test suite
    def readFormulaFile(self, filename):
        f = open(filename)
        self.readOpenFormulaFile(f)
        f.close()
    
    #Generates a reduced test suite using a simple random algorithm
    def generateRandomReducedTestSuite(self):
        tests = self.__coverageDic.keys()
        toSatisfy = copy.deepcopy(self.__satisfiableObligations)
        
        testSuite = []
        
        while (len(toSatisfy) > 0):
            t = tests[random.randint(0, len(tests)-1)]
            tests.remove(t)
            
            satisfied = self.__coverageDic[t]
            toSatisfyAfter = toSatisfy - satisfied
            
            if len(toSatisfyAfter) < len(toSatisfy):
                testSuite.append(t)
                toSatisfy = toSatisfyAfter
        
        return testSuite
                
    #Generates numSubsets random subsets  
    def generateReducedSubsets(self, numSubsets):    
        subsets = []
        
        for i in xrange(numSubsets):
            subsets.append(self.generateRandomReducedTestSuite())
        
        return subsets
    
    def getRawData(self):
        return self.__coverageDic

    def computeCoverageStatistics(self):
        covNums = []
        numTests = 0
        for test in self.__coverageDic.keys():
            numTests += 1
            covNums.append(len(self.__coverageDic[test]))
        avg = float(sum(covNums)) / float(numTests)
        
        total = float(0.0)
        for n in covNums:
            total += math.pow(float(n)-avg, 2)
        var = total / float(numTests)
        
        return (avg,var)        

    def getCoverage(self, testSuite):
        satisfied = []
        for t in testSuite:
            x = list(self.__coverageDic[t])
            satisfied.extend(x)
        return float(len(set(satisfied))) / (float(len(self.__satisfiableObligations))) * 100.0 

    def getSatisfyingTests(self):
        return self.__satisfyingTests
    
    def getSatisfiableObligations(self):
        return self.__satisfiableObligations
    
    def getMaxObligations(self):
        return self.__numObligations
    
    def getMaximumCoverage(self):
        return float(len(self.__satisfiableObligations)) / float(self.__numObligations) * 100.0

def mainGenerateReducedSuite(inputFile, number, outputFile):
    t = TestCoverageData(inputFile)
    subs = t.generateReducedSubsets(int(number))    
    suiteCsv = CsvFile(subs)            
    suiteCsv.writeCsvFile(outputFile)

def printUsage():
    print "\nUsage: python TestCoverageData.py <test suite> <num reduced> <result file>"

#Main is below
if __name__ == "__main__":
    if len(sys.argv) < 4:
        printUsage()
        exit()        
    
    mainGenerateReducedSuite(sys.argv[1],sys.argv[2],sys.argv[3])    
