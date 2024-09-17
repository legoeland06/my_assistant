from typing import Literal
import fpdf


class PDF(fpdf.FPDF):
    iamodel:str

    def __init__(self, orientation: Literal[''] | Literal['portrait'] | Literal['p'] | Literal['P'] | Literal['landscape'] | Literal['l'] | Literal['L'] = "portrait", unit: float | Literal['pt'] | Literal['mm'] | Literal['cm'] | Literal['in'] = "mm", format: tuple[float, float] | Literal[''] | Literal['a3'] | Literal['A3'] | Literal['a4'] | Literal['A4'] | Literal['a5'] | Literal['A5'] | Literal['letter'] | Literal['Letter'] | Literal['legal'] | Literal['Legal'] = "A4") -> None:
        super().__init__(orientation, unit, format)
    
    def set_iamodel(self,iamodel:str):
        self.iamodel=iamodel

    def header(self):
        # Logo
        self.image("banniere.jpeg", 10, 8, 33)
        # Arial bold 15
        self.set_font("Arial", "B", 8)
        # Title
        self.cell(0, 10, self.iamodel, 0, 1, "R")
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font("Arial", "I", 8)
        # Page number
        self.cell(0, 5, "page " + str(self.page_no()) + "/{nb}", 0, 0, "C")


def _transformer(text_list: list, n: int) -> list:
    """
    Prend une liste `l` et un entier `m` en entrée, et renvoie une liste
    de sous-listes, chacune contenant `m` éléments de la liste originale
    """
    return [text_list[i : i + n] for i in range(0, len(text_list), n)]


def makePdfFromTtext(text_list: list, filename: str):
    pdf: PDF = PDF("portrait", "mm", "A4")
    pdf.set_iamodel(filename)
    # Add a Unicode font (uses UTF-8)
    pdf.add_font("Trebuchet", "", "fonts/trebuc.ttf", uni=True)

    pages = _transformer(text_list, 40)
    pdf.alias_nb_pages()

    for page in pages:
        pdf.add_page()

        pdf.set_font("Trebuchet", "", 10)
        for line in page:
            pdf.cell(0, 5, line, 0, 1, "L", False, "")

    # Save the PDF file
    pdf.output(filename + ".pdf", "F")
