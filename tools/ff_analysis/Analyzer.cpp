#include "Analyzer.h"

using namespace std;

Analyzer::Analyzer(string correctSuiteF, string mutantListF, 
        string suiteListF, string oracleListF) {
	correctSuite = new TestSuite(correctSuiteF);
    mutants = getMutantList(correctSuiteF, mutantListF);
	suiteList = getSuiteList(suiteListF);
	oracleList = getOracleList(oracleListF, correctSuite);

	cout<< "[analysis] "<< mutants.size()<< " mutants, "<< suiteList->size()
        <<" test suites, "<<oracleList->size()<<" oracles"<<endl;

}

void Analyzer::processSuite(const string& line, vector<int>& suite) {
	string cur;
	for (int i=0; i<line.size(); i++) {
		if (line[i] == ',') {
			suite.push_back(stringToInt(cur));
			cur = "";
		} else if (line[i] != ' ' && line[i] != '\n' && line[i] != '\r') {
			cur += line[i];
		}
	}
	//ending
	if (cur != "") {
		suite.push_back(stringToInt(cur));
	}
}

int Analyzer::stringToInt(const string& line) {
    istringstream buffer(line);
    int i;
    buffer >> i;
    return i;
}

vector<vector<int> >* Analyzer::getSuiteList(string filename) {
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
            /*
            cout<< "curSuite"<< endl;
            for (int i=0; i<curSuite.size(); i++) {
                cout<< curSuite[i]<< " ";
            }
            cout<< endl;
            */
		}
		inFile.close();
	} else {
        cerr << "Unable to open file "<<filename<<endl;
        exit(1);  
	}
    /*
    cout<< "suiteList"<< endl;
    for (int i=0; i<suiteList->size(); i++) {
        for (int j=0; j<(*suiteList)[i].size(); j++){ 
            cout<< (*suiteList)[i][j]<< " ";
        }
        cout<< endl;
    }
    cout<< endl;
    */
	
	return suiteList;
}

void Analyzer::processOracle(const string& line, vector<int>& oracle, TestSuite* ts) {
	string cur;
	for (int i = 0; i < line.size(); i++) {
		if (line[i] == ',') {
			oracle.push_back(ts->getColumn(cur));
			cur = "";
		} else if (line[i] != ' ' && line[i] != '\n' && line[i] != '\r') {
			cur += line[i];
		}
	}
	
	//ending
	if (cur != "") {
		oracle.push_back(ts->getColumn(cur));
	}
}

vector<vector<int> >* Analyzer::getOracleList(string filename, TestSuite* ts) {
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

string Analyzer::getPrefix(string s) {
	string pre = "";
	int end = s.rfind("/");
	for (int i = 0; i < end; i++) {
		pre += s[i];
	}
	return pre;
}

vector<string> Analyzer::getMutantList(string originalFname, string filename) {
	string prefix = getPrefix(originalFname);
	ifstream inFile(filename.c_str());	
	vector<string> mutList;

	string line;
	if (inFile.is_open()) {
        while (!inFile.eof() ) {
			getline (inFile,line);
			if (line != "") {
				string m = prefix;
				m+="/";
				m+=line;
				mutList.push_back(m);
			}
		}
		inFile.close();
	} else {
        cerr << "Unable to open file "<<filename<<endl;
        exit(1);  
	}
	
	return mutList;
}

string Analyzer::processMutantName(string mutFile) {
	int lastDot = mutFile.find_last_of('.');
	int lastUnder = mutFile.find_last_of('_');

	string mutantName = "";
	while (lastUnder < lastDot) {
		mutantName += mutFile[lastUnder];
		lastUnder+=1;
	}

	return mutantName;
}

void Analyzer::initResultMatrix() {
	resultMatrix = new int*[suiteList->size()];
	for (int i = 0; i < suiteList->size(); i++) {
		resultMatrix[i] = new int[oracleList->size()];
		for (int j = 0; j < oracleList->size(); j++) {
			resultMatrix[i][j] = 0;
		}
	}
}

void Analyzer::killMutants() {
	for (int i = 0; i < mutants.size(); i++) {
		string mutantName = processMutantName(mutants[i]);
		if (mutantCnt.count(mutantName) == 1){
			mutantCnt[mutantName] += 1;
		} else {
			mutantCnt[mutantName] = 1;
			for (int i = 0; i < suiteList->size(); i++) {
                for (int j = 0; j < oracleList->size(); j++) {
                    mutationScoreMap[mutantName][i][j] = 0;
                }
            }
		}
		TestSuite mutantSuite(mutants[i], correctSuite);
		for (int j=0; j < suiteList->size(); j++) {
			for (int k=0; k < oracleList->size(); k++) {
				if (!correctSuite->isEqualFast(mutantSuite, (*suiteList)[j], (*oracleList)[k])) {
					resultMatrix[j][k]++;
					mutationScoreMap[mutantName][j][k]++;
				}
			}
		}
	}
}

void Analyzer::writeResult(string outFname) {
	ofstream outFile;
	outFile.open((outFname + ".ff.csv").c_str());

    // header
    outFile<<"suite_size";
	for (int i = 0; i < oracleList->size(); i++) {
		outFile<<",";
		if ((*oracleList)[i].size() >= 1) {
		  	outFile<< "killed_"<< (*oracleList)[i].size()<< ","
                << "score_"<< (*oracleList)[i].size();
		} else {
			outFile<<correctSuite->getColumn((*oracleList)[i][0]);
		}
	}
	outFile<<endl;

    // rows
	for (int i = 0; i < suiteList->size(); i++) {
		outFile<<(*suiteList)[i].size();
        // mutation score
		for (int j = 0; j < oracleList->size(); j++) {
			outFile << "," << resultMatrix[i][j] << "," 
                << (float(resultMatrix[i][j]) / float(mutants.size()) * 100.0);
		}
		outFile<<endl;
	}
	outFile.close();
    return;

//TODO: refactor
	string stringBase = string(outFname);
	map<string, int>::iterator maxIt;
	for (maxIt=mutantCnt.begin() ; maxIt != mutantCnt.end(); maxIt++) {
        cout<< "another one"<< endl;
		string name = (*maxIt).first;
		int maxMuts = (*maxIt).second;
		string outputName = stringBase + "_" + name + ".txt";
		
		ofstream outFull;
		outFull.open(outputName.c_str());
		
		for (int i = 0; i < oracleList->size(); i++) {
			outFull<<" ,";
			if ((*oracleList)[i].size() > 1) {
			  	outFull<<(*oracleList)[i].size();
			} else {
				outFull<<correctSuite->getColumn((*oracleList)[i][0]);
			}
		}
		outFull<<endl;

        // two features mixed together. TODO refactor (TJ)
        int sumSize = 0;
        vector<float> average;
        average.resize(oracleList->size());
		for (int i = 0; i < suiteList->size(); i++) {
			outFull<<(*suiteList)[i].size();
            sumSize += (*suiteList)[i].size();
			for (int j = 0; j < oracleList->size(); j++) {
				outFull<<",";
				outFull<<(float(mutationScoreMap[name][i][j]) / float(maxMuts) * 100.0);
                average[j] += float(mutationScoreMap[name][i][j]) / float(maxMuts) * 100.0;
			}
			outFull<<endl;
		}
        outFull<< float(sumSize) / float(suiteList->size());
        for (auto avg : average) {
            outFull<< ","<< avg / suiteList->size();
        }
		outFull.close();
	}
}

Analyzer::~Analyzer() {
	delete correctSuite;
	delete suiteList;
	delete oracleList;
}

