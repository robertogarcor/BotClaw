from bot.servers.base import BaseServer
from bot.servers.opencode import OpenCodeServer


class ServerFactory:
    @staticmethod
    def create(server_type: str, **kwargs) -> BaseServer:
        servers = {
            "opencode": OpenCodeServer,
        }
        server_class = servers.get(server_type.lower())
        if not server_class:
            raise ValueError(f"Unknown server type: {server_type}")
        return server_class(**kwargs)

    @staticmethod
    def create_opencode(url: str, password: str = "") -> OpenCodeServer:
        return OpenCodeServer(url=url, password=password)