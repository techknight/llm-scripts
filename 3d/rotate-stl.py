# rotate-stl.py
# https://github.com/techknight/llm-scripts
#
# This script asks for a directory to process, then rotates each STL file found in it 
# by 90 degrees in the X axis and 180 degrees in the Y axis. The files are then saved 
# with "_rotated" appended to the filenames.
#
# Prerequisites:
# pip install numpy-stl
#
# Tool: 
# ChatGPT (GPT-4)
#
# Prompt: 
# Write a Python script that performs these actions on every STL file in a folder:
# 1. Rotate model 90 degrees in the X axis
# 2. Rotate model 180 degrees in the Y axis
# 3. Save the model by adding "_rotated" to the end of the original filename

import os
from stl import mesh
import numpy as np

def rotate_model(input_path, output_path):
    # Load the STL model
    main_mesh = mesh.Mesh.from_file(input_path)

    # Rotate 90 degrees about the X axis
    main_mesh.rotate([1, 0, 0], np.radians(90))

    # Rotate 180 degrees about the Y axis
    main_mesh.rotate([0, 1, 0], np.radians(180))

    # Save the rotated model
    main_mesh.save(output_path)

def process_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.stl') or filename.endswith('.STL'):
            input_file_path = os.path.join(directory_path, filename)
            output_file_path = os.path.join(directory_path, filename.replace('.stl', '_rotated.stl').replace('.STL', '_rotated.STL'))
            rotate_model(input_file_path, output_file_path)
            print(f"Processed: {filename}")

if __name__ == "__main__":
    dir_path = input("Enter the path to the directory containing the STL files: ").strip()
    process_directory(dir_path)
