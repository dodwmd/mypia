import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Button, InputField } from './UIComponents';
import useStore from '../store/useStore';

interface LoginFormData {
  email: string;
  password: string;
}

const schema = yup.object().shape({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().required('Password is required'),
});

interface LoginProps {
  onRegisterClick: () => void;
  onForgotPasswordClick: () => void;
}

const Login: React.FC<LoginProps> = ({ onRegisterClick, onForgotPasswordClick }) => {
  const { setUser, setIsAuthenticated } = useStore();
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: yupResolver(schema),
  });

  const onSubmit = (data: LoginFormData) => {
    // Here you would typically make an API call to authenticate the user
    console.log('Login data:', data);
    setUser({ id: '1', username: 'User', email: data.email });
    setIsAuthenticated(true);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <InputField
        id="email"
        label="Email address"
        type="email"
        {...register('email')}
        error={errors.email?.message}
      />
      <InputField
        id="password"
        label="Password"
        type="password"
        {...register('password')}
        error={errors.password?.message}
      />
      <div className="flex items-center justify-between">
        <div className="text-sm">
          <button
            type="button"
            onClick={onForgotPasswordClick}
            className="font-medium text-primary-600 hover:text-primary-500"
          >
            Forgot your password?
          </button>
        </div>
      </div>
      <Button type="submit" variant="primary" fullWidth>
        Sign in
      </Button>
      <div className="text-sm text-center">
        <span className="text-secondary-500">Don't have an account? </span>
        <button
          type="button"
          onClick={onRegisterClick}
          className="font-medium text-primary-600 hover:text-primary-500"
        >
          Register
        </button>
      </div>
    </form>
  );
};

export default Login;
