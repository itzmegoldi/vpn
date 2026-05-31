from fastapi import APIRouter

from src.api.vpn import router as vpn_router

router = APIRouter()
router.include_router(vpn_router, prefix="/vpn", tags=["VPN"])
