#include <iostream>
#include <fstream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sstream>
#include "TestSuite.h"


class Analyzer {
public:
	TestSuite* correctSuite;
	vector<string> mutants;
	vector<vector<int> >* suiteList;
	vector<vector<int> >* oracleList;

private:
	int** resultMatrix;
	// [mutant type][suite num][oracle num] = # of mutants caught
	map<string,map<int, map<int, int> > > mutationScoreMap;
	//[mutant type] = # of mutants seen
	map<string,int> mutantCnt;

public:
    Analyzer(string correctSuiteF, string mutantListF, string suiteListF, string oracleListF);
    ~Analyzer();
    void initResultMatrix();
    void killMutants();
    void writeResult(string outFname);
	
private:
    void processSuite(const string& line, vector<int>& suite);
    vector<vector<int> >* getSuiteList(string filename);
    void processOracle(const string& line, vector<int>& oracle, TestSuite* ts);
    vector<vector<int> >* getOracleList(string filename, TestSuite* ts);
    string getPrefix(string s);
    vector<string> getMutantList(string originalFilename, string filename);
    string processMutantName(string mutFile);
    int stringToInt(const string& line);

};

