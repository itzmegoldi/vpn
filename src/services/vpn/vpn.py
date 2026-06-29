import base64
import ipaddress

from fastapi import HTTPException

from src.builder.clients import Clients
from src.config.config import Config
from src.models.vpn import VPNClient, VPNServer
from src.repository.vpn import VPNRepositoryInterface


class VPNService:
    def __init__(self, clients: Clients, config: Config, repo: VPNRepositoryInterface):
        self.clients = clients
        self.config = config
        self.repo = repo

    def setup_server(self, payload) -> VPNServer:
        interface = payload.wireguard_interface
        port = payload.wireguard_port
        subnet = self._parse_network(payload.vpn_subnet)
        server_vpn_ip = self._first_host(subnet)

        ssh = self.clients.new_ssh_client()
        try:
            ssh.connect(
                hostname=payload.public_ip,
                username=payload.ssh_username,
                key_filename=payload.ssh_key_path,
            )
            self._install_wireguard(ssh)
            server_private_key, server_public_key = self._generate_key_pair(ssh)
            config_text = self._server_config(
                private_key=server_private_key,
                address=f"{server_vpn_ip}/{subnet.prefixlen}",
                port=port,
            )
            self._write_remote_file(
                ssh, f"/etc/wireguard/{interface}.conf", config_text
            )
            ssh.execute_command(
                "sudo sysctl -w net.ipv4.ip_forward=1 && "
                "echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-wireguard-forward.conf"
            )
            ssh.execute_command(
                f"sudo systemctl enable wg-quick@{interface} && "
                f"sudo systemctl restart wg-quick@{interface}"
            )
        finally:
            ssh.close()

        return self.repo.create_server(
            {
                "name": payload.name,
                "public_ip": payload.public_ip,
                "ssh_username": payload.ssh_username,
                "ssh_key_path": payload.ssh_key_path,
                "wireguard_interface": interface,
                "wireguard_port": port,
                "vpn_subnet": payload.vpn_subnet,
                "server_vpn_ip": server_vpn_ip,
                "server_private_key": server_private_key,
                "server_public_key": server_public_key,
                "config_text": config_text,
                "is_active": True,
            }
        )

    def list_servers(self) -> list[VPNServer]:
        return self.repo.list_servers()

    def create_client(self, payload) -> VPNClient:
        server = self._get_server_or_404(payload.server_id)
        client_ip = self._allocate_client_ip(server)

        ssh = self.clients.new_ssh_client()
        try:
            ssh.connect(
                hostname=server.public_ip,
                username=server.ssh_username,
                key_filename=server.ssh_key_path,
            )
            private_key, public_key = self._generate_key_pair(ssh)
            config_text = self._client_config(
                private_key=private_key,
                client_ip=client_ip,
                server=server,
            )
            self._add_peer(ssh, server.wireguard_interface, public_key, client_ip)
        finally:
            ssh.close()

        return self.repo.create_client(
            {
                "server_id": server.id,
                "username": payload.username,
                "client_private_key": private_key,
                "client_public_key": public_key,
                "client_ip": client_ip,
                "config_text": config_text,
                "is_active": True,
            }
        )

    def list_clients(self, server_id: int | None = None) -> list[VPNClient]:
        return self.repo.list_clients(server_id=server_id)

    def connect_client(self, client_id: int) -> VPNClient:
        client = self._get_client_or_404(client_id)
        server = self._get_server_or_404(client.server_id)
        ssh = self.clients.new_ssh_client()
        try:
            ssh.connect(
                hostname=server.public_ip,
                username=server.ssh_username,
                key_filename=server.ssh_key_path,
            )
            self._add_peer(
                ssh,
                server.wireguard_interface,
                client.client_public_key,
                client.client_ip,
            )
        finally:
            ssh.close()
        return self.repo.update_client(client, {"is_active": True})

    def disconnect_client(self, client_id: int) -> VPNClient:
        client = self._get_client_or_404(client_id)
        server = self._get_server_or_404(client.server_id)
        ssh = self.clients.new_ssh_client()
        try:
            ssh.connect(
                hostname=server.public_ip,
                username=server.ssh_username,
                key_filename=server.ssh_key_path,
            )
            ssh.execute_command(
                f"sudo wg set {server.wireguard_interface} "
                f"peer {client.client_public_key} remove"
            )
            ssh.execute_command(f"sudo wg-quick save {server.wireguard_interface}")
        finally:
            ssh.close()
        return self.repo.update_client(client, {"is_active": False})

    def _get_server_or_404(self, server_id: int) -> VPNServer:
        server = self.repo.get_server(server_id)
        if server is None:
            raise HTTPException(status_code=404, detail="VPN server not found")
        return server

    def _get_client_or_404(self, client_id: int) -> VPNClient:
        client = self.repo.get_client(client_id)
        if client is None:
            raise HTTPException(status_code=404, detail="VPN client not found")
        return client

    def _install_wireguard(self, ssh):
        ssh.execute_command(
            "if command -v apt-get >/dev/null 2>&1; then "
            "sudo apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y wireguard; "
            "elif command -v dnf >/dev/null 2>&1; then sudo dnf install -y wireguard-tools; "
            "elif command -v yum >/dev/null 2>&1; then sudo yum install -y wireguard-tools; "
            "else echo 'Unsupported Linux distribution' >&2; exit 1; fi"
        )

    def _generate_key_pair(self, ssh) -> tuple[str, str]:
        private_key = ssh.execute_command("wg genkey").strip()
        public_key = ssh.execute_command(
            f"printf '%s' '{private_key}' | wg pubkey"
        ).strip()
        return private_key, public_key

    def _server_config(self, private_key: str, address: str, port: int) -> str:
        return (
            "[Interface]\n"
            f"Address = {address}\n"
            f"ListenPort = {port}\n"
            f"PrivateKey = {private_key}\n"
            "SaveConfig = true\n"
        )

    def _client_config(
        self, private_key: str, client_ip: str, server: VPNServer
    ) -> str:
        return (
            "[Interface]\n"
            f"PrivateKey = {private_key}\n"
            f"Address = {client_ip}/32\n"
            "DNS = 1.1.1.1\n\n"
            "[Peer]\n"
            f"PublicKey = {server.server_public_key}\n"
            f"Endpoint = {server.public_ip}:{server.wireguard_port}\n"
            "AllowedIPs = 0.0.0.0/0, ::/0\n"
            "PersistentKeepalive = 25\n"
        )

    def _write_remote_file(self, ssh, path: str, content: str):
        encoded = base64.b64encode(content.encode()).decode()
        ssh.execute_command(
            f"echo '{encoded}' | base64 -d | sudo tee {path} >/dev/null && "
            f"sudo chmod 600 {path}"
        )

    def _add_peer(self, ssh, interface: str, public_key: str, client_ip: str):
        ssh.execute_command(
            f"sudo wg set {interface} peer {public_key} allowed-ips {client_ip}/32"
        )
        ssh.execute_command(f"sudo wg-quick save {interface}")

    def _allocate_client_ip(self, server: VPNServer) -> str:
        network = self._parse_network(server.vpn_subnet)
        reserved = {server.server_vpn_ip}
        reserved.update(
            client.client_ip for client in self.repo.list_clients(server_id=server.id)
        )
        for ip in network.hosts():
            address = str(ip)
            if address not in reserved:
                return address
        raise HTTPException(status_code=409, detail="VPN subnet has no free client IPs")

    def _parse_network(self, value: str):
        try:
            return ipaddress.ip_network(value)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid VPN subnet") from exc

    def _first_host(self, network) -> str:
        try:
            return str(next(network.hosts()))
        except StopIteration as exc:
            raise HTTPException(
                status_code=400, detail="VPN subnet must include usable host addresses"
            ) from exc
