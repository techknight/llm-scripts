# h265.py
# https://github.com/techknight/llm-scripts
#
# This script uses HandBrake and mkvmerge to transcode a folder of video files 
# using H.265/HEVC in one of three output resolutions. The idea is to process 
# only the video track, and then combine it with all of the original audio
# and subtitle tracks. (ie no downmixing or alterations)
#
# Usage:
#   h265.py <resolution> <input_folder> <output_folder>
# 
#   <resolution> must be 480p, 720p, 1080p, or 2160p
#
# Example:
#   h265.py 720p "M:\Video Files\The TV Show\Season 01" d:\temp
#
# Prerequisites:
#   HandBrake CLI must be installed https://handbrake.fr/
#   - In Windows 11, the easiest way to do this is to open a command prompt and run this command:
#     winget install "HandBrake CLI"
#   - In MacOS, with Homebrew https://brew.sh/ installed, open a terminal window and run:
#     brew install handbrake
#
#   MKVToolNix must be installed https://mkvtoolnix.download/downloads.html
#   - No matter which version you use, the binaries must be available in your PATH
#
# Tool: 
#   ChatGPT (GPT-4)
#
# Original Prompt: 
#   Create a Python script to automatically encode folders of video files using HandBrake. The script should require three command-line arguments: resolution (720p, 1080p, or 2160p), input folder, output folder
#   Use these options for encoding:
#   MKV output format
#   H.265 (x265) video encoder
#   Framerate same as source with constant framerate
#   Constant quality 22
#   Encoder preset slow
#   Copy all audio tracks without altering them
#   Copy all subtitle tracks without altering them
#
# Final prompt:
#   Create a Python script that automates video encoding and merging processes with the following specifications:
#   The script should encode video files using HandBrake with the following settings:
#
#   Output format: MKV
#   Video encoder: H.265 (x265)
#   Framerate: Same as source with a constant framerate
#   Constant quality: 22
#   Encoder preset: Slow
#   Resolution: Should be a command-line argument (720p, 1080p, or 2160p)
#   Audio and subtitle tracks should not be included in the encoding process.
#   
#   After encoding each video file, use mkvmerge to merge the newly encoded video with the original audio and subtitle tracks from the input file. The final output file should only contain the newly encoded video track, along with all original audio and subtitle tracks.
#   The script should accept three command-line arguments in the following order: resolution (720p, 1080p, 2160p), input folder path, and output folder path.
#   The script should check if the encoded file already exists in the output folder and skip encoding if it does.
#   The script should handle cases where the input file has no audio or subtitle tracks without failing.
#   Ensure that the final output file has the same filename as the input file, without additional suffixes like "-merged".
#   Please include error handling for common issues such as missing command-line arguments, incorrect resolution input, and HandBrake or mkvmerge failures.
#   This prompt requests a Python script with clear functionality requirements and error handling. The resulting script would be expected to perform video encoding followed by a merging process that combines the newly encoded video with the original audio and subtitle tracks into a final MKV file.

import subprocess
import sys
import os
import json
from datetime import datetime


def get_tracks_info(input_file):
    command = ["mkvmerge", "-J", input_file]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    info = json.loads(result.stdout)

    track_ids = {'video': [], 'audio': [], 'subtitles': []}
    for track in info['tracks']:
        if track['type'] == 'video':
            track_ids['video'].append(str(track['id']))
        elif track['type'] == 'audio':
            track_ids['audio'].append(str(track['id']))
        elif track['type'] == 'subtitles':
            track_ids['subtitles'].append(str(track['id']))

    return track_ids

def encode_video(input_path, output_path, target_height):
    command = [
        "HandBrakeCLI",
        "-i", input_path,
        "-o", output_path,
        "-f", "mkv",
        "-e", "x265",
        "--encoder-preset", "slow",
        "-q", "22",
        "--cfr",
        "--height", str(target_height),
        "--keep-display-aspect",  # Ensures the aspect ratio is maintained
        "-a", "none",  # No audio
        "-s", "none",  # No subtitles
    ]
    subprocess.run(command, check=True)

def merge_tracks(encoded_video, original_file, final_output, output_folder):
    tracks_info = get_tracks_info(original_file)

    # Start building the mkvmerge command with the output file and video track exclusion
    command = ["mkvmerge", "-o", final_output] + ["--no-video"]

    # Add the encoded video
    command.append(encoded_video)

    # Add audio tracks if they exist
    if tracks_info['audio']:
        audio_tracks = ",".join(tracks_info['audio'])
        command.extend(["--audio-tracks", audio_tracks])

    # Add subtitle tracks if they exist
    if tracks_info['subtitles']:
        subtitle_tracks = ",".join(tracks_info['subtitles'])
        command.extend(["--subtitle-tracks", subtitle_tracks])
    else:
        command.extend(["--no-subtitles"])

    # Finally, append the original file which will include only the selected audio and subtitle tracks
    command.append(original_file)

    # Execute the mkvmerge command and capture stderr
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)

    # Define the path for the warnings or errors log
    log_path = os.path.join(output_folder, 'mkvmerge-warnings-errors.log')

    # Get the current date and time in ISO 8601 format
    current_time = datetime.now().isoformat()

    # If there was a warning (exit status of 1), log it to a file in the output folder
    if result.returncode == 1:
        with open(log_path, 'a') as f:
            f.write(f"{current_time}: Warning encountered while processing file {original_file}:\n")
            f.write(result.stderr + "\n")
    # For any other non-zero return code, log the error and raise an exception
    elif result.returncode != 0:
        with open(log_path, 'a') as f:
            f.write(f"{current_time}: Error for file {original_file}:\n{result.stderr}\n")
        raise subprocess.CalledProcessError(result.returncode, command, output=result.stderr)

def encode_videos(resolution, input_folder, output_folder):
    target_heights = {
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
        "2160p": 2160
    }
    target_height = target_heights.get(resolution.lower())
    if not target_height:
        print("Invalid resolution. Choose 480p, 720p, 1080p, or 2160p.")
        sys.exit(1)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')):
            input_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            temp_output_path = os.path.join(output_folder, "temp_" + base_name + '.mkv')
            final_output_path = os.path.join(output_folder, base_name + '.mkv')

            # Skip encoding if the final file already exists in the output folder
            if os.path.exists(final_output_path):
                print(f"Output file {final_output_path} already exists. Skipping...")
                continue

            print(f"Encoding video track of {filename}...")
            encode_video(input_path, temp_output_path, target_height)

            print(f"Merging encoded video with original audio/subtitles from {filename}...")
            merge_tracks(input_path, temp_output_path, final_output_path, output_folder)

            os.remove(temp_output_path)
            print(f"Finished processing {filename}.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: encode.py <resolution> <input_folder> <output_folder>")
        sys.exit(1)

    resolution_arg = sys.argv[1]
    input_folder_arg = sys.argv[2]
    output_folder_arg = sys.argv[3]

    encode_videos(resolution_arg, input_folder_arg, output_folder_arg)
