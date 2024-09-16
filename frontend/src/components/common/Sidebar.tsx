import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const Sidebar: React.FC = () => {
  const router = useRouter();

  const isActive = (pathname: string) => router.pathname === pathname;

  return (
    <aside className="bg-gray-800 text-white w-64 min-h-screen p-4">
      <nav>
        <ul className="space-y-2">
          <li>
            <Link href="/dashboard">
              <a className={`block p-2 rounded ${isActive('/dashboard') ? 'bg-indigo-600' : 'hover:bg-gray-700'}`}>
                Dashboard
              </a>
            </Link>
          </li>
          <li>
            <Link href="/tasks">
              <a className={`block p-2 rounded ${isActive('/tasks') ? 'bg-indigo-600' : 'hover:bg-gray-700'}`}>
                Tasks
              </a>
            </Link>
          </li>
          <li>
            <Link href="/email">
              <a className={`block p-2 rounded ${isActive('/email') ? 'bg-indigo-600' : 'hover:bg-gray-700'}`}>
                Email
              </a>
            </Link>
          </li>
          <li>
            <Link href="/calendar">
              <a className={`block p-2 rounded ${isActive('/calendar') ? 'bg-indigo-600' : 'hover:bg-gray-700'}`}>
                Calendar
              </a>
            </Link>
          </li>
          <li>
            <Link href="/nlp">
              <a className={`block p-2 rounded ${isActive('/nlp') ? 'bg-indigo-600' : 'hover:bg-gray-700'}`}>
                NLP Tools
              </a>
            </Link>
          </li>
          <li>
            <Link href="/settings">
              <a className={`block p-2 rounded ${isActive('/settings') ? 'bg-indigo-600' : 'hover:bg-gray-700'}`}>
                Settings
              </a>
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
