#!/bin/sh

for P in 'A' 'B' 'C' 'D' 'E' 'F'; do
	sed s/'\$\$PROBLEM\$\$'/"$P"/ template.cpp > ${P}.cpp
done
