#List of my objects...
OBJECTS = TestSuite.o
FLAGS=-std=c++11

default : all

all: analysis

#the dependencies and compile instructions....
analysis:  TestSuite.o Analyzer.o analysis.cpp
	g++  TestSuite.o Analyzer.o analysis.cpp -o ff_analyzer $(FLAGS)
	-@rm Analyzer.o TestSuite.o
	-@cp ff_analyzer ../

analysis-multiMutant:  TestSuite.o analysis_multiMutant.cpp
	g++  TestSuite.o analysis_multiMutant.cpp -o analysis_multiMutant $(FLAGS)

TestSuite.o:  TestSuite.h TestSuite.cpp
	g++  -c TestSuite.cpp $(FLAGS)

Analyzer.o: Analyzer.h Analyzer.cpp
	g++ -c Analyzer.cpp $(FLAGS)

#Clean up stuff 
clean:
	-@rm core > /dev/null 2>&1
	-@rm analysis > /dev/null 2>&1
	-@rm ${OBJECTS} > /dev/null 2>&1
