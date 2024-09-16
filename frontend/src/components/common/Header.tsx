import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const Header: React.FC = () => {
  const router = useRouter();

  const handleLogout = () => {
    // Clear the token from localStorage
    localStorage.removeItem('token');
    // Redirect to login page
    router.push('/login');
  };

  return (
    <header className="bg-indigo-600 text-white">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/">
          <a className="text-2xl font-bold">MyPIA</a>
        </Link>
        <nav>
          <ul className="flex space-x-4">
            <li>
              <Link href="/dashboard">
                <a className="hover:text-indigo-200">Dashboard</a>
              </Link>
            </li>
            <li>
              <Link href="/tasks">
                <a className="hover:text-indigo-200">Tasks</a>
              </Link>
            </li>
            <li>
              <Link href="/email">
                <a className="hover:text-indigo-200">Email</a>
              </Link>
            </li>
            <li>
              <Link href="/calendar">
                <a className="hover:text-indigo-200">Calendar</a>
              </Link>
            </li>
            <li>
              <Link href="/nlp">
                <a className="hover:text-indigo-200">NLP Tools</a>
              </Link>
            </li>
            <li>
              <button onClick={handleLogout} className="hover:text-indigo-200">
                Logout
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
