import React from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { Button, InputField, Dropdown, Modal } from './UIComponents';
import useStore from '../store/useStore';

interface SettingsFormData {
  username: string;
  email: string;
  language: string;
  theme: string;
  notifications: boolean;
  emailFrequency: string;
  aiModel: string;
  privacyLevel: string;
}

const schema = yup.object().shape({
  username: yup.string().required('Username is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  language: yup.string().required('Language is required'),
  theme: yup.string().required('Theme is required'),
  notifications: yup.boolean(),
  emailFrequency: yup.string().required('Email frequency is required'),
  aiModel: yup.string().required('AI model is required'),
  privacyLevel: yup.string().required('Privacy level is required'),
});

const Settings: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { user, settings, setUser, setSettings } = useStore();

  const { register, handleSubmit, formState: { errors }, watch, reset } = useForm<SettingsFormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      username: user?.username || '',
      email: user?.email || '',
      ...settings,
    },
  });

  useEffect(() => {
    reset({
      username: user?.username || '',
      email: user?.email || '',
      ...settings,
    });
  }, [user, settings, reset]);

  const onSubmit = (data: SettingsFormData) => {
    const { username, email, ...newSettings } = data;
    setUser({ ...user!, username, email });
    setSettings(newSettings);
    setIsModalOpen(true);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-secondary-900 font-display">Settings</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <InputField
          id="username"
          label="Username"
          {...register('username')}
          error={errors.username?.message}
        />

        <InputField
          id="email"
          label="Email"
          type="email"
          {...register('email')}
          error={errors.email?.message}
        />

        <Dropdown
          label="Language"
          options={[
            { value: 'en', label: 'English' },
            { value: 'es', label: 'Spanish' },
            { value: 'fr', label: 'French' },
          ]}
          value={watch('language')}
          onChange={(value) => register('language').onChange({ target: { value } })}
        />

        <Dropdown
          label="Theme"
          options={[
            { value: 'light', label: 'Light' },
            { value: 'dark', label: 'Dark' },
            { value: 'system', label: 'System' },
          ]}
          value={watch('theme')}
          onChange={(value) => register('theme').onChange({ target: { value } })}
        />

        <div className="flex items-center">
          <input
            type="checkbox"
            id="notifications"
            {...register('notifications')}
            className="h-4 w-4 rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
          />
          <label htmlFor="notifications" className="ml-2 block text-sm text-secondary-700">Enable notifications</label>
        </div>

        <Dropdown
          label="Email Frequency"
          options={[
            { value: 'daily', label: 'Daily' },
            { value: 'weekly', label: 'Weekly' },
            { value: 'monthly', label: 'Monthly' },
          ]}
          value={watch('emailFrequency')}
          onChange={(value) => register('emailFrequency').onChange({ target: { value } })}
        />

        <Dropdown
          label="AI Model"
          options={[
            { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
            { value: 'gpt-4', label: 'GPT-4' },
            { value: 'claude-v1', label: 'Claude v1' },
          ]}
          value={watch('aiModel')}
          onChange={(value) => register('aiModel').onChange({ target: { value } })}
        />

        <Dropdown
          label="Privacy Level"
          options={[
            { value: 'high', label: 'High' },
            { value: 'balanced', label: 'Balanced' },
            { value: 'low', label: 'Low' },
          ]}
          value={watch('privacyLevel')}
          onChange={(value) => register('privacyLevel').onChange({ target: { value } })}
        />

        <Button type="submit" variant="primary" fullWidth>
          Save Settings
        </Button>
      </form>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Settings Saved"
      >
        <p className="text-sm text-gray-500">
          Your settings have been successfully saved.
        </p>
        <div className="mt-4">
          <Button onClick={() => setIsModalOpen(false)} variant="secondary">
            Close
          </Button>
        </div>
      </Modal>
    </div>
  );
};

export default Settings;
