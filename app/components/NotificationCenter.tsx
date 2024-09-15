import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaBell } from 'react-icons/fa';
import useStore from '../store/useStore';

const NotificationCenter: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { notifications, markNotificationAsRead, clearNotifications } = useStore();

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleNotificationClick = (id: string) => {
    markNotificationAsRead(id);
    // Here you could add logic to navigate to the relevant page or perform an action
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-full hover:bg-secondary-100 dark:hover:bg-secondary-700 transition-colors duration-200"
      >
        <FaBell className="text-secondary-600 dark:text-secondary-400" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 mt-2 w-80 bg-white dark:bg-secondary-800 rounded-md shadow-lg overflow-hidden z-50"
          >
            <div className="p-4 border-b border-secondary-200 dark:border-secondary-700">
              <h3 className="text-lg font-semibold text-secondary-900 dark:text-secondary-100">Notifications</h3>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <p className="p-4 text-secondary-600 dark:text-secondary-400">No notifications</p>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification.id)}
                    className={`p-4 border-b border-secondary-200 dark:border-secondary-700 cursor-pointer hover:bg-secondary-50 dark:hover:bg-secondary-700 transition-colors duration-200 ${
                      !notification.read ? 'bg-primary-50 dark:bg-primary-900' : ''
                    }`}
                  >
                    <h4 className="font-semibold text-secondary-900 dark:text-secondary-100">{notification.title}</h4>
                    <p className="text-sm text-secondary-600 dark:text-secondary-400">{notification.message}</p>
                    <p className="text-xs text-secondary-500 dark:text-secondary-500 mt-1">
                      {new Date(notification.createdAt).toLocaleString()}
                    </p>
                  </div>
                ))
              )}
            </div>
            {notifications.length > 0 && (
              <div className="p-4 border-t border-secondary-200 dark:border-secondary-700">
                <button
                  onClick={clearNotifications}
                  className="w-full px-4 py-2 bg-secondary-100 dark:bg-secondary-700 text-secondary-900 dark:text-secondary-100 rounded hover:bg-secondary-200 dark:hover:bg-secondary-600 transition-colors duration-200"
                >
                  Clear all notifications
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NotificationCenter;
