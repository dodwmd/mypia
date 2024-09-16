import React from 'react';
import '../styles/globals.css';
import dynamic from 'next/dynamic';

const Sidebar = dynamic(() => import('../src/components/layout/Sidebar'), { ssr: false });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-background text-text">
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 p-8 overflow-y-auto ml-64">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
