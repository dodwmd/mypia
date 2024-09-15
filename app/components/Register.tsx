import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Button, InputField } from './UIComponents';
import useStore from '../store/useStore';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const schema = yup.object().shape({
  username: yup.string().required('Username is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(8, 'Password must be at least 8 characters').required('Password is required'),
  confirmPassword: yup.string().oneOf([yup.ref('password'), null], 'Passwords must match'),
});

interface RegisterProps {
  onLoginClick: () => void;
}

const Register: React.FC<RegisterProps> = ({ onLoginClick }) => {
  const { setUser, setIsAuthenticated } = useStore();
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
    resolver: yupResolver(schema),
  });

  const onSubmit = (data: RegisterFormData) => {
    // Here you would typically make an API call to register the user
    console.log('Register data:', data);
    setUser({ id: '1', username: data.username, email: data.email });
    setIsAuthenticated(true);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <InputField
        id="username"
        label="Username"
        {...register('username')}
        error={errors.username?.message}
      />
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
      <InputField
        id="confirmPassword"
        label="Confirm Password"
        type="password"
        {...register('confirmPassword')}
        error={errors.confirmPassword?.message}
      />
      <Button type="submit" variant="primary" fullWidth>
        Register
      </Button>
      <div className="text-sm text-center">
        <span className="text-secondary-500">Already have an account? </span>
        <button
          type="button"
          onClick={onLoginClick}
          className="font-medium text-primary-600 hover:text-primary-500"
        >
          Sign in
        </button>
      </div>
    </form>
  );
};

export default Register;
