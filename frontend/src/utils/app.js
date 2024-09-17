import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost/v1', // Replace with your API URL
})

// Add a request interceptor to include the token in all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export const fetchTasks = () => api.get('/tasks').then(response => response.data.tasks)
export const createTask = (task) => api.post('/tasks', task).then(response => response.data)

// Add more API functions as needed

export default api
