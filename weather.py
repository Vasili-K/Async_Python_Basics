import asyncio
import time
from aiohttp import ClientSession


async def get_weather(city):
    async with ClientSession() as session:
        url = f'http://api.openweathermap.org/data/2.5/weather'
        params = {'q': city, 'APPID': '2a4ff86f9aaa70041ec8e82db64abf56'}

        async with session.get(url=url, params=params) as response:
            weather_json = await response.json()
            temperature = round(weather_json["main"]["temp"] - 273.15)
            feels_like = round(weather_json["main"]["feels_like"] - 273.15)
            print(f'{city}: {weather_json["weather"][0]["main"]}\n'
                  f'    Temperature: {temperature} C, Feels like: {feels_like} C')


async def main(cities):
    tasks = []
    for city in cities:
        tasks.append(asyncio.create_task(get_weather(city)))

    for task in tasks:
        await task


cities_list = ['Kielce', 'Warsaw', 'Minsk', 'Krakow']

print(time.strftime('%X'))

asyncio.run(main(cities_list))

print(time.strftime('%X'))
