#!/bin/bash

# Directory containing simulation files
SIM_DIR="simulations"

# Output directory (main dir)
OUT_DIR="."

# Loop through all .json files in the simulations directory
for simfile in "$SIM_DIR"/*.json; do
    # Get the base filename without extension
    base=$(basename "$simfile" .json)
    # Set the output filename with _test postfix
    outfile="${OUT_DIR}/${base}_test.txt"
    # Run the simulation (replace the command below with your actual simulation runner)
    python simulator.py "$simfile" "$outfile"
done