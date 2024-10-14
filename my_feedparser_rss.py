import feedparser


def lemonde(rss_url: list):
    rubrique = []
    for item in rss_url:
        resultat = ""
        feed = feedparser.parse("https://www.lemonde.fr/" + item + "/rss_full.xml")

        for entry in feed.entries:
            resultat += entry.title_detail["value"] + "\n"
        rubrique.append(resultat)

    return rubrique


def lemonde_afrique(rss_url):
    rubrique = []
    for item in rss_url:
        resultat = ""
        feed = feedparser.parse("https://www.lemonde.fr/" + item + "/rss_full.xml")

        for entry in feed.entries:
            resultat += entry.title_detail["value"] + "\n"
            resultat += str(entry.description) + "\n"
        rubrique.append(resultat)

    return rubrique


def le_monde_informatique(rss_url):
    rubrique = []
    for item in rss_url:
        resultat = ""
        feed = feedparser.parse(
            "https://www.lemondeinformatique.fr/flux-rss/" + item + "/rss.xml"
        )

        for entry in feed.entries:
            resultat += entry.title_detail["value"] + "\n"
        rubrique.append(resultat)

    return rubrique


def generic_search_rss(rss_url: list, nombre_items: int):
    rubrique = []
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

        rubrique.append(
            search_item.replace("+", " ")
            + ":\n*************************************\n"
            + resultat
            + "\n"
        )

    return rubrique


def linforme(nombre_items: int):
    rubrique = []
    links = "https://www.linforme.com/rss/all_headline.xml"
    links2 = (
            "https://news.google.com/rss/search?q="
            + "&hl=fr&gl=FR&ceid=FR:fr"
        )

    for lien in [links, links2]:
        resultat = str()
        feed = feedparser.parse(lien)

        print(f"FEED::{feed}")
        # pour le moment on ne prend que les 10 premières news
        for entry in feed.entries:
            resultat += entry.title + "\n"

        rubrique.append(
            "L'informé.com:\n*************************************\n" + resultat + "\n"
        )
        if len(rubrique)>=nombre_items:
            return rubrique

    return rubrique
