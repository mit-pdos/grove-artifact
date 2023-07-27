#!/usr/bin/env python3

import os
from os import system as do

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Make sure gokv, go-ycsb, and redis are cloned.
print("Cloning git repos...")
do("git submodule update --init --recursive")
print("Done cloning git repos")

# This download Go, python, and some other packages, builds some code.
os.chdir("./gokv/simplepb/bench")
print("Setting up machines for eval...")
do("./eval-setup.py")
print("Done up machines for eval")

# This actually runs the performance experiments
os.chdir(os.path.expanduser("~/gokv/simplepb/bench"))
print("Running performance experiments...")
do("./eval-run.py -v")
print("Done with performance experiments")

print("Generating figure...")
os.chdir(os.path.expanduser("~/gokv/simplepb/bench/figure"))
do("pdflatex p.tex")
print("Done. Final figures are in ~/gokv/simplepb/bench/figures/p.pdf")
