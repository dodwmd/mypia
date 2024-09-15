import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Button, InputField } from './UIComponents';

interface PasswordResetFormData {
  email: string;
}

const schema = yup.object().shape({
  email: yup.string().email('Invalid email').required('Email is required'),
});

interface PasswordResetProps {
  onBackToLoginClick: () => void;
}

const PasswordReset: React.FC<PasswordResetProps> = ({ onBackToLoginClick }) => {
  const { register, handleSubmit, formState: { errors } } = useForm<PasswordResetFormData>({
    resolver: yupResolver(schema),
  });

  const onSubmit = (data: PasswordResetFormData) => {
    // Here you would typically make an API call to initiate the password reset process
    console.log('Password reset data:', data);
    alert('Password reset email sent. Please check your inbox.');
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
      <Button type="submit" variant="primary" fullWidth>
        Reset Password
      </Button>
      <div className="text-sm text-center">
        <button
          type="button"
          onClick={onBackToLoginClick}
          className="font-medium text-primary-600 hover:text-primary-500"
        >
          Back to Sign in
        </button>
      </div>
    </form>
  );
};

export default PasswordReset;
