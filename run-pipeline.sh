#!/bin/bash

# Input path of scripts directory
export PATH="<PATH>/Canu-Contig-Overlap-Merge/scirpts:$PATH"

#######################################################################
USAGE='
run-pipeline.sh:
    Canu Contig Overlap Merge

USAGE:
    run-pipeline.sh -a <*.final.assembly> -c <*.final.fasta>

CAUTION:
    *.final.assembly, *.final.fasta are output from juicer or 3d-dna.
    Contig is assumed to be the result of being assembled in Canu.

OPTIONS:
    -h, --help              print help
    -a, --assembly-file     *.final.assembly file (not *.FINAL.assembly)
    -c, --contig            *.final.fasta file (not *.final.assembly)
    -i, --identity          % of identity allowed [default: 99.0%]
    -p, --prefix            output file prefix [default: out]
    -N, --scaffold-gap      Gap size of scaffold [default: 500]

REQUIREMENT:
    minimap2                minimap2 is used for contig end alignment
    seqkit                  seqkit is used for fasta processing
'

assembly_flag=0
contig_flag=0
identity="0.99"
N_nums="500"
while :;
do
    case $1 in
        -h | --help)
            echo "$USAGE" >&1
            exit 0
            ;;
        -a | --assemblyfile)
            assembly_flag=1
            if [ -z "$2" ]; then
                echo "[ERROR] assembly file name is not detected." >&2
                exit 1
            fi
            assembly_file=$2
            ;;
        -c | --contig)
            contig_flag=1
            if [ -z "$2" ]; then
                echo "[ERROR] contig file name is not detected" >&2
                exit 1
            fi
            contig_file=$2
            ;;
        -p | --prefix)
            if [ -z "$2" ]; then
                echo "[ERROR] prefix is not detected" >&2
                exit 1
            fi
            prefix="$2"
            ;;
        -i | --identity)
            if [ -z "$2" ]; then
                echo "[ERROR] identity % is not detected" >&2
                exit 1
            fi
            identity="$2"
            ;;
        -N | --scaffold-gap)
            if [ -z "$2" ]; then
                echo "[ERROR] scaffold gap is not detected" >&2
                exit 1
            fi
            N_nums="$2"
            ;;
        --)
            shift
            break
            ;;
        -?*)
            echo "[ERROR] Unknown option : ${1}" >&2
            exit 1
            ;;
        *)
            break
    esac
    shift
done


if [ $assembly_flag -eq 0 ] || [ $contig_flag -eq 0 ]; then
    echo "[ERROR] file option is necessary" >&2
    exit 1
fi


echo "[INFO] assembly file is : ${assembly_file}" >&1
echo "[INFO] contig file is : ${contig_file}" >&1


#=========================================================================

set -e
# Step1: search overlap by minimap2
mkdir step1
cd step1
step1_search_overlap_by_minimap2.sh $contig_file $assembly_file
cd ..

# Step2: filter paf file
mkdir step2
cd step2
step2_filter.sh $identity
cd ..

# Step3: merge prepare
mkdir step3
cd step3
step3_make_link.py ../step2/out.filtered.paf > paf_link.list
cd ..

# Step4: merge end to end
mkdir step4
cd step4
step4_merge_dup.py $contig_file $assembly_file ${prefix}.merged.fasta ../step2/out.filtered.paf ../step3/paf_link.list
cd ..

# Step5: add other seq
mkdir sstep5
cd step5
step5_add_other_seq.sh $contig_file ${prefix}.merged.added.fasta ../step2/out.filtered.paf ../step4/${prefix}.merged.fasta
cd ..

# Step6:
mkdir step6
cd step6
step6_scaffold.py $assembly_file ../step5/${prefix}.merged.added.fasta ${prefix}.merged.added.scaffolded.fasta $N_nums
cd ..

echo "All pipe-line is done" >&1
