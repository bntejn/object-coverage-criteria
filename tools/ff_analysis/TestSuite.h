//Author: Matt Staats

#include <string>
#include <map>
#include <vector>
#include <set>
using namespace std;

#ifndef TESTSUITE_H
#define TESTSUITE_H

class TestSuite {
private:
    map<string,int> m_header;
    map<int, string> m_reverseHeader; 
    vector<vector<float> > m_suite;
    vector<int> m_testStartLocations;
    vector<int> m_testEndLocations;
    int m_numSteps;

private:
    vector<int>* getColumns(const string& line, TestSuite* ts);
    vector<int>* allocateMemory(string filename, TestSuite* ts);
    void allocateMemory(string filename);		
    void processLine(int step, const string& line, vector<int>* columns);		
    void getHeader(const string& line);
    void processLine(int step, const string& line);

public:
    TestSuite(string filename);  
    TestSuite(string filename, TestSuite* ts);        
    virtual ~TestSuite(); 

    int getColumn(const string& var); 
    string getColumn(const int& col);       
    void printSuite();

    float getValue(int test, int step, const string& variable);
    bool isEqualFast(TestSuite& ts, const vector<int>& testSuite, const vector<int>& columns);      
    bool isEqual(TestSuite& ts, const vector<int>& testSuite, const vector<string>& oracle);
};

#endif
