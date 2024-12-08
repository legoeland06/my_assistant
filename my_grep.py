import re
from tkinter import simpledialog

from StoppableThread import StoppableThread


async def my_grep(
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
            result = await make_it_bold(pattern, audrey)
            final += result + "\n\n"

    return final


async def make_it_bold(pattern: str, audrey: str):
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


async def main(text_file, pattern):
    mythread = StoppableThread(
        None,
        name="my_thread",
        target=lambda: lance_grep(text_file, pattern),
    )
    mythread.daemon = True
    mythread.start()
    


async def lance_grep(text_file, pattern) -> str:
    task = await my_grep(
        text_file=text_file,
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
        import outils

        _ = main(outils.load_txt(None), pattern)
