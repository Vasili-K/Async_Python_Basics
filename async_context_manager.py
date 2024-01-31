import asyncio
import time


# imitation of async connection
async def get_conn(host, port):
    class Conn:
        async def put_data(self):
            print('Sending data...')
            await asyncio.sleep(2)
            print('Data sent.')

        async def get_data(self):
            print('Getting data...')
            await asyncio.sleep(2)
            print('Data received.')

        async def close(self):
            print('Closing connection...')
            await asyncio.sleep(2)
            print('Connection closed.')

    print('Connecting...')
    await asyncio.sleep(2)
    print('Connection set up.')
    return Conn()


class Connection:
    # will be executed in with first line
    def __init__(self, host, port):
        self.host = host
        self.port = port

    # enter in with
    async def __aenter__(self):
        self.conn = await get_conn(self.host, self.port)
        return self.conn

    # exit from with
    async def __aexit__(self, exc_type, exc, tb):
        await self.conn.close()


async def main():
    async with Connection('localhost', 9001) as conn:
        send_task = asyncio.create_task(conn.put_data())
        receive_task = asyncio.create_task(conn.get_data())

        # concurrent operations
        await send_task
        await receive_task


print(time.strftime('%X'))

asyncio.run(main())

print(time.strftime('%X'))
