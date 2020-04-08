import asyncio
from asyncio import transports
from typing import Optional

class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        decoded = data.decode()

        if self.login is not None:
            self.send_message(decoded)
            self.server.history.append(decoded)
        else:
            if decoded.startswith("login:"):
                    login = decoded.replace("login:", "").replace("\r\n", "")
                    for user in self.server.clients:
                        if user.login == login:
                            self.transport.write(f"Логин {login} занят, попробуйте другой\n".encode())
                            return
                        #else:
                    #self.transport.write(f"Привет, {login}!\n".encode())
                    self.login = login
                    self.server.send_history(self)


            else:
                self.transport.write("Неправильный логин\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Клиент вышел")

    def send_message(self, content: str):
        message = f"{self.login}: {content}"

        for user in self.server.clients:
            user.transport.write(message.encode())


class Server:
    clients: list
    history: list
    def __init__(self):
        self.clients = []
        self.history = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )
        print("Сервер запущен...")
        await coroutine.serve_forever()

    def send_history(self, login: ServerProtocol):
        login.transport.write(f"Привет, {login}!\n".encode())

        last_messages = self.history[-10:]

        for msg in last_messages:
            login.transport.write(msg.encode())


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
