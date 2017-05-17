//Author: Matt Staats

#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "TestSuite.h"
using namespace std;

TestSuite::TestSuite(string filename)
{
	allocateMemory(filename);
	ifstream inFile(filename.c_str());
	
	string line;
	int step = 0;
	m_testStartLocations.push_back(0);	//test at first position obviously
	if (inFile.is_open()) {
		getline (inFile,line); // drop header
		
        while (!inFile.eof() ) {
			getline (inFile,line);
			if (line != "") {
				processLine(step, line);
				step++;
			} else {
				m_testEndLocations.push_back(step-1);
				m_testStartLocations.push_back(step);
			}
			
		}
		m_testEndLocations.push_back(step-1);		//end of test and end positon obviously
		inFile.close();
	} else {
        cerr << "Unable to open file "<<filename<<endl;
        exit(1);  
	}
}

TestSuite::TestSuite(string filename, TestSuite* ts) {
	vector<int>* columns = allocateMemory(filename, ts);

	m_testEndLocations = ts->m_testEndLocations;
	m_testStartLocations = ts->m_testStartLocations;

	ifstream inFile(filename.c_str());
	
	string line;
	int step = 0;
	if (inFile.is_open()) {
		getline (inFile,line); // drop header
		
  	while (!inFile.eof() ) {
			getline (inFile,line);
			if (line != "") {
				processLine(step, line, columns);
				step++;
			} 
		}
		inFile.close();
	} else {
        cerr << "Unable to open file "<<filename<<endl;
        exit(1);  
	}
	
	delete columns;
}

TestSuite::~TestSuite() {
    /*
	for (int i = 0; i < m_numSteps; i++) {
		delete[] m_suite[i];
	}
	delete[] m_suite;
    */
}


void TestSuite::printSuite() {
    
    cout<< "suite"<< endl;
    int nrow = 0;
    for (auto row : m_suite) {
        int ncol = 0;
        for (auto col : row) {
            cout<< col<< ", ";
            ncol++;
            if (ncol > 20) {
                cout<< " ...";
                break;
            }
        }
        nrow++;
        cout<< endl;
        if (nrow > 10) {
            cout<< " ...";
            break;
        }
    }
    cout<< endl;
}

vector<int>* TestSuite::allocateMemory(string filename, TestSuite* ts) {
	ifstream inFile(filename.c_str());

	vector<int>* columns;
	//Just need the header to filter the columns we're interested in
	string line;
	if (inFile.is_open()) {
		getline(inFile,line); //process
		columns = getColumns(line, ts);
		inFile.close();
	} else {
	  cerr << "Unable to open file "<<filename<<endl;
	  exit(1);  
	}
	
	//old header and numsteps should apply here
	m_numSteps = ts->m_numSteps;
	m_header = ts->m_header;
	m_reverseHeader = ts->m_reverseHeader;
	
	//m_suite = new float*[m_numSteps];	
    m_suite.resize(m_numSteps);
	for (int i=0; i<m_numSteps; i++) {
		m_suite[i].resize(m_header.size());
        //  = new float[m_header.size()];
	}
	
	return columns;
}

void TestSuite::allocateMemory(string filename) {
	ifstream inFile(filename.c_str());
	string line;
	m_numSteps = 0;

	if (inFile.is_open()) {
		getline(inFile,line); //process
		getHeader(line);
		while (!inFile.eof() ) {
			getline (inFile,line);	
			if (line != "") {
				 m_numSteps++;
			}
		}
		inFile.close();
	} else {
	  cerr << "Unable to open file "<<filename<<endl;
	  exit(1);
	}
	//m_suite = new float*[m_numSteps];	
    m_suite.resize(m_numSteps);
	for (int i = 0; i < m_numSteps; i++) {
		m_suite[i].resize(m_header.size());// = new float[m_header.size()];
	}	
}

bool isNumber(const string& s)
{
	for (int i = 0; i < s.length(); i++) {
		if (!isdigit(s[i]) && !(s[i] == '.') && !(s[i] == '-'))
			return false;
	}
	return true;
}

float stringToFloat(const string& line) {
	float f;
 	if (isNumber(line)) {
		stringstream buffer(line);
		buffer>>f;
	} else if (string("true").compare(line)) {
        f = 1;
	} else if (string("false").compare(line)) {
        f = 0;
    } else {
		for (int i=0; i<line.length(); i++) {
			char c = (char) line[i];
			f += (i+1)*c;
		}
	}
	
	return f;
}

