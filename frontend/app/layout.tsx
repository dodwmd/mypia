import React from 'react';
import '../styles/globals.css';
import { AuthProvider } from '../src/contexts/AuthContext';
import ClientLayout from '../src/components/ClientLayout';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-background text-text">
        <AuthProvider>
          <ClientLayout>
            {children}
          </ClientLayout>
        </AuthProvider>
      </body>
    </html>
  );
}
