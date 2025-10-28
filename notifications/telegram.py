import asyncio
from typing import Optional

from aiohttp import ClientSession


async def send_telegram_message(
        bot_token: str,
        text: str,
        chat_id: str,
        message_thread_id: Optional[str] = None
) -> bool:
    request_data = {
        'chat_id': chat_id,
        'text': text,
    }
    if message_thread_id is not None:
        request_data['message_thread_id'] = message_thread_id
    async with ClientSession() as session:
        response = await session.post(
            url='https://api.telegram.org/bot' + bot_token + '/sendMessage',
            data=request_data,
            ssl=False
        )
        await asyncio.sleep(1)
    return response.status == 200
