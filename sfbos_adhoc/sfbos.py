import requests
import sys
import os, re, json
import PyPDF2
from bs4 import BeautifulSoup
from urllib.parse import urljoin

DEBUG_FILE = None # "o0032-24.pdf"

def download_pdfs(url, folder_location, max_files=3):
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
        # for link in soup.select("a[href$='.pdf']"):
        for row in soup.find_all('tr'):
            columns = row.find_all('td')
            try:
                link = columns[1].find('a')['href']
            except:
                # first row is header, doesnt have a link
                continue

            filename = os.path.join(folder_location, link.split('/')[-1])
            title = columns[3].text.strip()

            # Extract file name from the link
            if "committee_roster" in filename:
                continue

            if not os.path.exists(filename):
                remote_path = urljoin("http://sfbos.org", link)
                with open(filename, 'wb') as f:
                    f.write(requests.get(remote_path).content)
                print(f"Downloaded {count} - {filename}")
            else:
                print(f"File {count} {filename} already downloaded")

            # print("Found title of file?", filename, title)
            json_filepath = filename.replace("pdf","json")
            if not os.path.exists(json_filepath):
                with open(json_filepath, "w") as f:
                    json.dump({"title": title}, f, indent=2)

            count += 1
            if count >= max_files:
                break

def check_supervisor_votes(text, vote_type):
    text = text.replace("\n"," ")
    text = text.replace("Ayes: 1 O", "Ayes: 10") # just directly manually repair known PDF text errors..
    # if "PASSED" in text:
    if DEBUG_FILE:
        print("\nDebug text:", text)

    results = []
    matches = re.findall(fr"{vote_type}:\s*(\d+)\s*([\w\s,-]+)(?=Ayes|Excused|Noes|Absent|\.|\d|$)", text)
    for target, words in matches:
        votes = []
        target = int(target)

        captured_words = words.replace(" and ",", ").split(",")
        word_count = 0
        for word in captured_words:
            if word_count == target - 1:
                '''
                    we should be at the last name in the list now, so there will be no more commas and there will be other random
                    words following the name, so we can split on space here and just take the first word
                '''
                votes.append(word.split()[0].replace("-",""))
            elif word_count < target:
                # try to clean up weird pdf artifacts in the names
                votes.append(word.replace(",","").replace("-","").replace(" ","").strip())
                word_count += 1
            elif word_count >= target:
                break
        # results.append({vote_type: votes})
        results = votes # take the last vote in each doc for now, this should be when it actually passed

    return results


def extract_votes_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A string containing the extracted text.
    """
    votes = {}
    try:
        # Extract text from the PDF
        full_text = ""
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                full_text += text
            aye_votes = check_supervisor_votes(full_text, "Ayes")
            abstain_votes = check_supervisor_votes(full_text, "Excused")
            no_votes = check_supervisor_votes(full_text, "Noes")
            absent_votes = check_supervisor_votes(full_text, "Absent")
            total_votes = len(aye_votes) + len(abstain_votes) + len(no_votes) + len(absent_votes)
            votes = {
                "Ordinance": pdf_path,
                "Ayes": aye_votes,
                "Noes": no_votes,
                "Abstain": abstain_votes,
                "Absents": absent_votes
            }
            if total_votes < 11:
                print("Found incomplete vote", len(aye_votes) + len(abstain_votes), pdf_path)
                print("Ayes", aye_votes)
                print("Noes", no_votes)
                print("Abstain", abstain_votes)
                print("Absents", absent_votes)
                # raise Exception("Incomplete votes.") # just ignore and move on

        # Process the extracted text here
        # print(f"Extracted text from {pdf_path}")
        # return full_text
    except PyPDF2.utils.PdfReadError:
        print(f"Error reading {pdf_path}: Could not read the PDF.")
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

    return votes

def run_main():
    url = "https://sfbos.org/ordinances-2024"
    save_files_to_dir = "sfbos_ordinances"
    print("Checking for PDFs and downloading...")
    download_pdfs(url, save_files_to_dir, max_files=9999)

    votes = []
    print("\nAnalyzing votes...")
    if DEBUG_FILE:
        # Debug method
        pdf_path = os.path.join(save_files_to_dir, DEBUG_FILE)
        votes.append(extract_votes_from_pdf(pdf_path))
    else:
        files = os.listdir(save_files_to_dir)
        files.sort()
        for filename in files:
            if filename.endswith(".pdf"):
                json_filepath = os.path.join(save_files_to_dir, filename.replace("pdf","json"))

                file_votes = {}
                if os.path.exists(json_filepath):
                    print("Loading cached votes from", json_filepath)
                    with open(json_filepath, "r") as f:
                        file_votes = json.load(f)
                        '''
                            The json file will have been created to store the ordinance title, but if it doesnt
                            have the vote data yet then we still need to process the pdf file and update the json
                        '''
                        if file_votes.get("Ayes"):
                            votes.append(file_votes)

                if not file_votes.get("Ayes"): # either json doesnt exist, or hasnt had vote data written yet
                    print("Analyzing", filename)
                    pdf_path = os.path.join(save_files_to_dir, filename)
                    file_votes.update(extract_votes_from_pdf(pdf_path))
                    votes.append(file_votes)

                    # Cache analyzed file in json saved to disk
                    with open(json_filepath, "w") as f:
                        json.dump(file_votes, f, indent=2)

    print("\nResults: ")
    non_unanimous = []
    counter = 0
    for ordinance in votes:
        if len(ordinance["Noes"]) > 0:
            counter += 1
            non_unanimous.append(ordinance)
            print(f"Ayes {len(ordinance['Ayes'])} Noes {len(ordinance['Noes'])} ({','.join(ordinance['Noes'])}), {ordinance['title']}")

    print(f"Totals: {len(non_unanimous)} ordinances with dissenting votes")
    # print(json.dumps(non_unanimous,indent=2))


if __name__ == "__main__":
    # Disable buffering for stdout
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)  # Python 3.7+
    else:
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # Older Python versions
    run_main()
