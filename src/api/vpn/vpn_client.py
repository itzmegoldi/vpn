from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.builder import get_service
from src.services.vpn import VPNServiceInterface

router = APIRouter(prefix="/client", tags=["VPN Client"])


def get_vpn_server():
    return get_service().vpn_service


VpnServiceDep = Annotated[VPNServiceInterface, Depends(get_vpn_server)]


class VPNClientCreateRequest(BaseModel):
    server_id: int
    username: str


class VPNClientResponse(BaseModel):
    id: int
    server_id: int
    username: str
    client_public_key: str
    client_ip: str
    config_text: str
    is_active: bool

    model_config = {"from_attributes": True}


@router.post("/setup", response_model=VPNClientResponse)
def setup_client(payload: VPNClientCreateRequest, service: VpnServiceDep):
    return service.create_client(payload)


@router.get("", response_model=list[VPNClientResponse])
def list_clients(service: VpnServiceDep, server_id: int | None = None):
    return service.list_clients(server_id=server_id)


@router.post("/{client_id}/connect", response_model=VPNClientResponse)
def connect_client(client_id: int, service: VpnServiceDep):
    return service.connect_client(client_id)


@router.post("/{client_id}/disconnect", response_model=VPNClientResponse)
def disconnect_client(client_id: int, service: VpnServiceDep):
    return service.disconnect_client(client_id)
