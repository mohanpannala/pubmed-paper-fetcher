import argparse  #module to handle command-line arguments
from pubmed_fetcher.fetch import fetch_and_process_papers #module for the core processing function from your module

def main():
    # Creating a parser object for command-line arguments
    parser = argparse.ArgumentParser(
        description="Fetch PubMed papers with company affiliations"
    )

    # Positional argument: required to search query
    parser.add_argument(
        "query",
        type=str,
        help="PubMed search query (e.g., 'cancer immunotherapy')"
    )

    # Optional argument to output CSV filename
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Filename to save results as CSV (e.g., output.csv)"
    )

    # Optional flag to enable debug output
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug output for troubleshooting"
    )

    # to Parse the command-line arguments into `args`
    args = parser.parse_args()

    # Calling the core function with provided arguments
    fetch_and_process_papers(
        args.query,
        output_file=args.file,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
