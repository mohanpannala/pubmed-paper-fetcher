import requests
import csv
import re
from typing import List, Optional, Dict, Any
from xml.etree import ElementTree

# Keywords used to detect company or academic affiliation
COMPANY_KEYWORDS = ["pharma", "biotech", "therapeutics", "inc", "ltd", "llc", "gmbh", "laboratories", "solutions"]
ACADEMIC_KEYWORDS = ["university", "institute", "college", "hospital", "school", "department", "center", "centre", "academy"]

#function to check if an affiliation string belongs to a company, not academia.
def is_company_affiliation(affiliation: str) -> bool:

    affiliation = affiliation.lower()
    return (
        any(word in affiliation for word in COMPANY_KEYWORDS)
        and not any(word in affiliation for word in ACADEMIC_KEYWORDS)
    )


#function to Extract non-academic authors, company affiliations, and the corresponding author's email.
def extract_authors_info(authors: List[Dict[str, Any]]) -> (List[str], List[str], Optional[str]):
    
    non_academic_authors = []
    company_affiliations = set()
    corresponding_email = None

    for author in authors:
        name = f"{author.get('LastName', '')} {author.get('ForeName', '')}".strip()
        affiliations = author.get('AffiliationInfo', [])

        for aff in affiliations:
            aff_text = aff.get('Affiliation', '')

            # Checking if this is a company affiliation
            if is_company_affiliation(aff_text):
                non_academic_authors.append(name)
                company_affiliations.add(aff_text)

            # Extracting the first email found in any affiliation (for corresponding author)
            if not corresponding_email:
                email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", aff_text)
                if email_match:
                    corresponding_email = email_match.group(0)

    return non_academic_authors, list(company_affiliations), corresponding_email


#Function Fetching PubMed IDs from the esearch endpoint based on the user's query.
def fetch_pubmed_ids(query: str, debug: bool = False) -> List[str]:
    
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmax": 100, "retmode": "json"}
    response = requests.get(url, params=params)
    response.raise_for_status()

    if debug:
        print("PubMed ID Fetch Response:", response.json())

    return response.json()["esearchresult"]["idlist"]

#Function to fetch detailed paper information using the efetch endpoint.
def fetch_pubmed_details(pubmed_ids: List[str], debug: bool = False) -> List[Dict[str, Any]]:

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": ",".join(pubmed_ids), "retmode": "xml"}
    response = requests.get(url, params=params)
    response.raise_for_status()

    if debug:
        print("Raw XML fetched")

    return parse_pubmed_xml(response.text)


#Function to Parse the XML response and extract paper information.
def parse_pubmed_xml(xml_str: str) -> List[Dict[str, Any]]:
    
    root = ElementTree.fromstring(xml_str)
    results = []

    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")

        # Extracting the publication date
        pub_date_el = article.find(".//PubDate")
        pub_date = ""
        if pub_date_el is not None:
            year = pub_date_el.findtext("Year") or ""
            month = pub_date_el.findtext("Month") or ""
            day = pub_date_el.findtext("Day") or ""
            pub_date = f"{year}-{month}-{day}".strip("-")

        # Extracting the all authors
        authors = []
        for author in article.findall(".//Author"):
            author_data = {
                "LastName": author.findtext("LastName"),
                "ForeName": author.findtext("ForeName"),
                "AffiliationInfo": [
                    {"Affiliation": aff.findtext("Affiliation")}
                    for aff in author.findall("AffiliationInfo")
                ]
            }
            authors.append(author_data)

        #logic to find non-academic authors and emails
        non_acad_authors, company_affs, email = extract_authors_info(authors)

        #Only include papers with at least one company-affiliated author
        if non_acad_authors:
            results.append({
                "PubmedID": pmid,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academicAuthor(s)": "; ".join(non_acad_authors),
                "CompanyAffiliation(s)": "; ".join(company_affs),
                "Corresponding Author Email": email or "N/A"
            })

    return results


#function that fetches, filters, and either prints or saves the paper data.
def fetch_and_process_papers(query: str, output_file: Optional[str], debug: bool = False) -> None:

    try:
        #To Get matching PubMed IDs
        pubmed_ids = fetch_pubmed_ids(query, debug)

        if not pubmed_ids:
            print("No papers found.")
            return

        #To Get full paper details for those IDs
        papers = fetch_pubmed_details(pubmed_ids, debug)

        # To Save file or print to console
        if output_file:
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "PubmedID", "Title", "Publication Date",
                    "Non-academicAuthor(s)", "CompanyAffiliation(s)",
                    "Corresponding Author Email"
                ])
                writer.writeheader()
                writer.writerows(papers)
            print(f"Results saved to {output_file}")
        else:
            for paper in papers:
                print(paper)

    except Exception as e:
        print("Error:", str(e))
