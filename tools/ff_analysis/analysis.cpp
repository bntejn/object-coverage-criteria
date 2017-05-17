#include "Analyzer.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void segfault_sigaction(int signal, siginfo_t *si, void *arg)
{
    printf("Caught segfault at address %p\n", si->si_addr);
    exit(0);
}

void attach_segfault_handler() {
    /* Handle segfaults and print the eip */
    struct sigaction sa;

    memset(&sa, 0, sizeof(struct sigaction));
    sigemptyset(&sa.sa_mask);
    sa.sa_sigaction = segfault_sigaction;
    sa.sa_flags   = SA_SIGINFO;

    sigaction(SIGSEGV, &sa, NULL);
}

using namespace std;

/*
Arguments: 
  1 - the original test suite
  2 - the mutant list file
  3 - the suite list file
  4 - the oracle list file
  5 - output filename*/


int main(int argc, char **argv)
{
    if (argc != 6) {
        cout<< "Invalid number of arguments (expected 5)"<< endl;
        cout<< argv[0]<< " <correctSuiteF> <mutantListF> <suiteListF>"
            << " <oracleListF> <outF>"<< endl;
        return -1;
    }
    attach_segfault_handler();

    Analyzer analyzer(argv[1], argv[2], argv[3], argv[4]);
    analyzer.initResultMatrix();

	cout<< "[analysis] Beginning analysis...\n";
    time_t t_begin = time(NULL);
    analyzer.killMutants();

	time_t t_end = time(NULL);
    double t_diff = difftime(t_end, t_begin);
	cout<< "[analysis] Time to run: "<< t_diff<< " seconds\n";
	cout<< "[analysis] Average time per comparison: "
        << (t_diff / (analyzer.suiteList->size() * analyzer.oracleList->size() 
             * analyzer.mutants.size()))
        << " seconds\n";

    analyzer.writeResult(argv[5]);

	return 0;
}

