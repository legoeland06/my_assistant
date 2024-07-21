# python
from googleapiclient.discovery import build
from Constants import STARS
import my_scrapper
import secret as sc

my_api_key = sc.GOOGLE_API_KEY
my_cse_id = sc.GOOGLE_CSE_ID
project_number = "728224194740"


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res["items"]


def main(texte):
    results = google_search(texte, my_api_key, my_cse_id, num=10)

    # Commentaires utiles
    # composition du json result
    # kind
    # title
    # htmlTitle
    # link
    # displayLink
    # snippet
    # htmlSnippet
    # formattedUrl
    # htmlFormattedUrl
    # pagemap

    return results


if __name__ == "__main__":
    import sys

    arguments = " ".join(sys.argv[1:])
    main(arguments)
