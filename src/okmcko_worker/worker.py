import asyncio
import datetime
import zipfile
from pathlib import Path
from typing import Optional

import fitz
import requests
from bs4 import BeautifulSoup
from playwright.async_api import Browser, async_playwright, BrowserContext, Page

from settings import settings, FileEntry, File


class OkMckoWorker:
    _school_mos_ru_url = "https://school.mos.ru"
    _okmcko_mos_ru_url = "https://okmcko.mos.ru/index.php"
    _headless = True
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _page: Optional[Page] = None
    _mcko_files_list: Optional[list[FileEntry]] = None
    _new_files: Optional[list[FileEntry]] = None

    def __init__(self):
        self._headless = settings.DEBUG

    async def _init(self):
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(headless=self._headless is False)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()

    async def _school_mos_ru_auth(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        if self._page is None:
            await self._init()
        await self._page.goto(self._school_mos_ru_url)
        await self._page.wait_for_selector(".style_btn__3lIWs")
        await self._page.locator(".style_btn__3lIWs").click()
        await self._page.wait_for_selector("#login")
        await self._page.fill('input[id="login"]', login)
        await self._page.fill('input[id="password"]', password)
        await self._page.locator("#bind").click()
        await self._page.wait_for_selector(".systems_Wrapper__1h8Fz")

    async def _okmcko_ru_auth(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        if self._page is None:
            await self._init()
        if len(await self._context.cookies()) < 1:
            await self._school_mos_ru_auth(login=login, password=password)
        await self._page.get_by_text("Организация обучения", exact=True).click()
        await self._page.wait_for_selector(".T627UHU6")
        await self._page.get_by_text("Внешняя оценка", exact=True).click()
        await asyncio.sleep(1)

    def __parce_mcko_files_table(self, table_html: str):
        soup = BeautifulSoup(table_html, "html.parser")
        row_rows = soup.find_all("tr")
        self._mcko_files_list = []
        for row in row_rows:
            row_inn_list = [cell.text for cell in row.find_all("td")]
            if len(row_inn_list) > 0:
                self._mcko_files_list.append(
                    FileEntry(
                        filename=row_inn_list[2].strip("\xa0"),
                        comment=row_inn_list[3],
                    )
                )

    async def _get_mcko_files_list(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        if self._page is None:
            await self._init()
        if len(await self._context.cookies()) < 1:
            await self._school_mos_ru_auth(login=login, password=password)
            await self._okmcko_ru_auth(login=login, password=password)
        await self._page.goto(self._okmcko_mos_ru_url)
        await self._page.locator("#content").get_by_role("link", name="Оценка качества образования").click()
        await self._page.locator("#content").get_by_role("link", name="Скачать файлы (download)").click()
        self.__parce_mcko_files_table(await self._page.locator(".tbl").evaluate("el => el.outerHTML"))

    async def _choose_new_files(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        await self._get_mcko_files_list(login=login, password=password)
        old_files = File.select().order_by(File.id.desc()).limit(10)
        pydantic_old_files = [FileEntry(
            filename=file.filename,
            comment=file.comment
        ) for file in old_files]
        self._new_files = []
        for file in self._mcko_files_list[:30]:
            if file not in pydantic_old_files:
                if ("ДИАГНОСТИКА" in file.comment.upper() and "mcl" in file.filename) or ("diag" in file.filename):
                    self._new_files.append(file)
                    File.create(
                        filename=file.filename,
                        comment=file.comment,
                    )

    async def _download_new_files(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        await self._choose_new_files(login=login, password=password)
        for file in self._new_files:
            async with self._page.expect_download() as download_info:
                await self._page.get_by_text(file.filename).click()
            download = await download_info.value
            await download.save_as(
                f"./{settings.DWNLD_DIR_PATH}/{datetime.datetime.now().date()}/" + download.suggested_filename)

    async def send_new_files(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        await self._download_new_files(login=login, password=password)
        for file in self._new_files:
            document = open(f"./{settings.DWNLD_DIR_PATH}/{datetime.datetime.now().date()}/" + file.filename, "rb")
            url = f"https://api.telegram.org/bot{settings.MCKO_BOT_TOKEN}/sendDocument"
            requests.post(
                url, data={
                    'chat_id': settings.CHAT_ID,
                    'message_thread_id': settings.MESSAGE_THREAD_ID,
                    'caption': file.comment
                },
                files={'document': document}
            )
            await asyncio.sleep(1)

    async def decompress_new_files(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        await self._download_new_files(login=login, password=password)
        for file in self._new_files:
            source_file_path = f"{settings.DWNLD_DIR_PATH}/{datetime.datetime.now().date()}/" + file.filename
            dest_folder = f"{settings.DWNLD_DIR_PATH}/{datetime.datetime.now().date()}/{file.filename}".strip(".zip")
            try:
                with zipfile.ZipFile(source_file_path, 'r') as zip_ref:
                    zip_ref.extractall(dest_folder)
            except FileNotFoundError:
                print(f"Error: The file {source_file_path} was not found.")
            except zipfile.BadZipFile:
                print(f"Error: {source_file_path} is not a valid ZIP file.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
            pdf_files = []
            path = Path(dest_folder)
            for pdf_file in path.glob("**/*.pdf"):
                pdf_files.append(pdf_file.absolute())
            for pdf in pdf_files:
                doc = fitz.open(pdf)
                pdftext = ""
                for page in doc:
                    pdftext += page.get_text()
                pdf_lines = pdftext.split("\n")
                for line in pdf_lines:
                    if line.startswith("ЛИСТ ФИКСАЦИИ РАБОЧИХ МЕСТ"):
                        break
                    if line.startswith("этаж "):
                        print(line)
                    if line.startswith("город "):
                        print(line)
                    if line.startswith("Адрес сайта диагностики:"):
                        print(line)
                    if line.startswith("IP:"):
                        print(line)
                        break
                # print(pdftext)
                print("===========================")
                # await asyncio.sleep(60)

    async def close(self):
        # await asyncio.sleep(50)
        await self._browser.close()
