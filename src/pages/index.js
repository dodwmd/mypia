import * as React from "react"
import { Link } from "gatsby"
import Layout from "../components/Layout"

const IndexPage = () => (
  <Layout>
    <h1 className="text-4xl font-bold mb-4">Welcome to MyPIA</h1>
    <p className="mb-4">Your Personal AI Assistant</p>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Link to="/tasks" className="bg-blue-500 text-white p-4 rounded hover:bg-blue-600">Manage Tasks</Link>
      <Link to="/email" className="bg-green-500 text-white p-4 rounded hover:bg-green-600">Check Emails</Link>
      <Link to="/calendar" className="bg-yellow-500 text-white p-4 rounded hover:bg-yellow-600">View Calendar</Link>
      <Link to="/nlp" className="bg-red-500 text-white p-4 rounded hover:bg-red-600">NLP Tools</Link>
    </div>
  </Layout>
)

export default IndexPage
