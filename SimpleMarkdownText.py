from asyncio.log import logger
import re
import tkinter
import tkinter.font as tkfont

from Constants import ATTENTION, LIGHT2
from outils import from_rgb_to_tkcolors


class SimpleMarkdownText(tkinter.Text):
    """
    Really basic Markdown display. Thanks to Bryan Oakley's RichText:
    https://stackoverflow.com/a/63105641/79125
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_font = tkfont.nametofont("TkTextFont")
        self.default_font.configure(size=14)
        self.em = self.default_font.measure("m")
        self.default_size = self.default_font.cget("size")
        self.bold_font = tkfont.Font(**self.default_font.configure())  # type: ignore
        self.italic_font = tkfont.Font(**self.default_font.configure())  # type: ignore

        self.bold_font.configure(weight="bold")
        self.italic_font.configure(slant="italic")

        # Small subset of markdown. Just enough to make text look nice.
        self.tag_configure("**", font=self.bold_font, foreground="orange")

        self.tag_chars = "*_"
        self.tag_char_re = re.compile(r"[*_]")

        header_font1 = tkfont.Font(**(self.default_font.configure()))  # type: ignore
        header_font1.configure(size=int(self.default_size + 8), weight="bold")

        header_font2 = tkfont.Font(**(self.default_font.configure()))  # type: ignore
        header_font2.configure(size=int(self.default_size + 5), weight="bold")

        header_font3 = tkfont.Font(**(self.default_font.configure()))  # type: ignore
        header_font3.configure(
            size=int(self.default_size + 3), weight="normal", slant="italic"
        )

        date_font = tkfont.Font(**(self.default_font.configure()))  # type: ignore
        date_font.configure(
            size=int(self.default_size - 4), weight="normal", slant="italic"
        )

        link_font = tkfont.Font(**(self.default_font.configure()))  # type: ignore
        link_font.configure(
            size=int(self.default_size - 2), weight="bold", slant="italic"
        )

        self.tag_configure(
            "#",
            foreground="orange",
            font=header_font1,
            spacing3=header_font1.cget("size"),
        )

        self.tag_configure(
            "##",
            foreground="yellow",
            font=header_font2,
            spacing3=header_font2.cget("size"),
        )

        self.tag_configure(
            "###",
            foreground="red",
            font=header_font3,
            spacing3=header_font3.cget("size"),
        )

        self.tag_configure(
            "date_font",
            foreground=from_rgb_to_tkcolors((0x90, 0xE0, 0xEF)),
            font=date_font,
            spacing3=date_font.cget("size"),
        )

        self.tag_configure(
            "hyperlink",
            foreground="white",
            underline=True,
            font=link_font,
        )

        self.lmargin2 = self.em + self.default_font.measure("\u2022 ")
        self.tag_configure("bullet", lmargin1=self.em, lmargin2=self.lmargin2)
        self.lmargin2 = self.em + self.default_font.measure("1. ")
        self.tag_configure("numbered", lmargin1=self.em, lmargin2=self.lmargin2)

        self.numbered_index = 1

    def clear_text(self):
        """
        efface le contenu du simpleMardownText
        """
        self.replace("1.0", tkinter.END, "")

    def get_text(self) -> str:
        return self.get("1.0", tkinter.END)

    def get_selection(self) -> str:
        """
        récupère le contenu de la sélection
        """
        try:
            return self.get(tkinter.SEL_FIRST, tkinter.SEL_LAST)
        except Exception as e:
            logger.warning(f"{ATTENTION} {e}")
            return str()

    def insert_bullet(self, position, text):
        self.insert(position, f"- {text}", "bullet")

    def insert_numbered(self, position, text):
        self.insert(position, f"{self.numbered_index}. {text}", "numbered")
        self.numbered_index += 1

    def insert_markdown(self, mkd_text):
        """
        #### A very basic markdown parser.

        Helpful to easily set formatted text in tk. If you want actual markdown
        support then use a real parser.
        """

        # teste si on ne se trouve pas dans un code
        # avant de formater la ligne avec des # par exemple
        in_code = False

        def tester_line(line:str):
             
            if line.startswith("### "):
                    line = line[3:]
                    self.insert("end", line, "###") 

            elif line.startswith("## "):
                line = line[2:]
                self.insert("end", line, "##") 

            elif line.startswith("# "):
                line = line[1:]
                self.insert("end", line, "#") 

            elif line.startswith("* "):
                line = line[2:]
                self.insert_bullet("end", line)

            elif line.startswith("1. "):
                line = line[2:]
                self.insert_numbered("end", line)

            elif line.startswith("CreatedAt: "):
                line = line[10:]
                self.insert("end", line, "date_font")

            elif not self.tag_char_re.search(line):
                self.insert("end", line)

            else:
                tag = None
                accumulated = []
                skip_next = False
                for i, c in enumerate(line):
                    if skip_next:
                        skip_next = False
                        continue
                    if c in self.tag_chars and (not tag or c == tag[0]):
                        if tag:
                            self.insert("end", "".join(accumulated), tag)
                            accumulated = []
                            tag = None
                        else:
                            self.insert("end", "".join(accumulated))
                            accumulated = []
                            tag = c
                            next_i = i + 1
                            if len(line) > next_i and line[next_i] == tag:
                                tag = line[i : next_i + 1]
                                skip_next = True

                    else:
                        accumulated.append(c)
                self.insert("end", "".join(accumulated), tag)  # type: ignore

        for line in mkd_text.split("\n"):
            if line == str():
                # Blank lines reset numbering
                self.numbered_index = 1
                self.insert("end", line)

            elif line.startswith("```"):
                in_code = not in_code

            elif in_code == False:
                tester_line(line)
                
            else:
                self.insert(tkinter.END, line)
                
            self.insert(tkinter.END, "\n")
