# Repository Conventions for AI Agents

## Bibliography (`_bibliography/papers.bib`)
- **Ordering**: Entries are ordered by `year` descending (newest year first), and **within each year sorted alphabetically by author last names** (first author, then co-authors).
- **Refereed vs. Preprints vs. Other publications**: `_pages/publications.md` splits entries into three tabs ("Refereed", "Preprints", and "Other publications") using `pubtype = {refereed}`, `pubtype = {preprint}`, or `pubtype = {other}` on every entry in `_bibliography/papers.bib`. Use `pubtype = {preprint}` for arXiv/SSRN/Research Square preprints, `pubtype = {other}` for books, book chapters, technical reports, editorials, reviews, edited volumes, and non-refereed articles, and `pubtype = {refereed}` for refereed publications (including the PhD thesis).
- **Google Scholar tracking**:
  - Each entry with a Google Scholar record includes `google_scholar_id = {<id>}`.
  - Citation counts are cached in `_data/scholar_citations.csv` (updated daily by `.github/workflows/update-scholar-citations.yml` running `assets/code/check_references_from_Google_Scholar.py`).
  - Missing or mismatched Scholar entries are listed in `_data/missing_or_issues_with_Scholar_citations.csv`. When adding a missing entry to `_bibliography/papers.bib`, also add `<id>,0` to `_data/scholar_citations.csv` and remove its `missing` row from `_data/missing_or_issues_with_Scholar_citations.csv`.
