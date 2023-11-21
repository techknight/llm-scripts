# ia-download.py
# https://github.com/techknight/llm-scripts
#
# This script takes an Internet Archive URL and optionally a filetype as input,
# and does a multi-threaded download of the matching files in that folder.
#
# Usage:
#   ia-download.py <URL> [filetype]
# 
#   <URL> must be a /download folder on archive.org, ie https://archive.org/download/Computer_Chronicles/Season%2003/
#   [filetype] is optional, defaults to zip
#
# Example: (downloads all MP4 files from Season 03 of the Computer Chronicles)
#   ia-download.py https://archive.org/download/Computer_Chronicles/Season%2003/ mp4
#
# Prerequisites:
#   BeautifulSoup
#   pip install beautifulsoup4
#   
#   TQDM
#   pip install tqdm
#
# Tool: 
#   ChatGPT (GPT-4)

import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import sys
import urllib.parse

# Get the URL from the command-line arguments
if len(sys.argv) < 2:
    print('Please specify the URL of the archive.org folder.')
    sys.exit()
url = sys.argv[1]

# Get the file type from the command-line arguments or default to .zip
file_type = '.zip'
if len(sys.argv) >= 3:
    file_type = '.' + sys.argv[2] if not sys.argv[2].startswith('.') else sys.argv[2]

# Request the HTML content of the page
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all links that end with the specified file type and do not have "View Contents" in their text
file_links = soup.find_all('a', href=lambda href: href is not None and href.endswith(file_type) and 'View Contents' not in href)

# Create a directory to store the downloaded files
download_dir = f'downloaded_{file_type[1:]}s'  # e.g., downloaded_zips or downloaded_pdfs
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Function to sanitize filenames by replacing invalid characters
def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '-')
    return filename

# Define a function to download a single file with progress bar
def download_file(file_url):
    decoded_url = urllib.parse.unquote(file_url)
    raw_filename = decoded_url.split('/')[-1]
    filename = sanitize_filename(raw_filename)
    
    filepath = os.path.join(download_dir, filename)
    with open(filepath, 'wb') as f:
        download_and_write_file(f, file_url, filename)

def download_and_write_file(file_handle, file_url, filename):
    response = requests.get(file_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc=filename)
    try:
        for data in response.iter_content(block_size):
            if tqdm._instances:
                progress_bar.update(len(data))
                file_handle.write(data)
            else:
                # Progress bar has been closed by user
                break
    except KeyboardInterrupt:
        # User pressed the q key to quit
        progress_bar.close()
        print('\nDownload interrupted.')
        sys.exit()

# Use multithreading to download the files
with ThreadPoolExecutor(max_workers=10) as executor:
    for link in file_links:
        file_url = url + link.get('href')
        executor.submit(download_file, file_url)

print(f'All {file_type[1:]} files downloaded.')