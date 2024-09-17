import React, { useState, useEffect } from 'react';

const DebugLogs: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const storedLogs = localStorage.getItem('auth_logs');
    if (storedLogs) {
      setLogs(JSON.parse(storedLogs));
    }

    const intervalId = setInterval(() => {
      const updatedLogs = localStorage.getItem('auth_logs');
      if (updatedLogs) {
        setLogs(JSON.parse(updatedLogs));
      }
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="fixed bottom-0 left-0 p-4 bg-black text-white opacity-75 max-h-48 overflow-y-auto">
      <h3>Debug Logs:</h3>
      {logs.map((log, index) => (
        <div key={index}>{log}</div>
      ))}
    </div>
  );
};

export default DebugLogs;
