from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field

from src.builder import get_service
from src.services.vpn import VPNServiceInterface

router = APIRouter(prefix="/server", tags=["VPN Server"])


def get_vpn_service():
    return get_service().vpn_service


VpnServiceDep = Annotated[VPNServiceInterface, Depends(get_vpn_service)]


class VPNServerSetupRequest(BaseModel):
    name: str
    public_ip: str
    ssh_username: str
    ssh_key: str
    wireguard_interface: str = "wg0"
    wireguard_port: int = Field(default=51820, ge=1, le=65535)
    vpn_subnet: str = "10.8.0.0/24"


class VPNServerResponse(BaseModel):
    id: int
    name: str
    public_ip: str
    ssh_username: str
    ssh_key_path: str
    wireguard_interface: str
    wireguard_port: int
    vpn_subnet: str
    server_vpn_ip: str
    server_public_key: str
    config_text: str
    is_active: bool

    model_config = {"from_attributes": True}


@router.post("/setup", response_model=VPNServerResponse, status_code=201)
def setup_server(payload: VPNServerSetupRequest, service: VpnServiceDep):
    try:
        return service.setup_server(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[VPNServerResponse], status_code=200)
def list_servers(service: VpnServiceDep):
    try:
        return service.list_servers()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
