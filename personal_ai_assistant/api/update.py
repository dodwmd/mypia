from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from personal_ai_assistant.updater.update_manager import UpdateManager
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


def get_update_manager():
    return UpdateManager()


@router.post("/check")
async def check_for_updates(
    token: str = Depends(oauth2_scheme),
    update_manager: UpdateManager = Depends(get_update_manager)
):
    try:
        updates_available = await update_manager.check_for_updates()
        if updates_available:
            logger.info("Updates are available")
            return {"message": "Updates are available", "updates_available": True}
        logger.info("No updates available")
        return {"message": "No updates available", "updates_available": False}
    except Exception as e:
        logger.error(f"Error checking for updates: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking for updates")


@router.post("/apply")
async def apply_updates(
    token: str = Depends(oauth2_scheme),
    update_manager: UpdateManager = Depends(get_update_manager)
):
    try:
        updates_available = await update_manager.check_for_updates()
        if updates_available:
            await update_manager.update_all()
            logger.info("Successfully applied updates")
            return {"message": "Updates applied successfully"}
        logger.info("No updates available to apply")
        return {"message": "No updates available to apply"}
    except Exception as e:
        logger.error(f"Error applying updates: {str(e)}")
        raise HTTPException(status_code=500, detail="Error applying updates")


@router.get("/status")
async def get_update_status(
    token: str = Depends(oauth2_scheme),
    update_manager: UpdateManager = Depends(get_update_manager)
):
    try:
        status = await update_manager.get_update_status()
        logger.info(f"Successfully retrieved update status: {status}")
        return {"status": status}
    except Exception as e:
        logger.error(f"Error getting update status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting update status")
