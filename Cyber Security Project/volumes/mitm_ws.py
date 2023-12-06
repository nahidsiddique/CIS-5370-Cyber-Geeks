import asyncio
import websockets

async def server(websocket, path):
    while True:
        message = await websocket.recv()
        print(f"Received message: {message}")

async def main():
    server_task = websockets.serve(server, "localhost", 8765)

    await asyncio.gather(server_task)

if __name__ == "__main__":
    asyncio.run(main())

