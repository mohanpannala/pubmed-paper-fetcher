# PubMed Paper Fetcher

This project fetches research papers from PubMed based on a search query, filters for papers with at least one author affiliated with a **pharmaceutical or biotech** company, and outputs the results as a CSV file.

## 🚀 Features

- Fetches papers using **PubMed E-utilities API**
- Filters authors based on **non-academic** affiliations
- Extracts:
  - PubMed ID
  - Title
  - Publication Date
  - Non-academic authors
  - Company affiliations
  - Corresponding author email
- CLI interface with output to **CSV** or **console**

## 🔧 Installation

```bash
git clone https://github.com/mohanpannala/pubmed-paper-fetcher.git
cd pubmed-paper-fetcher
poetry install
```

## 🧪 Usage

```bash
poetry run get-papers-list "your pubmed query here"
```

## License

MIT License © 2024 Mohan Pannala