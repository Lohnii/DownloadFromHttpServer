import os
from urllib.parse import urljoin, unquote
import requests
from bs4 import BeautifulSoup

# Global variables
global path, currentPath, url, currentUrl
path = os.path.dirname(os.path.abspath(__file__))
currentPath = path

#get ip
ip = input('ip e porta do seu coiso (exemplo: 0.0.0.0:8000):\n') #0.0.0.0:8000
url = f'http://{ip}/'
currentUrl = url

# Track folders and files
global currentLink, paths, files, allFiles
paths = ['']
files = []
allFiles = []
currentLink = ''


# Function to extract links from page content
def get_links(content):
    soup = BeautifulSoup(content, 'html.parser')
    for a in soup.find_all('a', href=True):
        yield a.get('href')

# Function to download a single file
def Baixar(content):
    global path

    folder = ''
    fileName = ''

    # Decode URL-encoded characters
    content = unquote(content)

    # Separate folder and file name
    if '/' in content:
        parts = content.split('/')
        fileName = parts[-1]
        parts.pop(-1)
        folder = os.path.join(*parts)
    else:
        fileName = content

    currentPath = os.path.join(path, folder)

    # Ensure the directory exists
    os.makedirs(currentPath, exist_ok=True)

    # File download URL
    file_url = urljoin(url, content)

    # File save path
    save_path = os.path.join(currentPath, fileName)

    print(f'Downloading {fileName} to {currentPath}')

    # Download the file
    response = requests.get(file_url, stream=True)
    response.raise_for_status()

    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

# Recursive downloader
def download():
    global currentPath, url, currentUrl, currentLink
    print(f"Starting download from URL: {currentUrl}")

    while paths:
        currentLink = paths.pop(0)
        currentUrl = urljoin(url, currentLink)

        GetFromPage(currentUrl)

# Process links from a page
def GetFromPage(url):
    global currentLink, paths, files, allFiles

    response = requests.get(url)
    response.raise_for_status()
    content = response.text

    print(f'Accessing {url}')

    for link in get_links(content):
        # Normalize the link
        full_link = urljoin(currentLink, link)

        # Decode URL-encoded characters
        link = unquote(link)

        # Directory or file?
        if link.endswith('/'):
            paths.append(full_link)
        else:
            allFiles.append(full_link)

    print(f'Current paths: {paths}')
    print(f'Current files: {allFiles}')

# Download all files collected
def DownloadFiles():
    for file in allFiles:
        Baixar(file)

if __name__ == '__main__':
    download()
    DownloadFiles()
