#!/bin/bash

for env in dfw iad ord lon syd hkg
do
    for conf in configs/*${env}*
    do
        ./graphite_calc.py ${conf}
    done
    echo
done
