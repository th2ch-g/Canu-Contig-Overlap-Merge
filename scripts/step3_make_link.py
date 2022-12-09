#!/usr/bin/env python3

import sys

paf_file = sys.argv[1]

union_list = []

with open(paf_file) as ref:
    for line in ref:
        line = line.rstrip()
        a = line.split("\t")
        forward_name = a[0]
        backward_name = a[5]
        union_list.append((forward_name, backward_name))

new_union_list = []
for i in range(0, len(union_list)):
    if i == 0:
        pre_union = list(union_list[i])
        continue
    if pre_union[-1] == union_list[i][0]:
        pre_union.append(union_list[i][1])
    else:
        new_union_list.append(pre_union)
        pre_union = list(union_list[i])
new_union_list.append(pre_union)


for i in range(0, len(new_union_list)):
    tmp = ""
    for j in range(0, len(new_union_list[i])):
        tmp += new_union_list[i][j]
        tmp += " "
    print(tmp.rstrip())


