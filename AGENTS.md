# Repository Conventions for AI Agents

## Bibliography (`_bibliography/papers.bib`)
- **Ordering**: Entries are ordered by `year` descending (newest year first), and **within each year sorted alphabetically by author last names** (first author, then co-authors).
- **Refereed vs. Other publications**: `_pages/publications.md` splits entries into two tabs ("Refereed" and "Other publications") using `nonrefereed = {true}` on non-refereed entries. Add `nonrefereed = {true}` to preprints, technical reports, theses, and other non-refereed items.
- **Google Scholar tracking**:
  - Each entry with a Google Scholar record includes `google_scholar_id = {<id>}`.
  - Citation counts are cached in `_data/scholar_citations.csv` (updated daily by `.github/workflows/update-scholar-citations.yml` running `assets/code/check_references_from_Google_Scholar.py`).
  - Missing or mismatched Scholar entries are listed in `_data/missing_or_issues_with_Scholar_citations.csv`. When adding a missing entry to `_bibliography/papers.bib`, also add `<id>,0` to `_data/scholar_citations.csv` and remove its `missing` row from `_data/missing_or_issues_with_Scholar_citations.csv`.
