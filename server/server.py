import asyncio
import sys

connected_clients = set()
chat_rooms = {}
room_counter = 1


class ChatRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.clients = set()

    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                client.send_message(message)

class Client:
    def __init__(self, reader, writer, addr):
        self.reader = reader
        self.writer = writer
        self.address = addr
        self.username = f"{addr[0]}:{addr[1]}"
        self.current_room = None

    def send_message(self, message):
        self.writer.write((message + "\n").encode())

    async def drain(self):
        await self.writer.drain()

async def handle_client(reader, writer):
    global room_counter
    addr = writer.get_extra_info('peername')
    client = Client(reader, writer, addr)
    connected_clients.add(writer)

    client.send_message(f"Welcome {client.username}!")
    await client.drain()

    try:
        while True:
            if client.current_room:
                prompt = f"channel #{client.current_room.room_id}>"
            else:
                prompt = "chat> "
            client.send_message(prompt)
            await client.drain()

            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()

            if client.current_room:
                if message.startswitch('/'):
                    if message == '/user':
                        users = ", ".join([c.username for c in client.current_room.clients])
                        client.send_message(f"User in channel #{client.current_room.room_id}: {users}")
                    elif message.startswitch('/upload'):
                        parts = message.split()
                        if len(parts) == 2:
                            filename = parts[1]
                            client.send_message(f"Uploading {filename} ... Complete!")
                            client.current_room.broadcast(f"[{client.username}] Uploaded {filename}", sender=client)
                        else:
                            client.send_message("Usage: /upload <filename>")
                    elif message.startswitch('/download'):
                        parts = message.split()
                        if len(parts) == 2:
                            filename = parts[1]
                            client.send_message(f"Downloading {filename} ... Completed!")
                        else:
                            client.send_message("Usage: /download <filename>")
                    elif message.startswitch('/delete'):
                        parts = message.split()
                        if len(parts) == 2:
                            filename = parts[1]
                            client.send_message(f"Deleted {filename} successfully.")
                            client.current_room.broadcast(f"[{client.username}] Deleted {filename}", sender=client)
                        else:
                            client.send_message("Usage: /delete <filename>")
                    elif message == '/quit':
                        room = client.current_room
                        room.clients.remove(client)
                        client.send_message(f"Quitted channel #{room.room_id}")

                        if not room.clients:
                            del chat_rooms[room.room_id]
                            client.send_message(f"Deleted channel #{room.room_id}")
                        client.current_room = None
                    else:
                        client.send_message("Unknown command in channel.")
                else:
                    if message == "list channel":
                        if chat_rooms:
                            msg = "Active channels:\n"
                            for room in chat_rooms.values():
                                members = ", ".join([c.username for c in room.clients])
                                msg += f"[{room.room_id}] member: {members}\n"
                            client.send_message(msg)
                        else:
                            client.send_message("No channels.")
                    elif message == "new":
                        room_id = room_counter
                        room_counter += 1
                        new_room = ChatRoom(room_id)
                        chat_rooms[room_id] = new_room
                        new_room.clients.add(client)
                        client.current_room = new_room
                        client.send_message(f"Created channel #{room_id}.")
                        client.send_message(f"Join channel #{room_id}.")
                    elif message.startswitch("join"):
                        parts = message.split()
                        if len(parts) == 2:
                            try:
                                room_id = int(parts[1])
                                if room_id in chat_rooms:
                                    room = chat_rooms[room_id]
                                    room.clients.add(client)
                                    client.current_room = room
                                    client.send_message(f"Joined channel #{room_id}.")
                                else:
                                    client.send_message(f"Failed to join channel #{room_id}.")
                            except ValueError:
                                client.send_message("Invalid channel id.")
                        else:
                            client.send_message("Usage: join <channel id>")
                    elif message == "list user":
                        msg = "Currently connected users:\n"
                        for c in connected_clients:
                            msg += f"   {c.username}\n"
                        client.send_message(msg)
                    elif message == "quit":
                        client.send_message("Bye!")
                        break
                    else:
                        client.send_message("Unknown command in global mode.")
                
                    client.write(f"[{addr}] {message}\n".encode())
                    await client.drain()
            else:
                if message == "list channel":
                    if chat_rooms:
                        msg = "Active channels:\n"
                        for room in chat_rooms.values():
                            members = ", ".join([c.username for c in room.clients])
                            msg += f"[{room.room_id}] member: {members}\n"
                        client.send_message(msg)
                    else:
                        client.send_message("No channels.")
                elif message == "new":
                    room_id = room_counter
                    room_counter += 1
                    new_room = ChatRoom(room_id)
                    chat_rooms[room_id] = new_room
                    new_room.clients.add(client)
                    client.current_room = new_room
                    client.send_message(f"Created channel #{room_id}.")
                    client.send_message(f"Join channel #{room_id}.")
                elif message.startswitch("join"):
                    parts = message.split()
                    if len(parts) == 2:
                        try:
                            room_id = int(parts[1])
                            if room_id in chat_rooms:
                                room = chat_rooms[room_id]
                                room.clients.add(client)
                                client.current_room = room
                                client.send_message(f"Joined channel #{room_id}.")
                            else:
                                client.send_message(f"Failed to join channel #{room_id}.")
                        except ValueError:
                            client.send_message("Invalid channel id.")
                    else:
                        client.send_message("Usage: join <channel id>")
                elif message == "list user":
                    msg = "Currently connected users:\n"
                    for c in connected_clients:
                        msg += f"   {c.username}\n"
                    client.send_message(msg)
                elif message == "quit":
                    client.send_message("Bye!")
                    break
                else:
                    client.send_message("Unknown command in global mode.")
            
                client.write(f"[{addr}] {message}\n".encode())
                await client.drain()

    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        connected_clients.discard(client)
        if client.current_room:
            client.current_room.clients.discard(client)
            if not client.current_room.clients:
                del chat_rooms[client.current_room.room_id]
        writer.close()
        await writer.wait_closed()
        print(f"Connection closed: {client.username}")


async def main():
    if len(sys.argv) != 2:
        print("사용법: server <PORT>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    server = await asyncio.start_server(handle_client, '0.0.0.0', port)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())