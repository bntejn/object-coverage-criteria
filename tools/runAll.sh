#!/bin/bash

# Taejoon Byun <taejoon.umn.edu>
# first: Apr 7 2017

#ccs=("gcc" "clang" "ccomp")
ccs=("gcc" "clang" "ccomp")
n_suites=40

for cc in ${ccs[@]}; do
    echo $cc
    echo -e "config_compiler=$cc" >> config.sh
#    ./runObcExperiment ../systems/cruise100 ../outs-old/cruise100-$cc 200 $n_suites
    ./runObcExperiment ../systems/sys145 ../outs-old/microwave145-$cc 200 $n_suites
    ./runObcExperiment ../systems/infusion-nr ../outs-old/infusion-nr-$cc 200 $n_suites
#    ./runObcExperiment ../systems/docking100 ../outs-old/docking100-$cc 200 $n_suites
    sed -i '$d' config.sh
done

exit

for cc in ${ccs[@]}; do
    echo $cc
    echo -e "config_compiler=$cc" >> config.sh
#    ./runObcExperiment ../systems/cruise200 ../outs/cruise200-$cc 200 $n_suites
    ./runObcExperiment ../systems/microwave200 ../outs/microwave200-$cc 200 $n_suites
    ./runObcExperiment ../systems/infusion200 ../outs/infusion200-$cc 200 $n_suites
    ./runObcExperiment ../systems/docking200 ../outs/docking200-$cc 200 $n_suites
    sed -i '$d' config.sh
done

#./exportAllReports.sh

