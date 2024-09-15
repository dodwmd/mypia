import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

const BottomNav: React.FC = () => {
  const navItems = [
    { href: '/', label: 'Dashboard' },
    { href: '/chat', label: 'Chat' },
    { href: '/tasks', label: 'Tasks' },
    { href: '/email', label: 'Email' },
    { href: '/calendar', label: 'Calendar' },
    { href: '/settings', label: 'Settings' },
  ];

  return (
    <motion.nav
      className="bg-white border-t border-secondary-200"
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: 0.05,
          },
        },
      }}
    >
      <ul className="flex justify-around">
        {navItems.map((item, index) => (
          <motion.li key={item.label} className="flex-1" variants={itemVariants}>
            <Link href={item.href}>
              <a className="flex flex-col items-center py-2 text-secondary-600 hover:text-primary-600 transition duration-150 ease-in-out">
                <span className="text-xs">{item.label}</span>
              </a>
            </Link>
          </motion.li>
        ))}
      </ul>
    </motion.nav>
  );
};

export default BottomNav;
