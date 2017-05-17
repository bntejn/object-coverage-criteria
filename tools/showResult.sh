#!/bin/bash

reports=`ls $1/results/*/*/report.csv`
for report in $reports; do
    echo "===================================================================="
    echo -ne "# REPORT: "$report"\n\n"
    column -s , -t $report
done
