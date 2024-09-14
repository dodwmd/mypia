import asyncio
import aiohttp
import os
import json
import subprocess
from typing import Dict, Any
from personal_ai_assistant.config import settings
from personal_ai_assistant.utils.logging_config import setup_logging

logger = setup_logging()

class UpdateManager:
    def __init__(self):
        self.update_url = settings.update_url
        self.current_version = settings.version
        self.update_info = None

    async def check_for_updates(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.update_url}/version") as response:
                if response.status == 200:
                    self.update_info = await response.json()
                    return self.update_info['version'] > self.current_version
                else:
                    logger.error(f"Failed to check for updates: {response.status}")
                    return False

    async def download_update(self, component: str) -> str:
        if not self.update_info:
            raise ValueError("No update information available. Call check_for_updates first.")

        download_url = self.update_info['components'][component]['url']
        file_name = os.path.basename(download_url)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status == 200:
                    with open(file_name, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    logger.info(f"Downloaded {component} update: {file_name}")
                    return file_name
                else:
                    logger.error(f"Failed to download {component} update: {response.status}")
                    return ""

    async def apply_update(self, component: str, file_name: str) -> bool:
        if component == 'llm_model':
            # Update LLM model
            new_model_path = os.path.join(settings.model_dir, file_name)
            os.rename(file_name, new_model_path)
            settings.llm_model_path = new_model_path
        elif component == 'embeddings':
            # Update embeddings model
            new_embeddings_path = os.path.join(settings.model_dir, file_name)
            os.rename(file_name, new_embeddings_path)
            settings.embedding_model = new_embeddings_path
        elif component == 'system':
            # Update system components
            subprocess.run(['pip', 'install', '--upgrade', file_name])
            os.remove(file_name)
        else:
            logger.error(f"Unknown component: {component}")
            return False

        logger.info(f"Applied {component} update: {file_name}")
        return True

    async def update_all(self):
        if await self.check_for_updates():
            for component in self.update_info['components']:
                file_name = await self.download_update(component)
                if file_name:
                    success = await self.apply_update(component, file_name)
                    if not success:
                        logger.error(f"Failed to apply {component} update")
            
            # Update current version
            settings.version = self.update_info['version']
            logger.info(f"Updated to version {settings.version}")
        else:
            logger.info("No updates available")

async def run_update_check():
    updater = UpdateManager()
    await updater.update_all()

if __name__ == "__main__":
    asyncio.run(run_update_check())