void TestSuite::getHeader(const string& line) {
	string cur = "";
	int curspace = 0;
	for (int i = 0; i < line.size(); i++) {
		if (line[i] == ',') {
			m_header[cur] = curspace;
			m_reverseHeader[curspace] = cur;
			curspace += 1;
			cur = "";
		} else if (line[i] != ' ' && line[i] != '\n' && line[i] != '\r') {
			cur += line[i];
		}
	}
	
	//ending
	if (cur != "") {
		m_header[cur] = curspace;
		m_reverseHeader[curspace] = cur;
	}
}

void TestSuite::processLine(int step, const string& line) {
	string cur = "";
	int curspace = 0;
    for (char c : line) {
		if (c == ',') {
			m_suite[step][curspace] = stringToFloat(cur);
			curspace += 1;
			cur = "";
		} else if (c != ' ' && c != '\n' && c != '\r') {
			cur += c;
		}
	}
	
	//ending
	if (cur != "") {
		m_suite[step][curspace] = stringToFloat(cur);
	}	
}

void TestSuite::processLine(int step, const string& line, vector<int>* columns) {
	string cur = "";
	int curspace = 0;
	int curcolumn = 0;
	int curSuiteColumn = 0;
	for (char c : line) {
		if (c == ',') {
			if ((*columns)[curcolumn] == curspace) {
				m_suite[step][curSuiteColumn] = stringToFloat(cur);
				if (curcolumn < columns->size()-1) {
					curcolumn++;
				}
				curSuiteColumn++;
			} 
			curspace += 1;
			cur = "";
		} else if (c != ' ' && c != '\n' && c != '\r') {
			cur += c;
		}
	}
	
	//ending
	if (cur != "") {
		if ((*columns)[curcolumn] == curspace) {
			m_suite[step][curSuiteColumn] = stringToFloat(cur);
		}
	}	
}

float TestSuite::getValue(int test, int step, const string& variable) {
	return m_suite[m_testStartLocations[test]+ step][m_header[variable]];
}

vector<int>* TestSuite::getColumns(const string& line, TestSuite* ts) {
	vector<int>* columns = new vector<int>();

	string cur = "";
	int curspace = 0;
    for (char c : line) {
		if (c == ',') {
			if (ts->m_header.find(cur) != ts->m_header.end()) {
				columns->push_back(curspace);
			}
			curspace += 1;
			cur = "";
		} else if (c != ' ' && c != '\n' && c != '\r') {
			cur += c;
		}
	}

	//ending
	if (cur != "" && (ts->m_header.find(cur) != ts->m_header.end())) {
		columns->push_back(curspace);
	}
	
	return columns;
}

int TestSuite::getColumn(const string& var) {
	return m_header[var];
}

string TestSuite::getColumn(const int& col) {
	return m_reverseHeader[col];
}

bool TestSuite::isEqualFast(TestSuite& ts, const vector<int>& testSuite, const vector<int>& columns) {
    //cout<< " isEqualFast() "<< testSuite.size()<< endl;
	for (int i = 0; i < testSuite.size(); i++) {
		int currentTs = m_testStartLocations[testSuite[i]];
		int endTest = m_testEndLocations[testSuite[i]];
		for (int j = currentTs; j <= endTest; j++) {
			int colSize = columns.size();
            //cout<< " | j: "<< j<< ", ss: "<< m_suite.size();
			for (int k = 0; k < colSize; k++) {			
				int c = columns[k];
                //cout<< " | cmp "<< m_suite.size()<< ", "<< m_suite[j].size();
                assert(j < m_suite.size());
                assert(c < m_suite[j].size());
				if ((m_suite[j][c]) != (ts.m_suite[j][c])) {
                    //cout<< " false"<< endl;
                    //cout.flush();
					return false;
				}
			}
		}
	}
    //cout<< " true"<< endl;
    //cout.flush();
    //cout<< " exit";
	
	return true;

}

bool TestSuite::isEqual(TestSuite& ts, const vector<int>& testSuite, const vector<string>& oracle) {

	int tsSize = testSuite.size();
	for (int i = 0; i < tsSize; i++) {
		int currentTs = m_testStartLocations[testSuite[i]];
		int endTest = m_testEndLocations[testSuite[i]];
		for (int j = currentTs; j <= endTest; j++) {
			int orSize = oracle.size();
			for (int k = 0; k < orSize; k++) {			
				if ((m_suite[j][m_header[oracle[k]]]) != (ts.m_suite[j][ts.m_header[oracle[k]]])) {
					return false;
				}
			}
		}
	}
	
	return true;
}

