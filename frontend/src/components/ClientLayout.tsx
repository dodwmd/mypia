'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './layout/Sidebar';
import Image from 'next/image';

const ClientLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user === null && pathname !== '/login' && pathname !== '/register') {
      router.push('/login');
    } else {
      setIsLoading(false);
    }
  }, [user, router, pathname]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-800">
        <Image
          src="/img/loading.gif"
          alt="Loading"
          width={100}
          height={100}
        />
        <p className="mt-4 text-white text-xl">Loading</p>
      </div>
    );
  }

  // If we're on the login or register page, don't show the sidebar
  if (pathname === '/login' || pathname === '/register') {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 overflow-y-auto ml-64">
        {children}
      </main>
    </div>
  );
};

export default ClientLayout;
