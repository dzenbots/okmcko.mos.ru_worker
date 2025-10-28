from collections import defaultdict
from pathlib import Path

import fitz


class PdfParser:
    path: Path

    def __init__(self, path: Path):
        if not path.exists():
            raise FileNotFoundError
        self.path = path

    def get_diag_link(self):
        doc = fitz.open(self.path)
        pdftext = ""
        link_struct = dict()
        for page in doc:
            pdftext += page.get_text()
        pdf_lines = pdftext.split("\n")
        for line in pdf_lines:
            if line.startswith("ЛИСТ ФИКСАЦИИ РАБОЧИХ МЕСТ"):
                break
            if line.startswith("этаж "):
                link_struct["kab_num"] = line
            if line.startswith("город "):
                link_struct["address"] = line
            if line.startswith("Адрес сайта диагностики:"):
                link_struct["link"] = line
            if line.startswith("IP:"):
                link_struct["ip"] = line
                break
        return link_struct
