#!/usr/bin/env python3

import os
import subprocess as sb
import sys

contig = sys.argv[1]
assemble_file = sys.argv[2]
out_file_name = sys.argv[3]
paf_file = sys.argv[4]
paf_link_file = sys.argv[5]


def return_strand(seq_name):
    # seq_id
    with open(assemble_file) as ref:
        for line in ref:
            line = line.rstrip()
            if ">" not in line:
                continue
            a = line.split(" ")
            if a[0].lstrip(">") == seq_name:
                seq_id = a[1]
    print(seq_id)
    # strand
    with open(assemble_file) as ref:
        for line in ref:
            line = line.rstrip()
            if ">" in line:
                continue
            a = line.split(" ")
            for i in range(0, len(a)):
                if a[i] == seq_id:
                    strand = "+"
                    break
                elif int(a[i]) == -1 * int(seq_id):
                    strand = "-"
                    break
    return strand

def return_forward_start_end(forward_name, backward_name):
    with open(paf_file) as ref:
        for line in ref:
            line = line.rstrip()
            a = line.split("\t")
            if a[0] == forward_name and a[5] == backward_name:
                start = a[2]
                end = a[3]
    # cmd = 'cat ' + paf_file + ' | rg ' + forward_name + " | rg " + backward_name + " | choose 2"
    # print(cmd)
    # res = sb.run(cmd, shell = True, capture_output = True, text = True)
    # start = res.stdout.rstrip()
    # cmd = 'cat ' + paf_file + ' | rg ' + forward_name + " | rg " + backward_name + " | choose 3"
    # print(cmd)
    # res = sb.run(cmd, shell = True, capture_output = True, text = True)
    # end = res.stdout.rstrip()
    return (int(start), int(end))


def return_backward_start_end(forward_name, backward_name):
    with open(paf_file) as ref:
        for line in ref:
            line = line.rstrip()
            a = line.split("\t")
            if a[0] == forward_name and a[5] == backward_name:
                start = a[7]
                end = a[8]
    # cmd = 'cat ' + paf_file + ' | rg ' + forward_name + " | rg " + backward_name + " | choose 7"
    # print(cmd)
    # res = sb.run(cmd, shell = True, capture_output = True, text = True)
    # start = res.stdout.rstrip()
    # cmd = 'cat ' + paf_file + ' | rg ' + forward_name + " | rg " + backward_name + " | choose 8"
    # print(cmd)
    # res = sb.run(cmd, shell = True, capture_output = True, text = True)
    # end = res.stdout.rstrip()
    return (int(start), int(end))


def extract_forward_fasta(forward_name, forward_strand):
    print(forward_strand)
    if forward_strand == "+":
        os.system('seqkit grep -np ' + forward_name + " " + contig + " -w 0 > tmp.forward.fasta")
    else:
        os.system('seqkit grep -np ' + forward_name + " " + contig + " -w 0 | seqkit seq -pr -w 0 > tmp.forward.fasta")

def extract_backward_fasta(backward_name, backward_strand):
    print(backward_strand)
    if backward_strand == "+":
        os.system('seqkit grep -np ' + backward_name + " " + contig + " -w 0 > tmp.backward.fasta")
    else:
        os.system('seqkit grep -np ' + backward_name + " " + contig + " -w 0 | seqkit seq -pr -w 0 > tmp.backward.fasta")

#------------------------------------------

out_file = open(out_file_name, "w")

# merge
with open(paf_link_file) as ref:
    for line in ref:
        line = line.rstrip()
        a = line.split(" ")

        print("start")
        # fasta name
        fasta_name = ">"
        for i in range(0, len(a)):
            fasta_name += a[i]
            if i != len(a) -1:
                fasta_name += "_plus_"
        #os.system('echo "' + fasta_name + '" >> ' + out_file)
        out_file.write(fasta_name + "\n")
        print(fasta_name)


        ## First process
        forward_name = a[0]
        backward_name = a[1]

        # Check: strand
        forward_strand = return_strand(forward_name)
        backward_strand = return_strand(backward_name)

        # Check: start end
        #(forward_start, forward_end) = return_forward_start_end(forward_name, backward_name)
        (backward_start, backward_end) = return_backward_start_end(forward_name, backward_name)

        # extract fasta
        extract_forward_fasta(forward_name, forward_strand)
        extract_backward_fasta(backward_name, backward_strand)

        # merge forward and backward
        #os.system('echo -n $(cat tmp.forward.fasta | tail -n +2) >> ' + out_file)
        #os.system('echo -n $(cat tmp.backward.fasta | seqkit subseq -r ' + str(backward_end + 1) + ':-1 -w 0 | tail -n +2) >> ' + out_file)
        cmd = 'cat tmp.forward.fasta | tail -n +2'
        res = sb.run(cmd, shell = True, capture_output = True, text = True)
        forward_fasta = res.stdout.rstrip()
        cmd = 'cat tmp.backward.fasta | seqkit subseq -r ' + str(backward_end + 1) + ':-1 -w 0 | tail -n +2'
        res = sb.run(cmd, shell = True, capture_output = True, text = True)
        backward_fasta = res.stdout.rstrip()
        out_file.write(forward_fasta)
        out_file.write(backward_fasta)


        if len(a) == 2:
            out_file.write("\n")
            continue

        for i in range(2, len(a)):
            forward_name = a[i-1]
            backward_name = a[i]

            # Check: strand
            #forward_strand = return_strand(forward_name)
            backward_strand = return_strand(backward_name)

            # Check: start end
            #(forward_start, forward_end) = return_forward_start_end(forward_name, backward_name)
            (backward_start, backward_end) = return_backward_start_end(forward_name, backward_name)

            # extract fasta
            #extract_forward_fasta(forward_name, forward_strand)
            extract_backward_fasta(backward_name, backward_strand)

            #os.system('echo -n $(cat tmp.backward.fasta | seqkit subseq -r ' + str(backward_end + 1) + ':-1 -w 0 | tail -n +2) >> ' + out_file)
            cmd = 'cat tmp.backward.fasta | seqkit subseq -r ' + str(backward_end + 1) + ':-1 -w 0 | tail -n +2'
            res = sb.run(cmd, shell = True, capture_output = True, text = True)
            backward_fasta = res.stdout.rstrip()
            out_file.write(backward_fasta)

        #os.system('echo "" >> ' + out_file)
        out_file.write("\n")

