from Article import Article


class RechercheArticles():
    status:bool
    totalResults:int
    articles:list[Article]

    def __init__(self,status:bool,totalResults:int,articles:list[Article]) -> None:
        self.status=status
        self.totalResults=totalResults
        self.articles=articles
            