#!/bin/bash
#
# Splits Techzone XML aggregated files into separate XML files
#
# Receives as input the name of the folder with the aggregated XML files,
# and the name of the folder where to produce the outputs

input=$1
output=$2

# Iterate over files in input folder
for inputfile in $(ls $1)
do
    cat $input/$inputfile |
    gawk -v output=$output -v inputfile=$inputfile '
        BEGIN {
            outputsuffix = "0"
        }
        {
            if ( $0 ~ "<?xml version=\"1.0\" " )
                outputsuffix = outputsuffix + 1
                outfile = output"/"inputfile"."outputsuffix
            if ( outputsuffix > 0 )
                print $0 > outfile
        }
    '
done
