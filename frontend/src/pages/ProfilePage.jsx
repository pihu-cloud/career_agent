import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import {
  getProfile,
  updateProfile,
  getSkills,
  getInterests,
  getPersonality,
  getAcademics,
  getProfileCompletion,
} from '../services/profile';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import ProgressBar from '../components/ui/ProgressBar';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  UserCircleIcon,
  WrenchScrewdriverIcon,
  HeartIcon,
  SparklesIcon,
  AcademicCapIcon,
  CheckCircleIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';

export const ProfilePage = () => {
  const { user, setUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [sectionCounts, setSectionCounts] = useState({
    skills: 0,
    interests: 0,
    personality: 0,
    academics: 0,
  });
  const [completionData, setCompletionData] = useState({
    percentage: 50,
    sections: {
      basic_info: true,
      skills: false,
      interests: false,
      personality: false,
      academics: false,
    },
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting },
  } = useForm({
    defaultValues: {
      full_name: '',
      username: '',
      email: '',
      bio: '',
      phone: '',
      location: '',
    },
  });

  useEffect(() => {
    const loadProfileData = async () => {
      setLoading(true);
      try {
        const [profRes, skillsRes, intRes, persRes, acadRes, compRes] =
          await Promise.allSettled([
            getProfile(),
            getSkills(),
            getInterests(),
            getPersonality(),
            getAcademics(),
            getProfileCompletion(),
          ]);

        const profile = profRes.status === 'fulfilled' ? profRes.value : user || {};
        const skills = skillsRes.status === 'fulfilled' ? (Array.isArray(skillsRes.value) ? skillsRes.value : skillsRes.value.skills || []) : [];
        const interests = intRes.status === 'fulfilled' ? (Array.isArray(intRes.value) ? intRes.value : intRes.value.interests || []) : [];
        const personality = persRes.status === 'fulfilled' ? (Array.isArray(persRes.value) ? persRes.value : persRes.value.traits || []) : [];
        const academics = acadRes.status === 'fulfilled' ? (Array.isArray(acadRes.value) ? acadRes.value : acadRes.value.records || []) : [];

        reset({
          full_name: profile.full_name || user?.full_name || '',
          username: profile.username || user?.username || '',
          email: profile.email || user?.email || '',
          bio: profile.bio || '',
          phone: profile.phone || '',
          location: profile.location || '',
        });

        const counts = {
          skills: skills.length,
          interests: interests.length,
          personality: personality.length,
          academics: academics.length,
        };
        setSectionCounts(counts);

        if (compRes.status === 'fulfilled') {
          const val = compRes.value;
          setCompletionData({
            percentage: val.completion_percentage ?? val.percentage ?? 60,
            sections: val.sections || {
              basic_info: true,
              skills: counts.skills > 0,
              interests: counts.interests > 0,
              personality: counts.personality > 0,
              academics: counts.academics > 0,
            },
          });
        } else {
          setCompletionData({
            percentage: 60,
            sections: {
              basic_info: true,
              skills: counts.skills > 0,
              interests: counts.interests > 0,
              personality: counts.personality > 0,
              academics: counts.academics > 0,
            },
          });
        }
      } catch (err) {
        console.error('Failed to load profile details:', err);
      } finally {
        setLoading(false);
      }
    };

    loadProfileData();
  }, [user, reset]);

  const onUpdateProfile = async (data) => {
    try {
      const updated = await updateProfile(data);
      if (setUser) {
        setUser((prev) => ({ ...prev, ...data }));
      }
      toast.success('Profile updated successfully!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update profile');
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading profile details..." />;
  }

  const sectionsList = [
    {
      id: 'skills',
      title: 'Skills & Proficiencies',
      count: sectionCounts.skills,
      unit: 'skills',
      path: '/profile/skills',
      icon: WrenchScrewdriverIcon,
      isDone: sectionCounts.skills > 0,
      description: 'Technical languages, tools, frameworks & soft skills.',
    },
    {
      id: 'interests',
      title: 'Career Interests',
      count: sectionCounts.interests,
      unit: 'interests',
      path: '/profile/interests',
      icon: HeartIcon,
      isDone: sectionCounts.interests > 0,
      description: 'Domain fields, work styles, and industry preferences.',
    },
    {
      id: 'personality',
      title: 'Personality (OCEAN)',
      count: sectionCounts.personality,
      unit: 'traits assessed',
      path: '/profile/personality',
      icon: SparklesIcon,
      isDone: sectionCounts.personality > 0,
      description: 'Big Five psychometric profile for career environment fit.',
    },
    {
      id: 'academics',
      title: 'Academic Background',
      count: sectionCounts.academics,
      unit: 'degrees/records',
      path: '/profile/academics',
      icon: AcademicCapIcon,
      isDone: sectionCounts.academics > 0,
      description: 'University degrees, GPA, majors & coursework records.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header and Wizard banner */}
      <div className="bg-white p-6 rounded-xl border border-gray-200/80 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Student Profile Overview</h1>
            <p className="text-sm text-gray-500 mt-1">
              Maintain your credentials, preferences, and competencies for precision career recommendations.
            </p>
          </div>
          <Link to="/profile/complete">
            <Button variant="outline" size="sm">
              View Checklist
            </Button>
          </Link>
        </div>

        <ProgressBar
          label="Profile Completion Score"
          progress={completionData.percentage}
          color="gradient"
          size="lg"
        />

        {/* Wizard step pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          {sectionsList.map((sec) => (
            <Link
              key={sec.id}
              to={sec.path}
              className={`p-3 rounded-lg border text-left transition-colors flex items-center justify-between ${
                sec.isDone
                  ? 'border-green-200 bg-green-50/50 hover:bg-green-50'
                  : 'border-gray-200 bg-gray-50/50 hover:bg-gray-100'
              }`}
            >
              <div className="truncate mr-2">
                <p className="text-xs font-semibold text-gray-800 truncate">{sec.title}</p>
                <p className="text-xs text-gray-500">{sec.count} {sec.unit}</p>
              </div>
              {sec.isDone ? (
                <CheckCircleIcon className="h-5 w-5 text-success flex-shrink-0" />
              ) : (
                <span className="h-2 w-2 rounded-full bg-gray-300 flex-shrink-0" />
              )}
            </Link>
          ))}
        </div>
      </div>

      {/* Profile Form & Sections Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Personal Details Form */}
        <div className="lg:col-span-2">
          <Card
            title="Personal Details"
            subtitle="Manage your basic identity and contact coordinates"
          >
            <form onSubmit={handleSubmit(onUpdateProfile)} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  required
                  {...register('full_name')}
                />
                <Input
                  label="Username"
                  disabled
                  helperText="Username is fixed for identity integrity"
                  {...register('username')}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Email Address"
                  type="email"
                  disabled
                  helperText="Email linked to authentication"
                  {...register('email')}
                />
                <Input
                  label="Phone Number"
                  placeholder="+1 (555) 000-0000"
                  {...register('phone')}
                />
              </div>

              <Input
                label="Location"
                placeholder="City, Country"
                {...register('location')}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Professional Bio / Career Objective
                </label>
                <textarea
                  rows={3}
                  className="block w-full rounded-md border border-gray-300 text-sm p-3 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
                  placeholder="Share a short summary of your background, goals, and passions..."
                  {...register('bio')}
                />
              </div>

              <div className="flex justify-end pt-2">
                <Button type="submit" variant="primary" isLoading={isSubmitting}>
                  Save Profile Changes
                </Button>
              </div>
            </form>
          </Card>
        </div>

        {/* Sub-sections Navigation Cards */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-gray-900">Pathway Pillars</h2>
          {sectionsList.map((sec) => {
            const Icon = sec.icon;
            return (
              <Card
                key={sec.id}
                className="hover:border-primary-400 transition-all cursor-pointer group"
              >
                <Link to={sec.path} className="block">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2.5 bg-primary-50 rounded-lg text-primary-900 group-hover:bg-primary-900 group-hover:text-white transition-colors">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900 group-hover:text-primary-900">
                          {sec.title}
                        </h3>
                        <p className="text-xs text-gray-500 mt-0.5">{sec.count} {sec.unit}</p>
                      </div>
                    </div>
                    <ArrowRightIcon className="h-4 w-4 text-gray-400 group-hover:text-primary-900 group-hover:translate-x-1 transition-all" />
                  </div>
                  <p className="text-xs text-gray-500 mt-3">{sec.description}</p>
                </Link>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
