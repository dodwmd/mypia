import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Login from './Login';
import Register from './Register';
import PasswordReset from './PasswordReset';

type AuthPage = 'login' | 'register' | 'passwordReset';

const pageVariants = {
  initial: { opacity: 0, y: 50 },
  in: { opacity: 1, y: 0 },
  out: { opacity: 0, y: -50 },
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.5,
};

const Auth: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<AuthPage>('login');

  const renderPage = () => {
    switch (currentPage) {
      case 'login':
        return <Login onRegisterClick={() => setCurrentPage('register')} onForgotPasswordClick={() => setCurrentPage('passwordReset')} />;
      case 'register':
        return <Register onLoginClick={() => setCurrentPage('login')} />;
      case 'passwordReset':
        return <PasswordReset onBackToLoginClick={() => setCurrentPage('login')} />;
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-secondary-900">
          {currentPage === 'login' ? 'Sign in to your account' :
           currentPage === 'register' ? 'Create a new account' :
           'Reset your password'}
        </h2>
      </div>
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentPage}
              initial="initial"
              animate="in"
              exit="out"
              variants={pageVariants}
              transition={pageTransition}
            >
              {renderPage()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default Auth;
