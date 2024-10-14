import json
import sys
from llm.genericllm import GenericLLM
from data_sources.web_page_scraper import WebPageScraper

llm = GenericLLM()
scraper = WebPageScraper()

def extract_position_from_voter_guide(election, source, text, issue):
    prompt = "Following is the text of " + source["name"] + ". Your job is to determine"
    prompt += " if the author of the text supports or opposes the passing of " + issue + "."
    prompt += " Reply with only 'support' or 'oppose' or 'none' if the text does not discuss the position of the voter guide. Do not include any other text in your reply."
    # Break text into 2048 chqaracter chunks with 512 character overlap
    chunks = [text[i:i+2048] for i in range(0, len(text), 1536)]
    print("[VoterGuideIngester] Number of chunks:\n " + str(len(chunks)))
    for chunk in chunks:
        print("[VoterGuideIngester] Processing chunk\n")
        position = llm.generate_content(prompt, chunk)
        position = position.split("\n")[0]
        if position == "support":
            return True
        elif position == "oppose":
            return False
    return None    
def ingest_voter_guide(election, source):
    url = source["url"]
    text = scraper.recursive_scrape(url, source["url_filter"])
    text = "\n".join(text)
    data = []
    for issue in election["issues"]:
        position = extract_position_from_voter_guide(election, source, text, issue)
        if position == True:
            data.append({"source": source["name"], "issue": issue, "position": "support"})
        elif position == False:
            data.append({"source": source["name"], "issue": issue, "position": "oppose"})
    return data
    print(len(text))

election_json = sys.argv[1]
source_json = sys.argv[2]
with open(election_json) as f:
    election_info = json.load(f)
with open(source_json) as f:
    source_info = json.load(f)
    
print("Ingesting source info from " + source_info["name"])
if source_info["type"] != "voter-guide":
    print("Source type not supported")
    sys.exit(1)
data = ingest_voter_guide(election_info, source_info)
print(data)


