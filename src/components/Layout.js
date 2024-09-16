import React from "react"
import { Link } from "gatsby"

const Layout = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="bg-purple-700 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold">MyPIA</Link>
          <nav>
            <Link to="/" className="mr-4">Home</Link>
            <Link to="/tasks" className="mr-4">Tasks</Link>
            <Link to="/email" className="mr-4">Email</Link>
            <Link to="/calendar" className="mr-4">Calendar</Link>
          </nav>
        </div>
      </header>
      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="bg-gray-200 p-4">
        <div className="container mx-auto text-center">
          © {new Date().getFullYear()} MyPIA. All rights reserved.
        </div>
      </footer>
    </div>
  )
}

export default Layout
