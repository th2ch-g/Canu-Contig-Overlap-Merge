#!/bin/env python3

import sys
import subprocess as sb
import os

assembly_file = sys.argv[1]
merged_fasta = sys.argv[2]
out_file_name = sys.argv[3]
N_nums = int(sys.argv[4])


# prepare scaffold id
id_name_dic = {}
with open(assembly_file) as ref:
    for line in ref:
        line = line.rstrip()
        if ">" not in line:
            continue
        a = line.split(" ")
        id_name_dic[a[1]] = a[0][1:]


out_file = open(out_file_name, "w")
scaffold_number = 0
with open(assembly_file) as ref:
    for line in ref:
        line = line.rstrip()
        if ">" in line:
            continue
        a = line.split(" ")

        scaffold_number += 1
        pre_name = ""
        out_file.write(">HiC_scaffold_" + str(scaffold_number) + "\n")
        for i in range(0, len(a)):
            seq_id = int(a[i])
            if seq_id > 0:
                name = id_name_dic[str(seq_id)]
                cmd = 'seqkit grep -w 0 -np ' + name + ' ' + merged_fasta + ' | tail -n +2'
            else:
                name = id_name_dic[str(-1 * seq_id)]
                cmd = 'seqkit grep -w 0 -np ' + name + ' ' + merged_fasta + ' | seqkit seq -pr -w 0 | tail -n +2'

            os.system('seqkit grep -w 0 -np ' + name + ' ' + merged_fasta + ' | seqkit stats')
            res = sb.run(cmd, shell = True, capture_output = True, text = True)
            seq = res.stdout.rstrip()

            if seq == "":
                print(name, "empty...")
                if pre_name == "":
                    pre_name = name
                else:
                    pre_name += "_plus_"
                    pre_name += name
                # search as +
                os.system('seqkit grep -w 0 -np ' + pre_name + ' ' + merged_fasta + ' | seqkit stats')
                cmd = 'seqkit grep -w 0 -np ' + pre_name + ' ' + merged_fasta + ' | tail -n +2'
                res = sb.run(cmd, shell = True, capture_output = True, text = True)
                seq = res.stdout.rstrip()
                if seq == "":
                    print(pre_name, "empty...")
                else:
                    print(pre_name, "hit!")
                    out_file.write(seq)
                    if i != len(a)-1:
                        out_file.write("N"*N_nums)
                    pre_name = ""
            else:
                print(name, "hit!")
                out_file.write(seq)
                if i != len(a)-1:
                    out_file.write("N"*N_nums)
                pre_name = ""

        out_file.write("\n")


out_file.close()
