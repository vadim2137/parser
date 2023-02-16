import asyncio
import re

import aiohttp as aiohttp

from loader import app


async def get_btc_course():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', ssl=True) as response:
            course_btc = await response.json()
            return round(float(course_btc['price']), 2)


async def activate_cheque_banker(cheque: str):
    """Activate Cheque BTC Banker"""
    code = cheque.split('BTC_CHANGE_BOT?start=')[1]
    async with app as client:
        await client.send_message('BTC_CHANGE_BOT', f'/start {code}')
        await asyncio.sleep(3)
        messages = [message async for message in client.get_chat_history('@BTC_CHANGE_BOT')]
        message_text = messages[0].text
        if 'Упс' in message_text:
            return 'InvalidCheck'
        elif 'Вы получили' in message_text:
            try:
                response = re.findall(r'(\d+ BTC)|(\d+\.\d+ BTC)', message_text)
                if len(response[0][1]) > 0:
                    btc = float(response[0][1].replace('BTC', ''))
                elif len(response[0][0]) > 0:
                    btc = float(response[0][0].replace('BTC', ''))

                return {'summa': round(await get_btc_course() * btc, 2), 'code': code}
            except (IndexError, ValueError):
                return 'ErrorCheck'
        else:
            return 'ErrorCheck'
