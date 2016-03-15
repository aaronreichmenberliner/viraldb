#!/bin/bash

echo "Start script!"

temp=`echo $1 | cut -d " " -f 1`
material=`echo $1 | cut -d " " -f 2`
locus=`echo $1 | cut -d " " -f 3`

echo $temp
echo $material
echo $locus

echo $2