#include <iostream>
#include <fstream>
#include <string>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <sstream>
#include "TestSuite.h"

using namespace std;

int stringToInt(const string& line) {
 istringstream buffer(line);
 int i;
 buffer>>i;
 return i;
}

string intToString(const int num) {
 stringstream buffer;
 buffer<<num;
 string s;
 buffer>>s;
 return s;
}

void processSuite(const string& line, vector<int>& suite) {
	string cur;
	for (int i = 0; i < line.size(); i++) {
		if (line[i] == ',') {
			suite.push_back(stringToInt(cur));
			cur = "";
		} else if (line[i] != ' ') {
			cur += line[i];
		}
	}
	
	//ending
	if (cur != "") {
		suite.push_back(stringToInt(cur));
	}
}

vector<vector<int> >*  getSuiteList(string filename) {
	vector<vector<int> >* suiteList = new vector<vector<int> >();

	ifstream inFile(filename.c_str());

	string line;
	if (inFile.is_open()) {
  	while (!inFile.eof() ) {
			getline (inFile,line);
			vector<int> curSuite;
			if (line != "") {
				processSuite(line, curSuite);
				suiteList->push_back(curSuite);
			}
		}
		
		inFile.close();
	} else {
    cerr << "Unable to open file "<<filename<<endl;
    exit(1);  
	}
	
	return suiteList;
}

void processOracle(const string& line, vector<int>& oracle, TestSuite* ts) {
	string cur;
	for (int i = 0; i < line.size(); i++) {
		if (line[i] == ',') {
			oracle.push_back(ts->getColumn(cur));
			cur = "";
		} else if (line[i] != ' ') {
			cur += line[i];
		}
	}
	
	//ending
	if (cur != "") {
		oracle.push_back(ts->getColumn(cur));
	}
}

vector<vector<int> >* getOracleList(string filename, TestSuite* ts) {
	vector<vector<int> >* oracleList = new vector<vector<int> >();

	ifstream inFile(filename.c_str());

	string line;
	if (inFile.is_open()) {
  	while (!inFile.eof() ) {
			getline (inFile,line);
			vector<int> curOracle;
			if (line != "") {
				processOracle(line, curOracle, ts);
				oracleList->push_back(curOracle);
			}
		}
		
		inFile.close();
	} else {
    cerr << "Unable to open file "<<filename<<endl;
    exit(1);  
	}
	
	return oracleList;
}

void processMutant(const string& line, vector<string>& mutant) {
	string cur;
	for (int i = 0; i < line.size(); i++) {
		if (line[i] == ',') {
			mutant.push_back(cur);
			cur = "";
		} else if (line[i] != ' ') {
			cur += line[i];
		}
	}
	
	//ending
	if (cur != "") {
		mutant.push_back(cur);
	}
}

vector<vector<string> >* getMutantList(string filename) {
	vector<vector<string> >* mutantList = new vector<vector<string> >();
	
	ifstream inFile(filename.c_str());

	string line;
	if (inFile.is_open()) {
  	while (!inFile.eof() ) {
			getline (inFile,line);
			vector<string> curMutant;
			if (line != "") {
				processMutant(line, curMutant);
				mutantList->push_back(curMutant);
			}
		}
		
		inFile.close();
	} else {
    cerr << "Unable to open file "<<filename<<endl;
    exit(1);  
	}
	
	return mutantList;
}


/*
Arguments: 
  1 - the original test suite
  2 - the mutant list file
  3 - the suite list file
  4 - the oracle list file
  5 - the output file */
int main(int argc, char **argv)
{
	cout<<"Beginning analysis...\n";

	TestSuite* original = new TestSuite(argv[1]);

	vector<vector<string> >* mutantList = getMutantList(argv[2]);
	vector<vector<int> >* suiteList = getSuiteList(argv[3]);
	vector<vector<int> >* oracleList = getOracleList(argv[4], original);
	
	time_t before = time(NULL);	

	int*** results = new int**[oracleList->size()];
	for (int i = 0; i < oracleList->size(); i++) {
		results[i] = new int*[mutantList->size()];
		for (int j = 0; j < mutantList->size(); j++) {
			results[i][j] = new int[suiteList->size()];		
			for (int k = 0; k < suiteList->size(); k++) {
				results[i][j][k] = 0;
			}
		}
	}
	
	for (int i = 0; i < oracleList->size(); i++) {
		cout<<"Running oracle of size: "<<(*oracleList)[i].size()<<endl;
		for (int j = 0; j < mutantList->size(); j++) {
			cout<<"Running mutantList: "<<j<<endl;
			for (int k = 0; k < (*mutantList)[j].size(); k++) {
				TestSuite mutant((*mutantList)[j][k], original);
				for (int l = 0; l < suiteList->size(); l++) {	
					if (!(original->isEqualFast(mutant, (*suiteList)[l], (*oracleList)[i]))) {
							results[i][j][l]++;
					}		
				}
			}
		}
	}
	
	time_t after = time(NULL);
	cout<<"Time to run: "<<difftime(after, before)<<" seconds\n";	

	cout<<"Going...\n";

	for (int i = 0; i < oracleList->size(); i++) {
		ofstream outFile;
		string prefix(argv[5]);
		string f = prefix + intToString((*oracleList)[i].size());
		f += ".csv";
		outFile.open(f.c_str());

		//header
		for (int j = 0; j < suiteList->size(); j++) {
		  outFile<<" ,";
			outFile<<(*suiteList)[j].size();
		}
		outFile<<endl;

		for (int j = 0; j < mutantList->size(); j++) {
			outFile<<j;
			for (int k = 0; k < suiteList->size(); k++) {
				outFile<<",";
				outFile<<results[i][j][k];
			}
			outFile<<endl;
		}
		outFile.close();
	}

	delete original;
	delete suiteList;
	delete oracleList;
	// "results" just leaks, but whatever, we're done here

	return 0;
}

