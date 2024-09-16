from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
from personal_ai_assistant.tasks.task_manager import TaskManager
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

class Task(BaseModel):
    title: str
    description: str

def get_task_manager():
    return TaskManager()

@router.get("/tasks")
async def get_tasks(
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        tasks = await task_manager.get_all_tasks()
        logger.info(f"Successfully fetched {len(tasks)} tasks")
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching tasks")

@router.post("/tasks")
async def create_task(
    task: Task,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        created_task = await task_manager.create_task(task.title, task.description)
        logger.info(f"Successfully created task: {task.title}")
        return {"message": "Task created successfully", "task": created_task}
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating task")

# You can add more task-related endpoints here, such as:
# - Update task
# - Delete task
# - Mark task as complete
# - Get task by ID
# For example:

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    task: Task,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        updated_task = await task_manager.update_task(task_id, task.title, task.description)
        logger.info(f"Successfully updated task: {task_id}")
        return {"message": "Task updated successfully", "task": updated_task}
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating task")

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        await task_manager.delete_task(task_id)
        logger.info(f"Successfully deleted task: {task_id}")
        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting task")

@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        completed_task = await task_manager.complete_task(task_id)
        logger.info(f"Successfully marked task as complete: {task_id}")
        return {"message": "Task marked as complete", "task": completed_task}
    except Exception as e:
        logger.error(f"Error marking task {task_id} as complete: {str(e)}")
        raise HTTPException(status_code=500, detail="Error marking task as complete")

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    token: str = Depends(oauth2_scheme),
    task_manager: TaskManager = Depends(get_task_manager)
):
    try:
        task = await task_manager.get_task(task_id)
        logger.info(f"Successfully fetched task: {task_id}")
        return {"task": task}
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching task")
