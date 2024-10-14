import requests
from bs4 import BeautifulSoup
import os

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
  for link in soup.select("a[href$='.pdf']"):
    count += 1
    # Extract file name from the link
    filename = os.path.join(folder_location, link['href'].split('/')[-1])

    with open(filename, 'wb') as f:
      f.write(requests.get(link['href']).content)
    print(f"Downloaded {count} - {filename}")

    #DEBUG stop at 1
    break

if __name__ == "__main__":
  url = "https://sfbos.org/ordinances-2024"  # Replace with the actual URL
  folder_location = "sfbos_ordinances_2024"  # Choose your desired folder name/path
  download_pdfs(url, folder_location)
