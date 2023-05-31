#!/bin/bash

cd /app

rm -rf /$MEMORY_DIR/chromadb

pip uninstall hnswlib -y

git clone https://github.com/nmslib/hnswlib.git
cd hnswlib
pip install .
cd ..

python main.py