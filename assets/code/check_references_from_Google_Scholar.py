import bibtexparser
from scholarly import scholarly, ProxyGenerator
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
        writer.order_entries_by = None  # Preserve the custom sorting order
        writer.align_values = False     # Do not insert large spaces for vertical alignment
        bibfile.write(writer.write(db))

def fetch_scholar_pubs(user_id, max_retries=5):
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries} to configure proxies and fetch author profile...")
            pg = ProxyGenerator()
            success = pg.FreeProxies()
            if not success:
                print("  Warning: FreeProxies() returned False, proxies might not be configured properly.")
            scholarly.use_proxy(pg)
            
            author = scholarly.search_author_id(user_id)
            pubs = list(scholarly.fill(author, sections=['publications'])['publications'])
            print(f"Found {len(pubs)} publications. Fetching details for each (this may take a while)...")
            for idx, pub in enumerate(pubs, 1):
                # We can get the details directly from the author profile without filling the publication
                print(f"  [{idx}/{len(pubs)}] Processing: {pub.get('bib', {}).get('title', '')}")
                try:
                    scholar_title = pub.get('bib', {}).get('title', '')
                    citations = pub.get('num_citations', 0)
                    pub_year = pub.get('bib', {}).get('pub_year', '')
                except Exception as e:
                    print(f"    Error processing publication: {e}")
                    continue
            print("Finished fetching publication details.")
            return pubs
        except Exception as e:
            print(f"Error fetching scholar pubs on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                sleep_time = random.uniform(5, 15)
                print(f"Waiting {sleep_time:.1f} seconds before retrying...")
                time.sleep(sleep_time)
            else:
                print("Max retries reached. Failing.")
                raise

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
        seen_ids = set()
        for entry in bib_entries:
            pub_id = entry.get('google_scholar_id', '')
            if pub_id and pub_id not in seen_ids:
                citations = scholar_citations.get(pub_id, 0)
                writer.writerow([pub_id, citations])
                seen_ids.add(pub_id)

def write_issues_csv(scholar_pubs, final_scholar_ids, duplicated_ids, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['title', 'pub_year', 'citations', 'google_scholar_id', 'status'])
        for pub in scholar_pubs:
            scholar_id = pub.get('author_pub_id', '')
            if ':' in scholar_id:
                scholar_id = scholar_id.split(':', 1)[1]
            if not scholar_id:
                continue
                
            status = None
            if scholar_id not in final_scholar_ids:
                status = 'missing'
            elif scholar_id in duplicated_ids:
                status = 'duplicated'
                
            if status:
                title = pub.get('bib', {}).get('title', '')
                pub_year = pub.get('bib', {}).get('pub_year', '')
                citations = pub.get('num_citations', 0)
                writer.writerow([title, pub_year, citations, scholar_id, status])

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
    
    final_scholar_ids = set()
    duplicated_ids = set()
    for entry in sorted_entries:
        pub_id = entry.get('google_scholar_id', '')
        if pub_id:
            if pub_id in final_scholar_ids:
                duplicated_ids.add(pub_id)
            else:
                final_scholar_ids.add(pub_id)

    if not dry_run:
        save_bib_entries(sorted_entries, BIB_PATH)
        # Write citations CSV with only pub_id and citations
        write_citations_csv(sorted_entries, scholar_pubs, '_data/scholar_citations.csv')
        write_issues_csv(scholar_pubs, final_scholar_ids, duplicated_ids, '_data/missing_or_issues_with_Scholar_citations.csv')
    else:
        print("\nDry run mode: No changes were written to the bib file.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check and update bib entries with Google Scholar info.")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be done, but don't write changes.")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
