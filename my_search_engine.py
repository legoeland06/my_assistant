
"""
This module provides functionality to perform a Google Custom Search using the Google API.

Functions:
    google_search(search_term, api_key, cse_id, **kwargs):
        Performs a Google Custom Search and returns the search results.

    main(texte):
        Main function to execute the Google search with the provided text.

Constants:
    my_api_key: API key for accessing Google Custom Search API.
    my_cse_id: Custom Search Engine ID.
    project_number: Project number associated with the Google API.

Usage:
    Run this script from the command line with the search query as arguments.
    Example: python my_search_engine.py "search query"
"""
import asyncio
from googleapiclient.discovery import build
from Constants import STARS
import secret as sc

my_api_key = sc.GOOGLE_API_KEY
my_cse_id = sc.GOOGLE_CSE_ID
project_number = sc.PROJECT_NUMBER


async def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    print(STARS * 10)
    print(res)
    print(STARS * 10)
    return res["items"]


async def main(texte):
    results = await google_search(texte, my_api_key, my_cse_id)
    return results


if __name__ == "__main__":
    import sys

    arguments = " ".join(sys.argv[1:])
    asyncio.run(main(arguments))
