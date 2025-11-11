import time
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
                link_struct["kab_num"] = f"<b>Кабинет:</b> {line}"
                continue
            if line.startswith("город "):
                link_struct["address"] = f"<b>Адрес:</b> {line}"
                continue
            if line.startswith("IP:") or line.startswith("Резервный сайт:"):
                link_struct["reserve"] = f"<b>Резервный сайт:</b> {line.strip("Резервный сайт: ")}"
                continue
            if line.find(".mcko.ru") > -1:
                link_struct["link"] = f"<b>Сайт:</b> {line}"
                continue
        return link_struct
