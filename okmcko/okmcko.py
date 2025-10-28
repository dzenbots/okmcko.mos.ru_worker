import asyncio
import datetime
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from playwright.async_api import Browser, async_playwright, BrowserContext, Page

from config import config
from database import File


class OkMckoWorker:
    _school_mos_ru_url = "https://school.mos.ru"
    _school_mos_ru_educationmanagement_url = "https://school.mos.ru/educationmanagement/routing"
    _okmcko_mos_ru_url = "https://okmcko.mos.ru/index.php"
    _headless = True
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _page: Optional[Page] = None

    def __init__(self, debug: bool = config.misc.debug):
        self._headless = debug

    async def init(self, login: str = config.mos_ru.login,
                   password: str = config.mos_ru.password.get_secret_value()):
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(headless=self._headless is False)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        await self._page.goto(self._school_mos_ru_url)
        await self._page.wait_for_selector(".style_btn__3lIWs")
        await self._page.locator(".style_btn__3lIWs").click()
        await self._page.wait_for_selector("#login")
        await self._page.fill('input[id="login"]', login)
        await self._page.fill('input[id="password"]', password)
        await self._page.locator("#bind").click()
        await self._page.wait_for_selector(".systems_Wrapper__1h8Fz")
        await self._page.goto(self._school_mos_ru_educationmanagement_url)
        await self._page.wait_for_selector(".T627UHU6")
        await self._page.get_by_text("Внешняя оценка", exact=True).click()
        await asyncio.sleep(1)

    async def get_mcko_files_list(self) -> list:
        await self._page.goto(self._okmcko_mos_ru_url)
        await self._page.locator("#content").get_by_role("link", name="Оценка качества образования").click()
        await self._page.locator("#content").get_by_role("link", name="Скачать файлы (download)").click()
        soup = BeautifulSoup(await self._page.locator(".tbl").evaluate("el => el.outerHTML"), "html.parser")
        row_rows = soup.find_all("tr")
        mcko_files_list = []
        for row in row_rows:
            row_inn_list = [cell.text for cell in row.find_all("td")]
            if len(row_inn_list) > 0:
                mcko_files_list.append(
                    {
                        "filename": row_inn_list[2].strip("\xa0"),
                        "comment": row_inn_list[3],
                    }
                )
        await asyncio.sleep(1)
        return mcko_files_list

    async def choose_new_files(self, mcko_files_list: list):
        old_files = [
            {
                "filename": file.filename,
                "comment": file.comment,
            } for file in File.select()
        ]
        new_files = []
        for file in mcko_files_list[:10]:
            if file not in old_files:
                new_files.append(file)
                File.create(
                    filename=file.get("filename"),
                    comment=file.get("comment"),
                )
        await asyncio.sleep(1)
        return new_files

    async def download_new_files(self, files_to_download: list, download_path: Path):
        for file in files_to_download:
            async with self._page.expect_download() as download_info:
                await self._page.get_by_text(file.get("filename")).click()
            download = await download_info.value
            file["download_path"] = download_path / str(datetime.datetime.now().date()) / download.suggested_filename
            await download.save_as(file.get("download_path"))
            await asyncio.sleep(1)

    async def close(self):
        await self._browser.close()
