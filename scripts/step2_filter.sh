#!/bin/sh

cat ../step1/*/out.paf \
    | awk '{if($2 == $4 && $8 == 0 && $5 == "+"){print $0}}' \
    | awk -v identity=${1} '{if($10/$11 >= identity){print $0}}' \
    > out.filtered.paf

