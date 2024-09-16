import api from './api';

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'done';
  due_date: string;
}

export interface CreateTaskDto {
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'done';
  due_date: string;
}

export interface UpdateTaskDto {
  title?: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'done';
  due_date?: string;
}

export const getTasks = async (): Promise<Task[]> => {
  try {
    const response = await api.get('/tasks');
    return response.data;
  } catch (error) {
    console.error('Error fetching tasks:', error);
    throw error;
  }
};

export const getTaskById = async (id: string): Promise<Task> => {
  try {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching task:', error);
    throw error;
  }
};

export const createTask = async (taskData: CreateTaskDto): Promise<Task> => {
  try {
    const response = await api.post('/tasks', taskData);
    return response.data;
  } catch (error) {
    console.error('Error creating task:', error);
    throw error;
  }
};

export const updateTask = async (id: string, taskData: UpdateTaskDto): Promise<Task> => {
  try {
    const response = await api.patch(`/tasks/${id}`, taskData);
    return response.data;
  } catch (error) {
    console.error('Error updating task:', error);
    throw error;
  }
};

export const deleteTask = async (id: string): Promise<void> => {
  try {
    await api.delete(`/tasks/${id}`);
  } catch (error) {
    console.error('Error deleting task:', error);
    throw error;
  }
};

export const searchTasks = async (query: string): Promise<Task[]> => {
  try {
    const response = await api.get('/tasks/search', { params: { query } });
    return response.data;
  } catch (error) {
    console.error('Error searching tasks:', error);
    throw error;
  }
};
