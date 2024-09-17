'use client';

import React, { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './layout/Sidebar';
import Image from 'next/image';

const ClientLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading) {
      if (!user && pathname !== '/login' && pathname !== '/register') {
        router.push('/login');
      } else if (user && (pathname === '/login' || pathname === '/register')) {
        router.push('/');
      }
    }
  }, [user, isLoading, pathname, router]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-800">
        <div className="w-24 h-24 relative">
          <Image
            src="/img/loading.gif"
            alt="Loading"
            width={96}
            height={96}
            style={{ objectFit: 'contain' }}
            unoptimized
          />
        </div>
        <p className="mt-4 text-white text-xl">Loading</p>
      </div>
    );
  }

  if (!user && (pathname === '/login' || pathname === '/register')) {
    return <>{children}</>;
  }

  if (!user) {
    return null;
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
