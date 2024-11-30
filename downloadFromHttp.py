import os
import time
from urllib.parse import urljoin, unquote, quote
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import concurrent.futures

# Global variables
global path, url, paths
path = os.path.dirname(os.path.abspath(__file__))

#get ip
ip = input('ip e porta do seu coiso (exemplo: 0.0.0.0:8000):\n') #0.0.0.0:8000
url = f'http://{ip}/'

paths = ['']  # Queue for folders to process

# Function to extract links from page content
def get_links(content):
    soup = BeautifulSoup(content, 'html.parser')
    for a in soup.find_all('a', href=True):
        yield a.get('href')

# Function to download a single file
def Baixar(content):
    global path

    # Decode URL-encoded characters in content (e.g., %20 for space)
    decoded_content = unquote(content)

    # Separate folder and file name
    if '/' in decoded_content:
        parts = decoded_content.split('/')
        fileName = parts[-1]
        parts.pop(-1)
        folder = os.path.join(*parts)
    else:
        folder = ''
        fileName = decoded_content

    # Handle invalid characters in folder and file names
    safe_folder = folder.replace(':', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('?', '_').replace('"', '_')
    safe_fileName = fileName.replace(':', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('?', '_').replace('"', '_')

    # Create target directory
    currentPath = os.path.join(path, safe_folder)
    os.makedirs(currentPath, exist_ok=True)

    # Re-encode the URL to ensure special characters are properly encoded (like # to %23)
    encoded_url = quote(decoded_content, safe=':/')

    # File download URL
    file_url = urljoin(url, encoded_url)

    # File save path
    save_path = os.path.join(currentPath, safe_fileName)

    print(f'Downloading {safe_fileName} to {currentPath}')

    # Download the file
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    except RequestException as e:
        print(f"Error downloading {content}: {e}")
        time.sleep(2)  # Adding a short delay before retry

# Recursive downloader
def download():
    global url, paths

    print(f"Starting download from URL: {url}")

    while paths:
        current_path = paths.pop(0)
        current_url = urljoin(url, current_path)
        GetFromPage(current_url, current_path)

# Process links from a page
def GetFromPage(current_url, base_path):
    global paths

    try:
        response = requests.get(current_url)
        response.raise_for_status()
        content = response.text

        print(f'Accessing {current_url}')

        for link in get_links(content):
            # Decode URL-encoded characters (fixing %20 -> spaces, etc.)
            decoded_link = unquote(link)

            # Re-encode the URL before making requests to ensure special characters like # are properly encoded as %23
            encoded_link = quote(decoded_link, safe=':/')

            # If the link is relative, resolve it with the base URL
            full_link = urljoin(base_path, encoded_link)

            # Directory or file?
            if link.endswith('/'):
                # Ensure folder links are unique in the paths queue
                relative_path = base_path + link
                if relative_path not in paths:
                    paths.append(relative_path)
            elif '.' in link:  # Likely a file
                # Download the file immediately using the correct full link
                Baixar(full_link)

        print(f'Current paths: {paths}')
    except RequestException as e:
        print(f"Error accessing {current_url}: {e}")
        time.sleep(2)  # Adding delay before retry

def download_files_concurrently():
    global allFiles

    # Set the number of threads (adjust as needed)
    max_threads = 10  # You can increase or decrease this based on your system's capabilities

    # Using ThreadPoolExecutor to handle multiple downloads concurrently
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        # Submitting all files for download
        futures = [executor.submit(Baixar, file) for file in allFiles]

        # Wait for all threads to complete
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Check for any exceptions raised during the download

if __name__ == '__main__':
    download()
    download_files_concurrently()
