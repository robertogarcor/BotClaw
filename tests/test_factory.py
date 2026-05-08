import pytest
from unittest.mock import patch, MagicMock


class TestServerFactory:
    def test_factory_creates_opencode_server(self):
        from bot.servers.factory import ServerFactory
        server = ServerFactory.create("opencode", url="http://localhost:4096")
        assert server is not None
        assert server.url == "http://localhost:4096"

    def test_factory_create_opencode_method(self):
        from bot.servers.factory import ServerFactory
        server = ServerFactory.create_opencode(url="http://localhost:4097", password="secret")
        assert server is not None
        assert server.url == "http://localhost:4097"
        assert server.password == "secret"

    def test_factory_raises_on_unknown_type(self):
        from bot.servers.factory import ServerFactory
        with pytest.raises(ValueError, match="Unknown server type"):
            ServerFactory.create("unknown_server", url="http://localhost:4096")