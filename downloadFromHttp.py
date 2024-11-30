import os
from pathlib import Path
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

global path, currentPath, url, currentUrl
path = os.path.dirname(os.path.abspath(__file__))
print(path)
currentPath = path

url = 'http://localhost:8000/'
currentUrl = url

global currentLink, paths, files, allFiles
paths = ['']
files = []
allFiles = []
currentLink = ''

def get_links(content):
    soup = BeautifulSoup(content)
    for a in soup.findAll('a'):
        yield a.get('href')

def Baixar(content):
    global path

    folder = ''
    fileName = ''
    #separa a pasta e o arquivo
    if '/' in content:
        content = content.split('/')
        fileName = content[-1]
        content.pop(-1)
        folder = '\\'.join(content)
        folder += '\\'
    else:
        fileName = content

    currentPath = os.path.join(path,folder)
    currentPath = currentPath.replace('/','')
    currentPath = currentPath.replace('%20',' ')
    fileName = fileName.replace('%20', ' ')

    print(f'baixando {fileName} para {currentPath}')
 
    if not os.path.exists(currentPath):
        os.makedirs(currentPath)
        print(f'criou dir {currentPath}')

    with open(f'{currentPath}{fileName}','w') as f:
        print(f'escrevi {fileName} para {currentPath}{fileName}')
        f.write(fileName)


def download():
    global currentPath, url, currentUrl, currentLink
    print(f"url: {currentUrl}")
    # path = urlparse(url).path.lstrip(':')
    # print(f"path: {path}")
    # path = url
    # print(content)

    do = True
    while do or len(paths) > 0:
    # while do:
        do = False

        currentLink = paths[0]
        currentUrl = url + paths[0]
        paths.pop(0)
        
        GetFromPage(currentUrl)

        # r = requests.get(currentUrl)
        # content = r.text
        # print(f'\nabrindo {currentUrl}')
        # # print(get_links(content))
        # for link in get_links(content):
        #     #pega as pastas
        #     if link.endswith('/'):
        #         #if not link.startswith('.'): # skip hidden files such as .DS_Store
        #         # download(urljoin(url, link))
        #         # print(link)
        #         paths.append(currentLink+link)
        #     #pega os arquivos
        #     else:
        #         files.append(currentLink+link)
        #         # with open(link, 'w') as f:
        #         #     f.write(content)
                
        # print(f'paths: {paths}\nfiles: {files}\ncurrentLink: {currentLink}')

        #baixa todos os arquivos da pasta atual
        # for file in files:
        #     print('baixa', file,'\n')
        #     # Baixar(file)


        # #muda o link pra proxima pasta
        # currentPath = os.path.join(path,paths[0])        
        # currentUrl = url + paths[0]
        # paths.pop(0)

        # files = []

    # <h1>Directory listing for /</h1>
    # <hr>
    # <ul>
    # <li><a href="teste%202/">teste 2/</a></li>
    # <li><a href="teste.txt">teste.txt</a></li>
    # <li><a href="teste1/">teste1/</a></li>
    # </ul>
    # <hr>
    # </body>
    # </html>

    # if r.status_code != 200:
    #     raise Exception('status code is {} for {}'.format(r.status_code, url))
    # content = r.text
    # if path.endswith('/'):
    #     Path(path.rstrip('/')).mkdir(parents=True, exist_ok=True)
    #     for link in get_links(content):
    #         if not link.startswith('.'): # skip hidden files such as .DS_Store
    #             download(urljoin(url, link))
    # else:
    #     with open(path, 'w') as f:
    #         f.write(content)

def GetFromPage(url):
    global currentLink, paths, files, allFiles

    r = requests.get(url)
    content = r.text

    print(f'\nabrindo {url}')

    for link in get_links(content):
        #pega as pastas
        if link.endswith('/'):
            #if not link.startswith('.'): # skip hidden files such as .DS_Store
            # download(urljoin(url, link))
            # print(link)
            paths.append(currentLink+link)
        #pega os arquivos
        else:
            allFiles.append(currentLink+link)
            # with open(link, 'w') as f:
            #     f.write(content)

    print(f'paths: {paths}\nfiles: {files}\ncurrentLink: {currentLink}\nallFiles: {allFiles}')

def DownloadFiles():
    global allFiles

    for file in allFiles:
        Baixar(file)

if __name__ == '__main__':
    # the trailing / indicates a folder
    download()
    DownloadFiles()