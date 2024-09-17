from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from personal_ai_assistant.github.github_client import GitHubClient
from personal_ai_assistant.config import settings
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


def get_github_client():
    return GitHubClient(settings.GITHUB_TOKEN)


@router.get("/repos")
async def get_github_repos(
    username: str,
    token: str = Depends(oauth2_scheme),
    github_client: GitHubClient = Depends(get_github_client)
):
    try:
        repos = await github_client.get_user_repos(username)
        logger.info(f"Successfully fetched GitHub repos for user: {username}")
        return {"repos": repos}
    except Exception as e:
        logger.error(f"Error fetching GitHub repos for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching GitHub repos")


@router.get("/issues")
async def get_github_issues(
    repo_full_name: str,
    token: str = Depends(oauth2_scheme),
    github_client: GitHubClient = Depends(get_github_client)
):
    try:
        issues = await github_client.get_repo_issues(repo_full_name)
        logger.info(f"Successfully fetched GitHub issues for repo: {repo_full_name}")
        return {"issues": issues}
    except Exception as e:
        logger.error(f"Error fetching GitHub issues for repo {repo_full_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching GitHub issues")
