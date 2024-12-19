import os
import time
from urllib.parse import urljoin, unquote, quote
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import concurrent.futures

# Global variables
global path, url, paths, allFiles, failed_downloads
path = os.path.dirname(os.path.abspath(__file__))

#get ip
ip = ''
try:
    with open('ip.txt','r') as i:
        ip = i.read()
except:    
    ip = input('ip e porta do seu coiso (exemplo: 0.0.0.0:8000):\n') #0.0.0.0:8000

url = f'http://{ip}/'

paths = ['']  # Queue for folders to process
allFiles = []  # List of files to download
failed_downloads = []  # List to track failed downloads

# Function to extract links from page content
def get_links(content):
    soup = BeautifulSoup(content, 'html.parser')
    for a in soup.find_all('a', href=True):
        yield a.get('href')

# Function to download a single file
def Baixar(content):
    global path, failed_downloads

    try:
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

        # Check if the file already exists
        try:
            response = requests.head(file_url, allow_redirects=True)
            response.raise_for_status()
            server_file_size = int(response.headers.get('Content-Length', 0))

            if os.path.exists(save_path):
                local_file_size = os.path.getsize(save_path)
                if local_file_size == server_file_size:
                    print(f"Skipping {safe_fileName}: Already downloaded.")
                    return
                else:
                    print(f"Redownloading {safe_fileName}: File is incomplete.")
                    os.remove(save_path)  # Delete incomplete file
        except RequestException as e:
            print(f"Error checking file {content}: {e}")
            failed_downloads.append(f"Failed HEAD: {content} -> {e}")
            return

        # Download the file
        print(f'Downloading {safe_fileName} to {currentPath}')

        try:
            response = requests.get(file_url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"Downloaded {safe_fileName} successfully.")
        except RequestException as e:
            print(f"Error downloading {content}: {e}")
            failed_downloads.append(f"Failed: {content} -> {e}")

    except Exception as e:
        print(f"Unexpected error for {content}: {e}")
        failed_downloads.append(f"Unexpected: {content} -> {e}")

# Recursive downloader
def download():
    global url, paths, allFiles

    print(f"Starting download from URL: {url}")

    while paths:
        current_path = paths.pop(0)
        current_url = urljoin(url, current_path)
        GetFromPage(current_url, current_path)

# Process links from a page
def GetFromPage(current_url, base_path):
    global paths, allFiles

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
                # Add file to allFiles list
                allFiles.append(full_link)
                # Download the file immediately
                Baixar(full_link)

        print(f'Current paths: {paths}')
    except RequestException as e:
        print(f"Error accessing {current_url}: {e}")
        time.sleep(2)  # Adding delay before retry

# Concurrent file downloader
def download_files_concurrently():
    global allFiles, failed_downloads

    # Set the number of threads (adjust as needed)
    max_threads = 10  # You can increase or decrease this based on your system's capabilities

    # Using ThreadPoolExecutor to handle multiple downloads concurrently
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        # Submitting all files for download
        futures = [executor.submit(Baixar, file) for file in allFiles]

        # Wait for all threads to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Check for any exceptions raised during the download
            except Exception as e:
                # Log unexpected errors
                failed_downloads.append(f"Unexpected error -> {e}")

    # Print failed downloads at the end
    if failed_downloads:
        print("\n### Failed Downloads ###")

        for failure in failed_downloads:
            print(failure)

        with open('failures.txt', 'w') as f:            
                f.writelines(failed_downloads)

        input()
    else:
        print("\nAll files downloaded successfully!")
        input()

if __name__ == '__main__':
    download()
    download_files_concurrently()
