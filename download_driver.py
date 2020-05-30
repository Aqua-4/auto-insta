"""This program will doenload the required chromedriver
based on your system type
"""

import platform
import urllib3
import subprocess
import zipfile
import os

SYS_TYPE = platform.system()
CHUNK_SIZE = 65536

CHROME_DRIVER_ZIP = "chromedriver.zip"


def check_selenium():
    try:
        import selenium
        selenium.__version__
        # print(selenium.__version__)
    except ImportError:
        subprocess.call(['pip', 'install', 'selenium'])


def download_file(_url):
    """Establish connection and download using urlllib3"""
    http = urllib3.PoolManager()
    r = http.request('GET', _url, preload_content=False)

    with open(CHROME_DRIVER_ZIP, 'wb') as out:
        while True:
            data = r.read(CHUNK_SIZE)
            if not data:
                break
            out.write(data)

    r.release_conn()


def driver_file_ops():
    driver_zip = zipfile.ZipFile(CHROME_DRIVER_ZIP)
    driver_zip.extractall()
    os.remove(CHROME_DRIVER_ZIP)
    if SYS_TYPE == 'Linux':
        subprocess.call(['chmod', '7771', 'chromedriver'])


check_selenium()
if SYS_TYPE == 'Linux':
    download_file(
        "https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip")
elif SYS_TYPE == 'Windows':
    download_file(
        "https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_win32.zip")
driver_file_ops()
