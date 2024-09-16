'use client';

import React from 'react';
import Link from 'next/link';
import DashboardWidget from '../src/components/dashboard/DashboardWidget';
import { FaTasks, FaCalendar, FaEnvelope, FaGithub, FaDatabase } from 'react-icons/fa';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">Personal AI Assistant Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <DashboardWidget title="Tasks" value="5" icon={<FaTasks />} color="primary" />
        <DashboardWidget title="Upcoming Events" value="3" icon={<FaCalendar />} color="secondary" />
        <DashboardWidget title="Unread Emails" value="10" icon={<FaEnvelope />} color="accent" />
        <DashboardWidget title="GitHub PRs" value="2" icon={<FaGithub />} color="primary" />
        <DashboardWidget title="Vector DB Entries" value="1000" icon={<FaDatabase />} color="secondary" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { href: '/tasks', label: 'Tasks', color: 'bg-primary-light hover:bg-primary text-white' },
          { href: '/calendar', label: 'Calendar', color: 'bg-secondary-light hover:bg-secondary text-white' },
          { href: '/email', label: 'Email', color: 'bg-accent-light hover:bg-accent text-white' },
          { href: '/github', label: 'GitHub', color: 'bg-primary-light hover:bg-primary text-white' },
          { href: '/vectordb', label: 'Vector DB', color: 'bg-secondary-light hover:bg-secondary text-white' },
        ].map((item) => (
          <Link key={item.href} href={item.href}>
            <div className={`p-6 rounded-lg shadow-md transition-colors duration-300 ${item.color}`}>
              <h2 className="text-2xl font-semibold mb-2">{item.label}</h2>
              <p>Manage your {item.label.toLowerCase()} here.</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
