import React from 'react';

interface DashboardWidgetProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: 'primary' | 'secondary' | 'accent';
}

const DashboardWidget: React.FC<DashboardWidgetProps> = ({ title, value, icon, color }) => {
  const colorClasses = {
    primary: 'bg-primary text-white',
    secondary: 'bg-secondary text-white',
    accent: 'bg-accent text-white',
  };

  return (
    <div className={`rounded-lg shadow-md p-6 flex items-center ${colorClasses[color]}`}>
      <div className="mr-4 text-3xl">{icon}</div>
      <div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </div>
  );
};

export default DashboardWidget;
