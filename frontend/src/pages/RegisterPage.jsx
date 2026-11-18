import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { register as apiRegister } from '../services/auth';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { SparklesIcon } from '@heroicons/react/24/outline';

const registerSchema = z
  .object({
    full_name: z.string().min(2, 'Full name must be at least 2 characters'),
    username: z
      .string()
      .min(3, 'Username must be at least 3 characters')
      .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
    email: z.string().email('Please enter a valid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirm_password: z.string(),
    role: z.enum(['student', 'admin']),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
  });

export const RegisterPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: '',
      username: '',
      email: '',
      password: '',
      confirm_password: '',
      role: 'student',
    },
  });

  const passwordVal = watch('password', '');

  // Calculate password strength: 0 to 4
  const getPasswordStrength = (pass) => {
    let score = 0;
    if (pass.length >= 8) score += 1;
    if (/[A-Z]/.test(pass)) score += 1;
    if (/[0-9]/.test(pass)) score += 1;
    if (/[^A-Za-z0-9]/.test(pass)) score += 1;
    return score;
  };

  const strength = getPasswordStrength(passwordVal);
  const strengthLabels = ['Too Weak', 'Weak', 'Fair', 'Good', 'Strong'];
  const strengthColors = ['bg-gray-200', 'bg-red-500', 'bg-amber-500', 'bg-blue-500', 'bg-green-500'];

  const onSubmit = async (data) => {
    setErrorMsg('');
    try {
      const payload = {
        full_name: data.full_name,
        username: data.username,
        email: data.email,
        password: data.password,
        role: data.role,
      };
      await apiRegister(payload);
      toast.success('Registration successful! Logging you in...');
      // Auto login
      await login(data.email, data.password);
      navigate('/onboarding');
    } catch (err) {
      const detail =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Registration failed. Please check your inputs.';
      setErrorMsg(typeof detail === 'string' ? detail : JSON.stringify(detail));
      toast.error('Registration failed');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex h-12 w-12 rounded-xl bg-gradient-to-tr from-primary-900 to-secondary-600 items-center justify-center text-white shadow-lg mb-3">
          <SparklesIcon className="h-7 w-7" />
        </div>
        <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">
          Create Account
        </h2>
        <p className="mt-2 text-sm text-gray-600">
          Get started with CareerPilot AI personalized pathways
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-lg">
        <Card className="px-6 py-8 shadow-md">
          {errorMsg && (
            <div className="mb-4 p-3 bg-red-50 border-l-4 border-danger text-sm text-red-700 rounded">
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                required
                placeholder="Jane Doe"
                error={errors.full_name?.message}
                {...register('full_name')}
              />
              <Input
                label="Username"
                required
                placeholder="janedoe"
                error={errors.username?.message}
                {...register('username')}
              />
            </div>

            <Input
              label="Email Address"
              type="email"
              required
              placeholder="jane@example.com"
              error={errors.email?.message}
              {...register('email')}
            />

            <div>
              <Input
                label="Password"
                type="password"
                required
                placeholder="••••••••"
                error={errors.password?.message}
                {...register('password')}
              />
              {/* Strength Meter */}
              {passwordVal && (
                <div className="mt-2">
                  <div className="flex justify-between items-center text-xs mb-1">
                    <span className="text-gray-500">Strength:</span>
                    <span className="font-semibold text-gray-700">
                      {strengthLabels[strength]}
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden flex gap-1">
                    {[1, 2, 3, 4].map((step) => (
                      <div
                        key={step}
                        className={`h-full flex-1 rounded-full transition-colors ${
                          step <= strength ? strengthColors[strength] : 'bg-gray-200'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>

            <Input
              label="Confirm Password"
              type="password"
              required
              placeholder="••••••••"
              error={errors.confirm_password?.message}
              {...register('confirm_password')}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Account Role
              </label>
              <select
                {...register('role')}
                className="block w-full rounded-md border border-gray-300 text-sm px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
              >
                <option value="student">Student / Job Seeker</option>
                <option value="admin">System Administrator</option>
              </select>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full mt-2"
              isLoading={isSubmitting}
            >
              Complete Registration
            </Button>
          </form>

          <div className="mt-6 border-t border-gray-100 pt-4 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-semibold text-secondary-600 hover:text-secondary-700"
              >
                Sign In here
              </Link>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default RegisterPage;
