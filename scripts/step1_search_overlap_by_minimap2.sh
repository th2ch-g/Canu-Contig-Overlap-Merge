#!/bin/sh

target_final_fasta=$1
target_final_assembly=$2

# prepare list
count=0
cat $target_final_assembly | rg -v ">" | while IFS= read -r line; do count=$(( $count +1 )); echo "$line" | tr " " "\n" > tmp.${count}.list; done

# exatract
scaffold_number=0
for i in $(ls tmp.*.list);
do
    if [ $(cat $i | wc -l) -eq 1 ]; then
        continue
    fi
    scaffold_number=$(( $scaffold_number + 1 ))
    mkdir scaffold_$scaffold_number
    cd scaffold_$scaffold_number

    while IFS= read -r line;
    do
        count=$(( $count + 1 ))
        if [ $count -eq 1 ]; then
            seq_strand=$(echo $line | awk '{if($1 > 0){print 0}else{print 1}}')
            number=$(echo $line | awk '{if($1 > 0){print $1}else{print -1 * $1}}')
            seq_name=$(cat $target_final_assembly | rg ">" | awk -v target=${number} '{if($2 == target){print substr($1, 2)}}')
            keep_seq_name=$seq_name
            keep_seq_strand=$seq_strand
            continue
        fi

        seq_strand=$(echo $line | awk '{if($1 > 0){print 0}else{print 1}}')
        number=$(echo $line | awk '{if($1 > 0){print $1}else{print -1 * $1}}')
        seq_name=$(cat $target_final_assembly | rg ">" | awk -v target=${number} '{if($2 == target){print substr($1, 2)}}')

        now_seq_name=$seq_name
        now_seq_strand=$seq_strand

        if [[ $keep_seq_strand -eq 0 ]]; then
            seqkit grep -nrp $keep_seq_name $target_final_fasta > tmp.forward.fasta
        else
            seqkit grep -nrp $keep_seq_name $target_final_fasta | seqkit seq -pr > tmp.forward.fasta
        fi

        if [[ $now_seq_strand -eq 0 ]]; then
            seqkit grep -nrp $now_seq_name $target_final_fasta > tmp.backward.fasta
        else
            seqkit grep -nrp $now_seq_name $target_final_fasta | seqkit seq -pr > tmp.backward.fasta
        fi

        minimap2 -c -x asm20 tmp.backward.fasta tmp.forward.fasta -t 10 --eqx --cs=long >> out.paf

        keep_seq_name=$seq_name
        keep_seq_strand=$seq_strand

    done < ../${i}

    cd ..

done

