import bibtexparser
from scholarly import scholarly, ProxyGenerator
import argparse
import time
import csv
import random

BIB_PATH = '_bibliography/papers.bib'
SCHOLAR_USER_ID = 'DUa7u60AAAAJ'

def load_bib_entries(path):
    with open(path, 'r', encoding='utf-8') as bibfile:
        bib_database = bibtexparser.load(bibfile)
    return bib_database.entries

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
            print(f"Found {len(pubs)} publications on Google Scholar profile.")
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

def extract_scholar_id(pub):
    author_pub_id = pub.get('author_pub_id', '')
    if ':' in author_pub_id:
        return author_pub_id.split(':', 1)[1]
    return None

def write_citations_csv(bib_entries, scholar_pubs_dict, csv_path):
    # Map each unique google_scholar_id in the bib file to its citations count
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['pub_id', 'citations'])
        seen_ids = set()
        for entry in bib_entries:
            pub_id = entry.get('google_scholar_id', '').strip()
            if pub_id and pub_id not in seen_ids:
                citations = scholar_pubs_dict.get(pub_id, {}).get('num_citations', 0)
                writer.writerow([pub_id, citations])
                seen_ids.add(pub_id)

def write_issues_csv(issues, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['title', 'pub_year', 'citations', 'google_scholar_id', 'status'])
        for issue in issues:
            writer.writerow([
                issue.get('title', ''),
                issue.get('pub_year', ''),
                issue.get('citations', 0),
                issue.get('google_scholar_id', ''),
                issue.get('status', '')
            ])

def main(dry_run=False):
    print("Loading bib entries from papers.bib...")
    bib_entries = load_bib_entries(BIB_PATH)
    
    print("Fetching publications from Google Scholar...")
    scholar_pubs = fetch_scholar_pubs(SCHOLAR_USER_ID)

    # Map scholar_id from Scholar profile to publication data
    scholar_pubs_dict = {}
    for pub in scholar_pubs:
        scholar_id = extract_scholar_id(pub)
        if scholar_id:
            scholar_pubs_dict[scholar_id] = pub

    # Analyze bib file entries by google_scholar_id
    scholar_id_to_bib_entries = {}
    for entry in bib_entries:
        pub_id = entry.get('google_scholar_id', '').strip()
        if pub_id:
            if pub_id not in scholar_id_to_bib_entries:
                scholar_id_to_bib_entries[pub_id] = []
            scholar_id_to_bib_entries[pub_id].append(entry)

    issues = []

    # 1. Detect Duplicated Scholar IDs in the bib file
    for sid, entries in scholar_id_to_bib_entries.items():
        if len(entries) > 1:
            citations = scholar_pubs_dict.get(sid, {}).get('num_citations', 0)
            for entry in entries:
                issues.append({
                    'title': entry.get('title', ''),
                    'pub_year': entry.get('year', ''),
                    'citations': citations,
                    'google_scholar_id': sid,
                    'status': 'duplicated'
                })

    # 2. Detect Erroneous Scholar IDs in the bib file
    for sid, entries in scholar_id_to_bib_entries.items():
        if sid not in scholar_pubs_dict:
            for entry in entries:
                issues.append({
                    'title': entry.get('title', ''),
                    'pub_year': entry.get('year', ''),
                    'citations': 0,
                    'google_scholar_id': sid,
                    'status': 'erroneous'
                })

    # 3. Detect Missing Publications (on Scholar profile but not in the bib file)
    for sid, pub in scholar_pubs_dict.items():
        if sid not in scholar_id_to_bib_entries:
            title = pub.get('bib', {}).get('title', '')
            pub_year = pub.get('bib', {}).get('pub_year', '')
            citations = pub.get('num_citations', 0)
            issues.append({
                'title': title,
                'pub_year': pub_year,
                'citations': citations,
                'google_scholar_id': sid,
                'status': 'missing'
            })

    # Sort issues by status, then title for consistent output
    issues.sort(key=lambda x: (x['status'], x['title'].lower()))

    if dry_run:
        print("\n=== DRY RUN MODE: No files will be modified ===")
        # Count unique google_scholar_ids in bib file
        unique_bib_ids = {entry.get('google_scholar_id', '').strip() for entry in bib_entries if entry.get('google_scholar_id', '').strip()}
        print(f"Would write {len(unique_bib_ids)} unique citations to _data/scholar_citations.csv")
        print(f"Would write {len(issues)} issues to _data/missing_or_issues_with_Scholar_citations.csv")
        print("\nIssues found:")
        for issue in issues:
            print(f"  [{issue['status'].upper()}] {issue['title']} (ID: {issue['google_scholar_id']})")
    else:
        print("Writing citation count CSV...")
        write_citations_csv(bib_entries, scholar_pubs_dict, '_data/scholar_citations.csv')
        
        print("Writing issues CSV...")
        write_issues_csv(issues, '_data/missing_or_issues_with_Scholar_citations.csv')
        print("Done.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check bib entries against Google Scholar info.")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be done, but don't write changes.")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
