#!/bin/bash

echo "Downloading genbank files"
python fetch_genbanks.py
echo "Creating Database"
python create-viraldb.py
python generate-indexes.py all clean short_clean
eecho "Creating visualization"
python vis.py