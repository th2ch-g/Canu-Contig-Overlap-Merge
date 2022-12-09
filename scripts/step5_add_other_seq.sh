#!/bin/sh

contig=$1
out_file=$2
paf_file=$3
merged_file=$4

# input other seq
cat $paf_file | awk '{print $1"\n"$6}' > tmp.merged.list
cp $merged_file $out_file
seqkit grep -f tmp.merged.list -v $contig -w 0 >> $out_file


