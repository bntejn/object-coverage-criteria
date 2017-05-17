'''
Created on Feb 7, 2011

@author: Matt

Helper functions for CSV files
'''

import os
import sys
import copy
import string

class CsvFile(object):
	__lines = []
	
	#Reads a CSV file
	def __init__(self, arg):
		if not arg == None:
			if isinstance(arg, basestring):
				self.__lines = []
				self.readFormulaFile(arg)
			elif isinstance(arg, list):
				if not self.convertList(arg):					
					raise Exception("Not appropriate CSV list: must be list of lists, items as strings -- could not convert")
			else:
				raise Exception("Bad data type, aborting CSV construction")			

	# checks that lst is list of lists, with individual items being strings, and try to convert otherwise
	def convertList(self, lst):
		self.__lines = []
		for l in lst:
			if isinstance(l, list):
				convert = []
				for i in l:					
					if not isinstance(i, basestring):
						convert.append(str(i))
					else:
						convert.append(i)
				self.__lines.append(convert)
			elif isinstance(l, basestring):
				self.__lines.append([l])
			else:
				return False
				
		return True
	
	def getLines(self):
		return self.__lines

	def readFormulaFile(self, fileName):
		f  = open(fileName)
		for l in f:
			self.__lines.append(l.strip().split(","))
		f.close()
		
	def writeCsvFile(self, outputFile):
		f = open(outputFile, "w")
		for l in self.__lines:
			f.write(",".join(l)+"\n")
		f.close()
