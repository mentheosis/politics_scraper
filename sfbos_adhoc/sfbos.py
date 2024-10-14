import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

def download_pdfs(url, folder_location):
    """
    Downloads all PDF files from a given URL and saves them to a specified folder.

    Args:
        url: The URL of the webpage containing the PDF links.
        folder_location: The path to the folder where the PDFs will be saved.
    """

    if not os.path.exists(folder_location):
        os.mkdir(folder_location)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    count = 0
    for table in soup.find_all('table'):
        for link in soup.select("a[href$='.pdf']"):
            # Extract file name from the link
            filename = os.path.join(folder_location, link['href'].split('/')[-1])
            if "committee_roster" in filename:
                continue

            remote_path = urljoin("http://sfbos.org", link['href'])
            with open(filename, 'wb') as f:
                f.write(requests.get(remote_path).content)
            count += 1
            print(f"Downloaded {count} - {filename}")

            #DEBUG stop
            if count >= 3:
                break

if __name__ == "__main__":
    url = "https://sfbos.org/ordinances-2024"
    folder_location = "sfbos_ordinances"
    download_pdfs(url, folder_location)
