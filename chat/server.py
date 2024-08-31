import socket

HOST = '0.0.0.0'
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"서버가 {PORT} 포트에서 대기 중 ...")

client_socket, client_addr = server_socket.accpet()
print(f"클라이언트 {client_addr} 연결됨!")

while True:
    try:
        data = client_socket.recv(1024)
        if not data:
            break