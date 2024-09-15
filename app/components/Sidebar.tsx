import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import useStore from '../store/useStore';
import { MoonIcon, SunIcon } from '@heroicons/react/solid';

const linkVariants = {
  hover: { scale: 1.05, transition: { duration: 0.2 } },
  tap: { scale: 0.95 },
};

const Sidebar: React.FC = () => {
  const { isDarkMode, toggleDarkMode } = useStore();

  const menuItems = [
    { name: 'Dashboard', href: '/' },
    { name: 'Chat', href: '/chat' },
    { name: 'Tasks', href: '/tasks' },
    { name: 'Email', href: '/email' },
    { name: 'Calendar', href: '/calendar' },
    { name: 'Settings', href: '/settings' },
  ];

  return (
    <div className="flex flex-col w-64 bg-white dark:bg-secondary-800 border-r border-secondary-200 dark:border-secondary-700">
      <div className="flex items-center justify-between h-16 px-4 border-b border-secondary-200 dark:border-secondary-700">
        <span className="text-xl font-semibold font-display text-primary-600 dark:text-primary-400">MyPIA</span>
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-full bg-secondary-100 dark:bg-secondary-700 text-secondary-600 dark:text-secondary-400 hover:bg-secondary-200 dark:hover:bg-secondary-600 transition-colors duration-200"
        >
          {isDarkMode ? (
            <SunIcon className="h-5 w-5" />
          ) : (
            <MoonIcon className="h-5 w-5" />
          )}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto">
        <ul className="p-4 space-y-2">
          {menuItems.map((item) => (
            <li key={item.name}>
              <Link href={item.href} passHref>
                <motion.a
                  className="flex items-center p-2 text-secondary-700 dark:text-secondary-300 hover:bg-primary-50 dark:hover:bg-primary-900 hover:text-primary-700 dark:hover:text-primary-300 rounded transition duration-150 ease-in-out"
                  variants={linkVariants}
                  whileHover="hover"
                  whileTap="tap"
                >
                  <span className="ml-3">{item.name}</span>
                </motion.a>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
