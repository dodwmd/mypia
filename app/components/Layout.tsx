import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import Sidebar from './Sidebar';
import BottomNav from './BottomNav';
import NotificationCenter from './NotificationCenter';
import useStore from '../store/useStore';

const pageVariants = {
  initial: { opacity: 0, x: -200 },
  in: { opacity: 1, x: 0 },
  out: { opacity: 0, x: 200 },
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.5,
};

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { settings, isDarkMode } = useStore();

  useEffect(() => {
    if (isDarkMode || (settings.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode, settings.theme]);

  return (
    <div className="flex h-screen bg-secondary-50 text-secondary-900 dark:bg-secondary-900 dark:text-secondary-50 font-sans transition-colors duration-200">
      {/* Sidebar for desktop */}
      <div className="hidden md:flex md:flex-shrink-0">
        <Sidebar />
      </div>

      {/* Main content area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top bar with notification center */}
        <div className="bg-white dark:bg-secondary-800 shadow-sm z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-3 md:justify-end md:space-x-10">
              <NotificationCenter />
            </div>
          </div>
        </div>

        <motion.main
          className="flex-1 overflow-y-auto p-4 md:p-6"
          initial="initial"
          animate="in"
          exit="out"
          variants={pageVariants}
          transition={pageTransition}
        >
          {children}
        </motion.main>

        {/* Bottom navigation for mobile */}
        <div className="md:hidden">
          <BottomNav />
        </div>
      </div>
    </div>
  );
};

export default Layout;
