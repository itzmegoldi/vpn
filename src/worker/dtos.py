from pydantic import BaseModel

from src.api.vpn.vpn_client import VPNClientCreateRequest
from src.api.vpn.vpn_server import VPNServerSetupRequest


class VPNClientConnectionRequest(BaseModel):
    client_id: int


class VPNClientListRequest(BaseModel):
    server_id: int | None = None


class EmptyRequest(BaseModel):
    pass


DTO_REQUEST_MAPPER: dict[str, type[BaseModel]] = {
    "setup_server": VPNServerSetupRequest,
    "list_servers": EmptyRequest,
    "create_client": VPNClientCreateRequest,
    "list_clients": VPNClientListRequest,
    "connect_client": VPNClientConnectionRequest,
    "disconnect_client": VPNClientConnectionRequest,
}
