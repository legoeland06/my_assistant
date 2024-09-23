import re
from tkinter import simpledialog

from StoppableThread import StoppableThread
from outils import load_txt


def myGrep(
    text_file: str,
    pattern: str,
    before: int,
    after: int,
):
    suzy = text_file.splitlines()

    final = str()
    for n, line in enumerate(suzy):
        mom_match = re.search(
            pattern=" " + pattern + " ", string=line, flags=re.IGNORECASE
        )
        if mom_match:
            result = str()
            print(f"{mom_match.span()}::{mom_match.string}")
            print("****************************************************")
            audrey = "\n".join(
                suzy[
                    (
                        max(0, n - before)
                        if mom_match.span()[0] != 0 or len(line) < 500
                        else 0
                    ) : min(len(suzy) if len(line) < 500 else len(line), n + after)
                ]
            )
            result = makeItBold(pattern, audrey)
            final += result + "\n\n"

    return final


def makeItBold(pattern: str, audrey: str):
    """
    met en gras les mots du paragraphe qui correspondent au pattern
    """
    result = str()
    for word in audrey.split():
        if pattern.lower() == word.lower():
            result += f" **{word}** "
        else:
            result += f" {word} "
    return result


def main(textFile, pattern):
    mythread = StoppableThread(
        None,
        name="my_thread",
        target=lambda: lance_grep(textFile, pattern),
    )
    mythread.daemon = True
    mythread.start()

def lance_grep(textFile, pattern) -> str:
    task = myGrep(
        text_file=textFile,
        pattern=pattern,
        before=2,
        after=5,
    )
    if isinstance(task, str) and task.__len__():
        return task
    else:
        return "Aucune occurrence trouvée"


if __name__ == "__main__":
    pattern = simpledialog.askstring(
        title="Motclé",
        prompt="Entrez le motclé à investiguer : ",
        initialvalue="Yeux",
    )

    if pattern:
        _ = main(load_txt(None), pattern)
