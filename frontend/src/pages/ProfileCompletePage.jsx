import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  getSkills,
  getInterests,
  getPersonality,
  getAcademics,
  getProfileCompletion,
} from '../services/profile';
import { getResumes } from '../services/resume';
import {
  CheckCircleIcon,
  SparklesIcon,
  ArrowRightIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';

export const ProfileCompletePage = () => {
  const [loading, setLoading] = useState(true);
  const [completionData, setCompletionData] = useState({
    percentage: 100,
    sections: {
      basic_info: true,
      skills: true,
      interests: true,
      personality: true,
      academics: true,
      resume: true,
    },
  });

  useEffect(() => {
    const checkChecklist = async () => {
      try {
        const [compRes, skillsRes, intRes, persRes, acadRes, resRes] =
          await Promise.allSettled([
            getProfileCompletion(),
            getSkills(),
            getInterests(),
            getPersonality(),
            getAcademics(),
            getResumes(),
          ]);

        const skills = skillsRes.status === 'fulfilled' ? (Array.isArray(skillsRes.value) ? skillsRes.value : skillsRes.value.skills || []) : [];
        const interests = intRes.status === 'fulfilled' ? (Array.isArray(intRes.value) ? intRes.value : intRes.value.interests || []) : [];
        const personality = persRes.status === 'fulfilled' ? (Array.isArray(persRes.value) ? persRes.value : persRes.value.traits || []) : [];
        const academics = acadRes.status === 'fulfilled' ? (Array.isArray(acadRes.value) ? acadRes.value : acadRes.value.records || []) : [];
        const resumes = resRes.status === 'fulfilled' ? (Array.isArray(resRes.value) ? resRes.value : resRes.value.resumes || []) : [];

        const hasSkills = skills.length > 0;
        const hasInterests = interests.length > 0;
        const hasPersonality = personality.length > 0;
        const hasAcademics = academics.length > 0;
        const hasResume = resumes.length > 0;

        const score = Math.round(
          ((1 + (hasSkills ? 1 : 0) + (hasInterests ? 1 : 0) + (hasPersonality ? 1 : 0) + (hasAcademics ? 1 : 0) + (hasResume ? 1 : 0)) / 6) * 100
        );

        setCompletionData({
          percentage: score,
          sections: {
            basic_info: true,
            skills: hasSkills,
            interests: hasInterests,
            personality: hasPersonality,
            academics: hasAcademics,
            resume: hasResume,
          },
        });
      } catch (err) {
        console.error('Error fetching completion details:', err);
      } finally {
        setLoading(false);
      }
    };

    checkChecklist();
  }, []);

  if (loading) {
    return <LoadingSpinner text="Calculating profile verification..." />;
  }

  const checklistItems = [
    { key: 'basic_info', label: 'Basic Contact & Personal Info', path: '/profile' },
    { key: 'skills', label: 'Technical & Soft Skills Portfolio', path: '/profile/skills' },
    { key: 'interests', label: 'Career Interests & Domain Categories', path: '/profile/interests' },
    { key: 'personality', label: 'Big Five (OCEAN) Psychometric Assessment', path: '/profile/personality' },
    { key: 'academics', label: 'Academic Qualifications & GPA Records', path: '/profile/academics' },
    { key: 'resume', label: 'Parsed Resume / CV Document', path: '/resume' },
  ];

  const allCompleted = completionData.percentage >= 80;

  return (
    <div className="relative max-w-3xl mx-auto space-y-8 py-6">
      {/* CSS Confetti elements when profile is largely complete */}
      {allCompleted && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
          <div className="animate-confetti absolute top-0 left-[15%] w-3 h-5 bg-blue-500 rounded-sm" />
          <div className="animate-confetti absolute top-0 left-[35%] w-3 h-4 bg-purple-500 rounded-sm" style={{ animationDelay: '0.8s' }} />
          <div className="animate-confetti absolute top-0 left-[55%] w-4 h-4 bg-amber-400 rounded-full" style={{ animationDelay: '1.5s' }} />
          <div className="animate-confetti absolute top-0 left-[75%] w-3 h-5 bg-green-500 rounded-sm" style={{ animationDelay: '0.3s' }} />
          <div className="animate-confetti absolute top-0 left-[85%] w-4 h-3 bg-pink-500 rounded-sm" style={{ animationDelay: '2.1s' }} />
        </div>
      )}

      {/* Hero Celebratory Card */}
      <Card className="text-center p-8 bg-gradient-to-b from-white to-primary-50/40 relative z-10 border-primary-200">
        <div className="inline-flex h-16 w-16 rounded-2xl bg-gradient-to-tr from-primary-900 to-secondary-600 items-center justify-center text-white shadow-xl mb-4">
          <SparklesIcon className="h-9 w-9" />
        </div>
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
          {allCompleted ? 'Profile Readied for Navigation!' : 'Your Pathway Progress'}
        </h1>
        <p className="mt-2 text-base text-gray-600 max-w-lg mx-auto">
          {allCompleted
            ? 'Awesome job! You have satisfied the core prerequisites for AI skill-gap analysis and pathway generation.'
            : `Your profile is ${completionData.percentage}% complete. Finish the remaining items below to maximize recommendation precision.`}
        </p>

        <div className="mt-6 flex justify-center gap-4">
          <Link to="/recommendations">
            <Button variant="primary" size="lg" icon={ArrowRightIcon}>
              View Recommendations
            </Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="outline" size="lg">
              Return to Dashboard
            </Button>
          </Link>
        </div>
      </Card>

      {/* Checklist Overview */}
      <Card title="Prerequisite Checklist" subtitle="Comprehensive status of your profile pillars" className="relative z-10">
        <div className="divide-y divide-gray-100">
          {checklistItems.map((item) => {
            const isDone = completionData.sections[item.key];
            return (
              <div
                key={item.key}
                className="py-3.5 flex items-center justify-between hover:bg-gray-50/50 px-2 rounded-lg transition-colors"
              >
                <div className="flex items-center space-x-3">
                  {isDone ? (
                    <CheckCircleIcon className="h-6 w-6 text-success flex-shrink-0" />
                  ) : (
                    <ExclamationCircleIcon className="h-6 w-6 text-warning flex-shrink-0" />
                  )}
                  <span
                    className={`text-sm font-medium ${
                      isDone ? 'text-gray-900' : 'text-gray-600'
                    }`}
                  >
                    {item.label}
                  </span>
                </div>

                <div>
                  {isDone ? (
                    <span className="text-xs font-semibold text-green-700 bg-green-50 px-2.5 py-1 rounded-full">
                      Completed
                    </span>
                  ) : (
                    <Link to={item.path}>
                      <span className="text-xs font-semibold text-primary-700 bg-primary-50 hover:bg-primary-100 px-2.5 py-1 rounded-full transition-colors">
                        Add Now →
                      </span>
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};

export default ProfileCompletePage;
