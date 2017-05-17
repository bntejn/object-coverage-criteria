#!/bin/bash

# first: Apr 4 2017
# last : Apr 7 2017
# Taejoon Byun <taejoon@umn.edu>

result_dir="../results/"
reports=`ls ../outs-old/*/results/*/*/report.csv`

rm -r $result_dir
mkdir $result_dir

# export all the reports
for report in $reports; do
    path_sep=(`echo "$report" | tr "/" "\n"`)
    echo $report
    filename=${path_sep[2]}_${path_sep[5]}.csv
    echo $filename
    cp $report $result_dir/$filename
done

# export all the figures
pdfs=`ls ../outs-old/*/results/*/*/*.pdf`
for pdf in $pdfs; do
    path_sep=(`echo "$pdf" | tr "/" "\n"`)
    echo $pdf
    filename=${path_sep[2]}_${path_sep[5]}_${path_sep[6]}
    echo $filename
    cp $pdf $result_dir/$filename
done

echo "COPY!"

ccs=("gcc" "clang" "ccomp")
cp $result_dir/cruise100-gcc_cruisecontrol_boxplot3.pdf ../../issre17/figures/cruise-mcdc.pdf
cp $result_dir/docking100-gcc_docking_boxplot3.pdf ../../issre17/figures/docking-mcdc.pdf
cp $result_dir/infusion-nr-gcc_infusion_boxplot3.pdf ../../issre17/figures/infusion-mcdc.pdf
cp $result_dir/microwave145-gcc_mw_manual_boxplot3.pdf ../../issre17/figures/mwmanual-mcdc.pdf
cp $result_dir/microwave145-gcc_mw_auto_boxplot3.pdf ../../issre17/figures/mwauto-mcdc.pdf
for cc in ${ccs[@]}; do
    cp $result_dir/cruise100-${cc}_cruisecontrol_boxplot1.pdf ../../issre17/figures/cruise-${cc}1.pdf
    cp $result_dir/cruise100-${cc}_cruisecontrol_boxplot2.pdf ../../issre17/figures/cruise-${cc}2.pdf
    cp $result_dir/docking100-${cc}_docking_boxplot1.pdf ../../issre17/figures/docking-${cc}1.pdf
    cp $result_dir/docking100-${cc}_docking_boxplot2.pdf ../../issre17/figures/docking-${cc}2.pdf
    cp $result_dir/infusion-nr-${cc}_infusion_boxplot1.pdf ../../issre17/figures/infusion-${cc}1.pdf
    cp $result_dir/infusion-nr-${cc}_infusion_boxplot2.pdf ../../issre17/figures/infusion-${cc}2.pdf
    cp $result_dir/microwave145-${cc}_mw_manual_boxplot1.pdf ../../issre17/figures/mwmanual-${cc}1.pdf
    cp $result_dir/microwave145-${cc}_mw_manual_boxplot2.pdf ../../issre17/figures/mwmanual-${cc}2.pdf
    cp $result_dir/microwave145-${cc}_mw_auto_boxplot1.pdf ../../issre17/figures/mwauto-${cc}1.pdf
    cp $result_dir/microwave145-${cc}_mw_auto_boxplot2.pdf ../../issre17/figures/mwauto-${cc}2.pdf
done

