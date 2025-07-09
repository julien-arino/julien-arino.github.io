import bibtexparser
from scholarly import scholarly
from fuzzywuzzy import fuzz
import argparse
import time
import csv
import random

BIB_PATH = '_bibliography/papers.bib'
SCHOLAR_USER_ID = 'DUa7u60AAAAJ'

def load_bib_entries(path):
    with open(path, 'r') as bibfile:
        bib_database = bibtexparser.load(bibfile)
    return bib_database.entries

def save_bib_entries(entries, path):
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = entries
    with open(path, 'w') as bibfile:
        writer = bibtexparser.bwriter.BibTexWriter()
        bibfile.write(writer.write(db))

def fetch_scholar_pubs(user_id):
    author = scholarly.search_author_id(user_id)
    pubs = list(scholarly.fill(author, sections=['publications'])['publications'])
    print(f"Found {len(pubs)} publications. Fetching details for each (this may take a while)...")
    for idx, pub in enumerate(pubs, 1):
        title = pub.get('bib', {}).get('title', '[No title]')
        print(f"  [{idx}/{len(pubs)}] Filling details for: {title}")
        try:
            scholarly.fill(pub)
        except Exception as e:
            print(f"    Error filling publication: {e}")
        time.sleep(random.uniform(0.5, 2.0))  # random delay to avoid throttling
    print("Finished fetching publication details.")
    return pubs

def match_entry(bib_entry, scholar_pubs):
    bib_title = bib_entry.get('title', '').lower()
    best_score = 0
    best_pub = None
    for pub in scholar_pubs:
        scholar_title = pub.get('bib', {}).get('title', '').lower()
        score = fuzz.token_set_ratio(bib_title, scholar_title)
        if score > best_score:
            best_score = score
            best_pub = pub
    return best_pub if best_score > 80 else None

def extract_scholar_id(pub):
    author_pub_id = pub.get('author_pub_id', '')
    if ':' in author_pub_id:
        return author_pub_id.split(':', 1)[1]
    return None

def sort_bib_entries(entries):
    def get_year(entry):
        try:
            return int(entry.get('year', 0))
        except Exception:
            return 0
    def get_author(entry):
        return entry.get('author', '').lower()
    # Sort by year (descending), then author (ascending)
    return sorted(entries, key=lambda e: (-get_year(e), get_author(e)))

def write_citations_csv(bib_entries, scholar_pubs, csv_path):
    # Build a mapping from scholar_id to citation count
    scholar_citations = {}
    for pub in scholar_pubs:
        scholar_id = pub.get('author_pub_id', '')
        if ':' in scholar_id:
            scholar_id = scholar_id.split(':', 1)[1]
        if scholar_id:
            citations = pub.get('num_citations', 0)
            scholar_citations[scholar_id] = citations

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['pub_id', 'citations'])
        for entry in bib_entries:
            pub_id = entry.get('google_scholar_id', '')
            citations = scholar_citations.get(pub_id, 0)
            writer.writerow([pub_id, citations])

def main(dry_run=False):
    bib_entries = load_bib_entries(BIB_PATH)
    scholar_pubs = fetch_scholar_pubs(SCHOLAR_USER_ID)

    print("\n=== DEBUG: All Google Scholar publications fetched ===")
    for idx, pub in enumerate(scholar_pubs, 1):
        print(f"\n[{idx}] {pub.get('bib', {}).get('title', '[No title]')}")
        print(pub)

    for entry in bib_entries:
        print(f"\nProcessing entry: {entry.get('title', '[No title]')}")
        matched_pub = match_entry(entry, scholar_pubs)
        if matched_pub:
            scholar_id = extract_scholar_id(matched_pub)
            scholar_year = matched_pub.get('bib', {}).get('pub_year', '')
            # Only update or check if a valid scholar_id is found
            if scholar_id:
                if not entry.get('google_scholar_id'):
                    print(f"Would add google_scholar_id for {entry.get('title')}: {scholar_id}")
                    if not dry_run:
                        entry['google_scholar_id'] = scholar_id
                elif entry['google_scholar_id'] != scholar_id:
                    print(f"Would correct google_scholar_id for {entry.get('title')}: {entry['google_scholar_id']} -> {scholar_id}")
                    if not dry_run:
                        entry['google_scholar_id'] = scholar_id
                # Check year (compare as strings, strip whitespace)
                if 'year' in entry and scholar_year and entry['year'].strip() != str(scholar_year).strip():
                    print(f"Year mismatch for {entry.get('title')}: bib={entry['year']} scholar={scholar_year}")
            else:
                print(f"  Matched in Scholar, but could not extract Scholar ID for: {entry.get('title')}")
        else:
            print(f"No Scholar match for: {entry.get('title')}")

    sorted_entries = sort_bib_entries(bib_entries)
    if not dry_run:
        save_bib_entries(sorted_entries, BIB_PATH)
        # Write citations CSV with only pub_id and citations
        write_citations_csv(sorted_entries, scholar_pubs, '_data/scholar_citations.csv')
    else:
        print("\nDry run mode: No changes were written to the bib file.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check and update bib entries with Google Scholar info.")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be done, but don't write changes.")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
