from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Text

from src.models.base import BaseModel


class VPNServer(BaseModel):
    __tablename__ = "vpn_servers"

    name = Column(String, nullable=False)
    public_ip = Column(String, nullable=False)
    ssh_username = Column(String, nullable=False)
    ssh_key_path = Column(String, nullable=False)
    wireguard_interface = Column(String, default="wg0")
    wireguard_port = Column(Integer, default=51820)
    vpn_subnet = Column(String, default="10.8.0.0/24")
    server_vpn_ip = Column(String, default="10.8.0.1")
    server_private_key = Column(Text, nullable=False)
    server_public_key = Column(Text, nullable=False)
    config_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)


class VPNClient(BaseModel):
    __tablename__ = "vpn_clients"

    server_id = Column(BigInteger, ForeignKey("vpn_servers.id"), nullable=False)
    username = Column(String, nullable=False)
    client_private_key = Column(Text, nullable=False)
    client_public_key = Column(Text, nullable=False)
    client_ip = Column(String, nullable=False)
    config_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
