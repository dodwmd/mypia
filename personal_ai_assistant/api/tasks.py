from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from personal_ai_assistant.tasks.task_manager import TaskManager
from personal_ai_assistant.models.task import Task  # Add this import
from personal_ai_assistant.api.dependencies import get_db
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool


def get_task_manager(db: Session = Depends(get_db)):
    return TaskManager(db)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        created_task = await task_manager.create_task(task.title, task.description)
        logger.info(f"Successfully created task: {task.title}")
        return TaskResponse(**created_task.to_dict())
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating task")


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        tasks = await task_manager.get_all_tasks()
        logger.info(f"Successfully fetched {len(tasks)} tasks")
        return [TaskResponse(**task.to_dict()) for task in tasks]
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching tasks")


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task: TaskCreate,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        updated_task = await task_manager.update_task(task_id, task.title, task.description)
        if updated_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(f"Successfully updated task: {task_id}")
        return TaskResponse(**updated_task.to_dict())
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating task")


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        deleted = await task_manager.delete_task(task_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(f"Successfully deleted task: {task_id}")
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting task")


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        completed_task = await task_manager.complete_task(task_id)
        if completed_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(f"Successfully marked task as complete: {task_id}")
        return TaskResponse(**completed_task.to_dict())
    except Exception as e:
        logger.error(f"Error marking task {task_id} as complete: {str(e)}")
        raise HTTPException(status_code=500, detail="Error marking task as complete")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        task = await task_manager.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(f"Successfully fetched task: {task_id}")
        return TaskResponse(**task.to_dict())
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching task")
