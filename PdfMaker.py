import os
import fpdf


def _transformer(text_list: list, n: int) -> list:
    """
    prend une liste `l` et un entier `m` en entrée, et renvoie une liste 
    de sous-listes, chacune contenant `m` éléments de la liste originale
    """
    return [text_list[i : i + n] for i in range(0, len(text_list), n)]


def makePdfFromTtext(text_list: list,filename:str):
    pdf: fpdf.FPDF = fpdf.FPDF("portrait", "mm", "A4")
    basepath=os.path.abspath(os.path.join(__file__, "..", ".."))
    # Add a Unicode font (uses UTF-8)
    pdf.add_font('Trebuchet', '', "fonts/trebuc.ttf", uni = True)
    # pdf.add_font('Trebuchet', '', \
    #     os.path.join(".", "font", 'trebuc.ttf'), \
    #     uni = True)
    pdf.set_font('Trebuchet', '', 10)
    # pdf.set_font(
    #     "Arial",
    #     size=10,
    # )

    pages = _transformer(text_list, 40)

    for page in pages:
        pdf.add_page()
        for line in page:
            pdf.cell(
                0,
                5,
                line,
                0,
                1,
                "L",
                False,
                "",
            )

    # Save the PDF file
    pdf.output(filename+".pdf", "F")
