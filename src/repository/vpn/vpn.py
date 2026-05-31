from datetime import datetime

from src.models.vpn import VPNClient, VPNServer


class VPNRepository:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def _now(self) -> int:
        return int(datetime.utcnow().timestamp())

    def create_server(self, data: dict) -> VPNServer:
        now = self._now()
        server = VPNServer(**data, created_at=now, updated_at=now)
        with self.db_handler.get_session() as session:
            session.add(server)
            session.commit()
            session.refresh(server)
            return server

    def get_server(self, server_id: int) -> VPNServer | None:
        with self.db_handler.get_session() as session:
            return session.get(VPNServer, server_id)

    def list_servers(self) -> list[VPNServer]:
        with self.db_handler.get_session() as session:
            return session.query(VPNServer).order_by(VPNServer.id.desc()).all()

    def create_client(self, data: dict) -> VPNClient:
        now = self._now()
        client = VPNClient(**data, created_at=now, updated_at=now)
        with self.db_handler.get_session() as session:
            session.add(client)
            session.commit()
            session.refresh(client)
            return client

    def get_client(self, client_id: int) -> VPNClient | None:
        with self.db_handler.get_session() as session:
            return session.get(VPNClient, client_id)

    def list_clients(self, server_id: int | None = None) -> list[VPNClient]:
        with self.db_handler.get_session() as session:
            query = session.query(VPNClient)
            if server_id is not None:
                query = query.filter(VPNClient.server_id == server_id)
            return query.order_by(VPNClient.id.desc()).all()

    def update_client(self, client: VPNClient, data: dict) -> VPNClient:
        with self.db_handler.get_session() as session:
            db_client = session.get(VPNClient, client.id)
            for key, value in data.items():
                setattr(db_client, key, value)
            db_client.updated_at = self._now()
            session.commit()
            session.refresh(db_client)
            return db_client
