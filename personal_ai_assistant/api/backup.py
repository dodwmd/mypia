from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from personal_ai_assistant.utils.backup_manager import BackupManager
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

def get_backup_manager():
    return BackupManager()

@router.post("/create")
async def create_backup(
    token: str = Depends(oauth2_scheme),
    backup_manager: BackupManager = Depends(get_backup_manager)
):
    try:
        backup_path = await backup_manager.create_backup()
        logger.info(f"Successfully created backup at: {backup_path}")
        return {"message": "Backup created successfully", "backup_path": backup_path}
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating backup")

@router.post("/restore")
async def restore_backup(
    backup_file: str,
    token: str = Depends(oauth2_scheme),
    backup_manager: BackupManager = Depends(get_backup_manager)
):
    try:
        await backup_manager.restore_backup(backup_file)
        logger.info(f"Successfully restored backup from: {backup_file}")
        return {"message": "Backup restored successfully"}
    except Exception as e:
        logger.error(f"Error restoring backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error restoring backup")

@router.get("/list")
async def list_backups(
    token: str = Depends(oauth2_scheme),
    backup_manager: BackupManager = Depends(get_backup_manager)
):
    try:
        backups = await backup_manager.list_backups()
        logger.info(f"Successfully listed {len(backups)} backups")
        return {"backups": backups}
    except Exception as e:
        logger.error(f"Error listing backups: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing backups")
