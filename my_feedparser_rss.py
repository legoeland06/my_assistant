import feedparser

from outils import translate_it


def lemonde(rss_url):
    rubrique = ""
    for item in rss_url:
        resultat = ""
        feed = feedparser.parse("https://www.lemonde.fr/" + item + "/rss_full.xml")

        for entry in feed.entries:
            resultat += entry.title_detail["value"] + "\n"
        rubrique += translate_it(resultat)

    return rubrique


def le_monde_informatique(rss_url):
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


def generic_search_rss(rss_url: list,nombre_items:int):
    rubrique = ""
    for search_item in rss_url:
        resultat = ""

        link_to_rss = (
            "https://news.google.com/rss/search?q="
            + search_item.replace(" ", "+")
            + "&hl=fr&gl=FR&ceid=FR:fr"
        )
        feed = feedparser.parse(link_to_rss)

        # pour le moment on ne prend que les 10 premières news
        for entry in feed.entries[:nombre_items]:
            resultat += entry.title + "\n"

        rubrique += (
            search_item.replace("+", " ")
            + ":\n*************************************\n"
            + resultat
            + "\n"
        )

    return rubrique


# if __name__ == "__main__":
#     generic_search_rss("sport","reuters.com")
