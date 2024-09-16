import React, { useState, useEffect } from "react"
import Layout from "../components/Layout"

const TasksPage = () => {
  const [tasks, setTasks] = useState([])
  const [newTask, setNewTask] = useState({ title: "", description: "" })

  useEffect(() => {
    // Fetch tasks from API
    // Replace with actual API call
    setTasks([
      { id: 1, title: "Task 1", description: "Description 1" },
      { id: 2, title: "Task 2", description: "Description 2" },
    ])
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    // Add new task to API
    // Replace with actual API call
    setTasks([...tasks, { id: tasks.length + 1, ...newTask }])
    setNewTask({ title: "", description: "" })
  }

  return (
    <Layout>
      <h1 className="text-3xl font-bold mb-4">Tasks</h1>
      <form onSubmit={handleSubmit} className="mb-4">
        <input
          type="text"
          placeholder="Title"
          value={newTask.title}
          onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
          className="border p-2 mr-2"
        />
        <input
          type="text"
          placeholder="Description"
          value={newTask.description}
          onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
          className="border p-2 mr-2"
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">Add Task</button>
      </form>
      <ul>
        {tasks.map((task) => (
          <li key={task.id} className="mb-2">
            <strong>{task.title}</strong>: {task.description}
          </li>
        ))}
      </ul>
    </Layout>
  )
}

export default TasksPage
