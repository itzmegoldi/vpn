from src.repository.vpn import VPNRepository, VPNRepositoryInterface


class Repositories:

    def with_vpn_repository(self, db_handler) -> "Repositories":
        self.vpn_repository: VPNRepositoryInterface = VPNRepository(
            db_handler=db_handler
        )
        return self
