from PIL import ImageTk


class Article:
    source: str
    author: str
    title: str
    description: str
    url: str
    urlToImage: str
    publishedAt: str
    content: str
    image:ImageTk.PhotoImage|None

    def __init__(
        self, source:str, author:str, title:str, description:str, url:str, urlToImage:str, publishedAt:str, content,image:ImageTk.PhotoImage|None
    ) -> None:
        self.source=source
        self.author=author
        self.title=title
        self.description=description
        self.url=url
        self.urlToImage=urlToImage
        self.publishedAt=publishedAt
        self.content=content
        self.image=image
