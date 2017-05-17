from TestCoverageData import TestCoverageData
from CsvFile import CsvFile
import copy
import os
import sys
import random

class getReduced(object):

	def main():
		cover = TestCoverageData(sys.argv[1])
		suites = cover.generateReducedSubsets(int(sys.argv[3]))
		out = CsvFile(suites)
		out.writeCsvFile(sys.argv[2])		

	if __name__ == '__main__':
		main()	
