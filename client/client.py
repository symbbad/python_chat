import asyncio
import sys

async def read_stdin_and_send(writer):
    while True:
        line = await asyncio.to_thread(input, "")
        writer.write((line + "\n").encode())
        await writer.drain()
        if line.strip() == "quit":
            break

async def receive_messages(reader):
    while True:
        data = await reader.readline()
        if not data:
            break
        print(data.decode().rstrip())

async def main():
    if len(sys.argv) != 3:
        print("사용법: client <IP주소> <PORT>")
        return

    server_ip = sys.argv[1]
    port = int(sys.argv[2])

    reader, writer = await asyncio.open_connection(server_ip, port)

    task_recv = asyncio.create_task(receive_messages(reader))
    task_send = asyncio.create_task(read_stdin_and_send(writer))
    await asyncio.wait(
        [task_recv, task_send],
        return_when=asyncio.FIRST_COMPLETED
    )
    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())