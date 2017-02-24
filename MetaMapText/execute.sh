#!/bin/bash
for i in $(ls $1);
do
    jython "MetaMapCaseText.py" -i $1"/"$i
    echo "$i process finished"
done
