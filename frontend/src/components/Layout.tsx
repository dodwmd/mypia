import React from 'react';
import Link from 'next/link';
import { useAuth } from '../contexts/AuthContext';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();

  return (
    <div className="flex flex-col min-h-screen">
      <header className="bg-purple-700 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold">
            MyPIA
          </Link>
          <nav>
            <Link href="/" className="mr-4">Home</Link>
            <Link href="/tasks" className="mr-4">Tasks</Link>
            <Link href="/email" className="mr-4">Email</Link>
            <Link href="/calendar" className="mr-4">Calendar</Link>
            <Link href="/contact" className="mr-4">Contact</Link>
            <Link href="/terms" className="mr-4">Terms</Link>
            {user ? (
              <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded">
                Logout
              </button>
            ) : (
              <Link href="/login" className="bg-green-500 text-white px-4 py-2 rounded">
                Login
              </Link>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-grow container mx-auto px-4 py-8">{children}</main>
      <footer className="bg-gray-200 p-4">
        <div className="container mx-auto text-center">
          © {new Date().getFullYear()} MyPIA. All rights reserved.
          <div className="mt-2">
            <Link href="/terms" className="mr-4">Terms of Service</Link>
            <Link href="/contact">Contact Us</Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
