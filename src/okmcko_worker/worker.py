import asyncio
from typing import Optional

from bs4 import BeautifulSoup
from playwright.async_api import Browser, async_playwright, BrowserContext, Page

from settings import settings, FileEntry


class OkMckoWorker:
    _school_mos_ru_url = "https://school.mos.ru"
    _okmcko_mos_ru_url = "https://okmcko.mos.ru/index.php"
    _headless = True
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _page: Optional[Page] = None
    _mcko_files_list: Optional[list[FileEntry]] = None

    def __init__(self):
        self._headless = settings.DEBUG

    async def init(self):
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(headless=self._headless is False)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()

    async def school_mos_ru_auth(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        if self._page is None:
            await self.init()
        await self._page.goto(self._school_mos_ru_url)
        await self._page.wait_for_selector(".style_btn__3lIWs")
        await self._page.locator(".style_btn__3lIWs").click()
        await self._page.wait_for_selector("#login")
        await self._page.fill('input[id="login"]', login)
        await self._page.fill('input[id="password"]', password)
        await self._page.locator("#bind").click()
        await self._page.wait_for_selector(".systems_Wrapper__1h8Fz")

    async def okmcko_ru_auth(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        if self._page is None:
            await self.init()
        if len(await self._context.cookies()) < 1:
            await self.school_mos_ru_auth(login=login, password=password)
        await self._page.get_by_text("Организация обучения", exact=True).click()
        await self._page.wait_for_selector(".T627UHU6")
        await self._page.get_by_text("Внешняя оценка", exact=True).click()
        await asyncio.sleep(1)

    def parce_mcko_files_table(self, table_html: str):
        soup = BeautifulSoup(table_html, "html.parser")
        row_rows = soup.find_all("tr")
        self._mcko_files_list = []
        for row in row_rows:
            row_inn_list = [cell.text for cell in row.find_all("td")]
            if len(row_inn_list) > 0:
                self._mcko_files_list.append(
                    FileEntry(
                        date=row_inn_list[1],
                        filename=row_inn_list[2].strip("\xa0"),
                        comment=row_inn_list[3],
                    )
                )

    async def get_mcko_files_list(self, login: str = settings.LOGIN, password: str = settings.PASSWORD):
        if self._page is None:
            await self.init()
        if len(await self._context.cookies()) < 1:
            await self.school_mos_ru_auth(login=login, password=password)
            await self.okmcko_ru_auth(login=login, password=password)
        await self._page.goto(self._okmcko_mos_ru_url)
        await self._page.locator("#content").get_by_role("link", name="Оценка качества образования").click()
        await self._page.locator("#content").get_by_role("link", name="Скачать файлы (download)").click()
        self.parce_mcko_files_table(await self._page.locator(".tbl").evaluate("el => el.outerHTML"))

    async def close(self):
        await asyncio.sleep(50)
        await self._browser.close()
