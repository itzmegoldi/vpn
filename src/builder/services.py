from src.services.vpn import VPNService, VPNServiceInterface


class Services:
    def with_vpn_service(self, clients, config, repo):
        self.vpn_service: VPNServiceInterface = VPNService(
            clients=clients, config=config, repo=repo
        )
        return self
