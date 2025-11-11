import asyncio
from pathlib import Path

from config import config
from database import initialize_db, close_db
from notifications import send_email_message, send_telegram_message
from okmcko.okmcko import OkMckoWorker
from unziper import Unziper
from parcers import PdfParser


async def main():
    while True:
        try:
            initialize_db()
            worker = OkMckoWorker()
            try:
                await worker.init(
                    login=config.mos_ru.login,
                    password=config.mos_ru.password.get_secret_value(),
                )
                while True:
                    mcko_files_list = await worker.get_mcko_files_list()
                    new_files = await worker.choose_new_files(mcko_files_list)
                    await worker.download_new_files(
                        files_to_download=new_files, download_path=Path(config.storage.folder_path)
                    )
                    for file in new_files:
                        if config.notifications.email:
                            await send_email_message(
                                subject="Материалы из МЦКО",
                                message_text=f"<strong>Получены новые материалы из МЦКО.<br>{file.get("comment")}</strong>",
                                file_path=Path(file.get("download_path")),
                                sender_email=config.email.smtp_login,
                                sender_password=config.email.smtp_password.get_secret_value(),
                                receiver_emails=config.email.target_emails,
                                smtp_server_hostname=config.email.smtp_server,
                                smtp_server_port=config.email.smtp_port
                            )
                        if "ДИАГНОСТИКА" in file.get("comment").upper():
                            if "КОДЫ УЧАСТНИКОВ" in file.get("comment").upper():
                                archive_path = Path(file.get("download_path"))
                                extract_path = Path(str(file.get("download_path")).strip(".zip"))
                                Unziper().unzip_file(path=archive_path, target_path=extract_path)
                                if config.notifications.telegram:
                                    for pdf_file in extract_path.glob("**/*.pdf"):
                                        link_struct = PdfParser(pdf_file).get_diag_link()
                                        if len(link_struct.keys()) > 0:
                                            await send_telegram_message(
                                                bot_token=config.telegram.bot_token.get_secret_value(),
                                                chat_id=config.telegram.chat_id,
                                                message_thread_id=config.telegram.thread_id,
                                                text="\n".join(
                                                    [
                                                        link_struct.get("address", "-"),
                                                        link_struct.get("kab_num", "-"),
                                                        link_struct.get("link", "-"),
                                                        link_struct.get("ip", "-"),
                                                    ]
                                                )
                                            )
                                            await asyncio.sleep(1)
                    await asyncio.sleep(1)
            except Exception as e:
                print(e)
                await worker.close()
        except Exception as e:
            print(e)
            close_db()


if __name__ == '__main__':
    asyncio.run(main())
