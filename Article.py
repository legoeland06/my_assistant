from PIL import ImageTk


class Article:
    source: str
    author: str
    title: str
    description: str
    url: str
    content: str
    image: ImageTk.PhotoImage | None

    def __init__(
        self,
        source: str,
        author: str,
        title: str,
        description: str,
        url: str,
        url_to_image: str,
        published_at: str,
        content,
        image: ImageTk.PhotoImage | None,
    ) -> None:
        self.source = source
        self.author = author
        self.title = title
        self.description = description
        self.url = url
        self.url_to_image = url_to_image
        self.published_at = published_at
        self.content = content
        self.image = image
