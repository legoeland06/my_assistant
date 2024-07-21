import feedparser

from outils import translate_it


def main_monde(rss_url):
    rubrique = ""
    for item in rss_url:
        resultat = ""
        feed = feedparser.parse("https://www.lemonde.fr/" + item + "/rss_full.xml")

        for entry in feed.entries:
            resultat += entry.title_detail["value"] + "\n"
        rubrique += translate_it(resultat)

    return rubrique


def main_monde_informatique(rss_url):
    rubrique = ""
    for item in rss_url:
        resultat = ""
        feed = feedparser.parse(
            "https://www.lemondeinformatique.fr/flux-rss/" + item + "/rss.xml"
        )

        for entry in feed.entries:
            resultat += entry.title_detail["value"] + "\n"
        rubrique += translate_it(resultat)

    return rubrique


# if __name__ == "__main__":
#     import sys

#     main(sys.argv[1:])
