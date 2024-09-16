'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FaHome, FaTasks, FaCalendar, FaEnvelope, FaGithub, FaDatabase } from 'react-icons/fa';

const navItems = [
  { href: '/', label: 'Home', icon: <FaHome /> },
  { href: '/tasks', label: 'Tasks', icon: <FaTasks /> },
  { href: '/calendar', label: 'Calendar', icon: <FaCalendar /> },
  { href: '/email', label: 'Email', icon: <FaEnvelope /> },
  { href: '/github', label: 'GitHub', icon: <FaGithub /> },
  { href: '/vectordb', label: 'Vector DB', icon: <FaDatabase /> },
];

const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <nav className="w-64 bg-primary text-white p-6 fixed h-full">
      <h1 className="text-2xl font-bold mb-8 text-white">MyPIA</h1>
      <ul className="space-y-2">
        {navItems.map((item) => (
          <li key={item.href}>
            <Link href={item.href} className={`flex items-center py-2 px-4 rounded transition-colors ${
              pathname === item.href ? 'bg-primary-dark' : 'hover:bg-primary-light'
            }`}>
              <span className="mr-3">{item.icon}</span>
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Sidebar;
