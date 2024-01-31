import asyncio
import json
from datetime import datetime

import aiosqlite
from aiohttp import ClientSession, web


async def create_db_table():
    async with aiosqlite.connect('weather_data.db') as db:
        await db.execute('CREATE TABLE IF NOT EXISTS requests '
                         '(date text, city text, wether text, language text, temperature integer, feels_like integer)')
        await db.commit()


async def save_to_db(city, weather, language, temperature, feels_like):
    async with aiosqlite.connect('weather_data.db') as db:
        await db.execute('INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?)',
                         (datetime.now(), city, weather, language, temperature, feels_like))
        await db.commit()


async def get_weather(city):
    async with ClientSession() as session:
        url = f'http://api.openweathermap.org/data/2.5/weather'
        params = {'q': city, 'APPID': '2a4ff86f9aaa70041ec8e82db64abf56'}

        async with session.get(url=url, params=params) as response:
            weather_json = await response.json()
            try:
                weather = weather_json["weather"][0]["main"]
                temperature = round(weather_json["main"]["temp"] - 273.15)
                feels_like = round(weather_json["main"]["feels_like"] - 273.15)
                result = {
                    'weather': weather,
                    'temperature': temperature,
                    'feels_like': feels_like
                }
                return result
            except KeyError:
                return "No data"


async def get_translation(text, source, target):
    async with ClientSession() as session:
        url = 'https://libretranslate.de/translate'

        data = {'q': text, 'source': source, 'target': target, 'format': 'text'}

        async with session.post(url, json=data) as response:
            print(response)
            translate_json = await response.json()

            try:
                return translate_json['translatedText']
            except KeyError:
                return text


async def handle(request):
    city_translate = request.rel_url.query['city']
    language = request.rel_url.query['lang']

    city_en = await get_translation(city_translate, language, 'en')

    weather = await get_weather(city_en)
    weather_en = weather['weather']
    weather_translate = await get_translation(weather_en, 'en', language)

    result = {'city': city_translate, 'weather': weather_translate}
    temperature = weather['temperature']
    feels_like = weather['feels_like']

    await save_to_db(city_translate, weather_translate, language, temperature, feels_like)

    return web.Response(text=json.dumps(result, ensure_ascii=False))


async def main():
    await create_db_table()
    app = web.Application()
    app.add_routes([web.get('/weather', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.run(main())
