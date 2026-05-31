from fastapi import APIRouter

from src.api.vpn.vpn_client import router as vpn_client_router
from src.api.vpn.vpn_server import router as vpn_server_router

router = APIRouter()
router.include_router(vpn_client_router)
router.include_router(vpn_server_router)
