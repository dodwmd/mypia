import { useEffect } from 'react';
import useStore from '../store/useStore';

const useNotificationSimulator = () => {
  const { addNotification } = useStore();

  useEffect(() => {
    const interval = setInterval(() => {
      const randomNotification = {
        title: `New ${['Email', 'Task', 'Event'][Math.floor(Math.random() * 3)]}`,
        message: `This is a simulated notification for demonstration purposes.`,
        type: ['info', 'success', 'warning', 'error'][Math.floor(Math.random() * 4)] as 'info' | 'success' | 'warning' | 'error',
      };
      addNotification(randomNotification);
    }, 30000); // Add a new notification every 30 seconds

    return () => clearInterval(interval);
  }, [addNotification]);
};

export default useNotificationSimulator;
