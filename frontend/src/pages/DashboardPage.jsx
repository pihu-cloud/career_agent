import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  getSkills,
  getInterests,
  getProfileCompletion,
} from '../services/profile';
import { getResumes } from '../services/resume';
import api from '../services/api';
import {
  SparklesIcon,
  WrenchScrewdriverIcon,
  HeartIcon,
  DocumentTextIcon,
  ArrowRightIcon,
  BellIcon,
  ClockIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

export const DashboardPage = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    skillsCount: 0,
    interestsCount: 0,
    resumesCount: 0,
    completionPercentage: 0,
  });
  const [recentActivities, setRecentActivities] = useState([]);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const [skillsRes, interestsRes, resumesRes, completionRes] = await Promise.allSettled([
          getSkills(),
          getInterests(),
          getResumes(),
          getProfileCompletion(),
        ]);

        const skills = skillsRes.status === 'fulfilled' ? skillsRes.value : [];
        const interests = interestsRes.status === 'fulfilled' ? interestsRes.value : [];
        const resumes = resumesRes.status === 'fulfilled' ? resumesRes.value : [];
        const completion =
          completionRes.status === 'fulfilled'
            ? completionRes.value.completion_percentage ?? completionRes.value.percentage ?? 40
            : 40;

        const skillsList = Array.isArray(skills) ? skills : skills.skills || [];
        const interestsList = Array.isArray(interests) ? interests : interests.interests || [];
        const resumesList = Array.isArray(resumes) ? resumes : resumes.resumes || [];

        setStats({
          skillsCount: skillsList.length,
          interestsCount: interestsList.length,
          resumesCount: resumesList.length,
          completionPercentage: completion,
        });

        // Try fetching notifications if available
        try {
          const notifRes = await api.get('/api/v1/notifications');
          const notifs = notifRes.data.notifications || notifRes.data || [];
          setNotifications(Array.isArray(notifs) ? notifs.slice(0, 4) : []);
        } catch {
          setNotifications([
            {
              id: '1',
              title: 'Welcome to CareerPilot AI!',
              message: 'Take your personality assessment to refine your career matches.',
              created_at: 'Just now',
              is_read: false,
            },
            {
              id: '2',
              title: 'Profile tip',
              message: 'Add at least 5 technical skills to unlock gap analysis.',
              created_at: '1 hour ago',
              is_read: false,
            },
          ]);
        }

        // Mock recent activity based on actual counts
        const activities = [];
        if (skillsList.length > 0) {
          activities.push({
            id: 'act-1',
            desc: `Added ${skillsList.length} skills to profile`,
            time: 'Recently',
            icon: WrenchScrewdriverIcon,
          });
        }
        if (resumesList.length > 0) {
          activities.push({
            id: 'act-2',
            desc: 'Uploaded new resume for parsing',
            time: 'Recently',
            icon: DocumentTextIcon,
          });
        }
        if (interestsList.length > 0) {
          activities.push({
            id: 'act-3',
            desc: `Selected ${interestsList.length} career interest categories`,
            time: 'Recently',
            icon: HeartIcon,
          });
        }
        if (activities.length === 0) {
          activities.push({
            id: 'act-0',
            desc: 'Account created and initialized',
            time: 'Today',
            icon: CheckCircleIcon,
          });
        }
        setRecentActivities(activities);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingSpinner text="Loading your career cockpit..." />;
  }

  const completionAngle = Math.min(100, stats.completionPercentage);
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (completionAngle / 100) * circumference;

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary-900 via-primary-800 to-secondary-900 text-white p-6 sm:p-8 shadow-md">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-medium text-primary-200">
              <SparklesIcon className="h-4 w-4 text-secondary-300" />
              <span>AI-Powered Career Intelligence</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
              Welcome back, {user?.full_name || user?.username || 'Explorer'}!
            </h1>
            <p className="text-primary-100 text-sm sm:text-base max-w-xl">
              Track your skill progression, update academic credentials, and prepare your pathway toward target roles.
            </p>
          </div>

          {/* Radial progress ring */}
          <div className="flex items-center space-x-4 bg-white/10 backdrop-blur-md p-4 rounded-xl border border-white/10">
            <div className="relative w-20 h-20 flex items-center justify-center">
              <svg className="w-20 h-20 transform -rotate-90">
                <circle
                  cx="40"
                  cy="40"
                  r={radius}
                  stroke="rgba(255, 255, 255, 0.2)"
                  strokeWidth="6"
                  fill="transparent"
                />
                <circle
                  cx="40"
                  cy="40"
                  r={radius}
                  stroke="#a855f7"
                  strokeWidth="6"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-700 ease-out"
                />
              </svg>
              <span className="absolute text-sm font-bold">{stats.completionPercentage}%</span>
            </div>
            <div>
              <p className="text-xs uppercase font-semibold text-primary-200 tracking-wider">
                Profile Readiness
              </p>
              <Link
                to="/profile"
                className="text-xs text-secondary-300 hover:text-white font-medium inline-flex items-center mt-1"
              >
                Complete profile <ArrowRightIcon className="h-3 w-3 ml-1" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Action Buttons */}
      <div className="flex flex-wrap items-center gap-3">
        <Link to="/profile">
          <Button variant="primary" size="md">
            Complete Profile
          </Button>
        </Link>
        <Link to="/resume">
          <Button variant="secondary" size="md">
            Upload Resume
          </Button>
        </Link>
        <Link to="/recommendations">
          <Button variant="outline" size="md">
            View Recommendations
          </Button>
        </Link>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <Card className="hover:border-primary-300 transition-all">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Skills Cataloged
              </p>
              <p className="text-3xl font-extrabold text-gray-900 mt-1">{stats.skillsCount}</p>
              <Link
                to="/profile/skills"
                className="text-xs font-semibold text-primary-700 hover:text-primary-900 inline-flex items-center mt-2"
              >
                Manage skills <ArrowRightIcon className="h-3 w-3 ml-1" />
              </Link>
            </div>
            <div className="p-3 bg-blue-50 rounded-xl text-primary-900">
              <WrenchScrewdriverIcon className="h-7 w-7" />
            </div>
          </div>
        </Card>

        <Card className="hover:border-secondary-300 transition-all">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Interests Set
              </p>
              <p className="text-3xl font-extrabold text-gray-900 mt-1">{stats.interestsCount}</p>
              <Link
                to="/profile/interests"
                className="text-xs font-semibold text-secondary-700 hover:text-secondary-900 inline-flex items-center mt-2"
              >
                Update interests <ArrowRightIcon className="h-3 w-3 ml-1" />
              </Link>
            </div>
            <div className="p-3 bg-purple-50 rounded-xl text-secondary-600">
              <HeartIcon className="h-7 w-7" />
            </div>
          </div>
        </Card>

        <Card className="hover:border-green-300 transition-all">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                Resumes Uploaded
              </p>
              <p className="text-3xl font-extrabold text-gray-900 mt-1">{stats.resumesCount}</p>
              <Link
                to="/resume"
                className="text-xs font-semibold text-green-700 hover:text-green-900 inline-flex items-center mt-2"
              >
                View documents <ArrowRightIcon className="h-3 w-3 ml-1" />
              </Link>
            </div>
            <div className="p-3 bg-green-50 rounded-xl text-green-600">
              <DocumentTextIcon className="h-7 w-7" />
            </div>
          </div>
        </Card>
      </div>

      {/* Two Column Layout: Recent Activity & Notifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card title="Recent Activity" subtitle="Your timeline of profile milestones">
          <div className="flow-root">
            <ul className="-mb-8">
              {recentActivities.map((activity, idx) => {
                const Icon = activity.icon;
                const isLast = idx === recentActivities.length - 1;
                return (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      {!isLast && (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      )}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-primary-100 text-primary-900 flex items-center justify-center ring-8 ring-white">
                            <Icon className="h-4 w-4" />
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{activity.desc}</p>
                          </div>
                          <div className="whitespace-nowrap text-right text-xs text-gray-500 flex items-center gap-1">
                            <ClockIcon className="h-3.5 w-3.5" />
                            {activity.time}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        </Card>

        {/* Notifications */}
        <Card
          title="Notifications"
          subtitle="Alerts & system recommendations"
          actions={
            <Badge variant="primary" size="sm">
              {notifications.filter((n) => !n.is_read).length} new
            </Badge>
          }
        >
          <div className="space-y-3">
            {notifications.length === 0 ? (
              <p className="text-sm text-gray-500 py-4 text-center">No notifications at this time.</p>
            ) : (
              notifications.map((notif) => (
                <div
                  key={notif.id}
                  className="p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors flex items-start gap-3"
                >
                  <div className="p-2 bg-amber-50 rounded-lg text-amber-600 mt-0.5">
                    <BellIcon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold text-gray-900">{notif.title}</p>
                      <span className="text-xs text-gray-400">{notif.created_at}</span>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{notif.message}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;
