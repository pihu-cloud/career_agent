import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import ProgressBar from '../components/ui/ProgressBar';
import { updateProfile, addSkills, addInterests } from '../services/profile';
import { uploadResume } from '../services/resume';
import {
  SparklesIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  DocumentArrowUpIcon,
} from '@heroicons/react/24/outline';

const STEPS = [
  { id: 1, name: 'Welcome', title: 'Welcome to CareerPilot AI' },
  { id: 2, name: 'Profile', title: 'Basic Identity Setup' },
  { id: 3, name: 'Skills', title: 'Key Competencies' },
  { id: 4, name: 'Interests', title: 'Domains of Passion' },
  { id: 5, name: 'Resume', title: 'Resume Attachment' },
];

export const OnboardingPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Form states across steps
  const [basicInfo, setBasicInfo] = useState({
    bio: '',
    phone: '',
    location: '',
  });

  const [skillInput, setSkillInput] = useState({
    skill_name: '',
    proficiency_level: 3,
    skill_type: 'technical',
    years_experience: 1,
  });
  const [skillsList, setSkillsList] = useState([]);

  const [interestInput, setInterestInput] = useState({
    category: 'Technology & Software',
    interest_name: '',
    strength: 8,
  });
  const [interestsList, setInterestsList] = useState([]);

  const [resumeFile, setResumeFile] = useState(null);

  const handleNext = async () => {
    setLoading(true);
    try {
      if (currentStep === 2) {
        if (basicInfo.bio || basicInfo.phone || basicInfo.location) {
          await updateProfile(basicInfo);
        }
      } else if (currentStep === 3) {
        if (skillsList.length > 0) {
          await addSkills(skillsList);
        }
      } else if (currentStep === 4) {
        if (interestsList.length > 0) {
          await addInterests(interestsList);
        }
      } else if (currentStep === 5) {
        if (resumeFile) {
          await uploadResume(resumeFile);
        }
        toast.success('Onboarding complete! Welcome aboard.');
        navigate('/dashboard');
        return;
      }
      setCurrentStep((prev) => Math.min(STEPS.length, prev + 1));
    } catch (err) {
      toast.error('Could not save step data, proceeding...');
      setCurrentStep((prev) => Math.min(STEPS.length, prev + 1));
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(1, prev - 1));
  };

  const addSkillToQueue = () => {
    if (!skillInput.skill_name.trim()) return;
    setSkillsList((prev) => [...prev, { ...skillInput, skill_name: skillInput.skill_name.trim() }]);
    setSkillInput({ ...skillInput, skill_name: '' });
  };

  const addInterestToQueue = () => {
    if (!interestInput.interest_name.trim()) return;
    setInterestsList((prev) => [
      ...prev,
      { ...interestInput, interest_name: interestInput.interest_name.trim() },
    ]);
    setInterestInput({ ...interestInput, interest_name: '' });
  };

  const progressPercent = ((currentStep - 1) / (STEPS.length - 1)) * 100;

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8 flex flex-col justify-center">
      <div className="max-w-2xl mx-auto w-full space-y-6">
        {/* Top Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-primary-900 flex items-center justify-center text-white">
              <SparklesIcon className="h-5 w-5" />
            </div>
            <span className="font-bold text-gray-900 text-lg">CareerPilot AI Onboarding</span>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-xs font-semibold text-gray-500 hover:text-gray-900"
          >
            Skip to Dashboard →
          </button>
        </div>

        {/* Step Indicator */}
        <div className="space-y-2">
          <ProgressBar progress={progressPercent} color="primary" size="sm" showPercentage={false} />
          <div className="flex justify-between text-xs font-medium text-gray-500">
            {STEPS.map((s) => (
              <span
                key={s.id}
                className={s.id === currentStep ? 'font-bold text-primary-900' : ''}
              >
                {s.name}
              </span>
            ))}
          </div>
        </div>

        {/* Step Card */}
        <Card className="p-6 sm:p-8 shadow-md">
          {/* Step 1: Welcome */}
          {currentStep === 1 && (
            <div className="text-center space-y-4 py-4">
              <div className="mx-auto h-16 w-16 bg-blue-50 text-primary-900 rounded-2xl flex items-center justify-center">
                <SparklesIcon className="h-8 w-8" />
              </div>
              <h2 className="text-2xl font-extrabold text-gray-900">
                Welcome to CareerPilot AI
              </h2>
              <p className="text-sm text-gray-600 max-w-md mx-auto leading-relaxed">
                Our autonomous career pathway agent uses your unique skills, psychometric personality
                traits, and academic records to compute real-time skill gaps and guide you to top career matches.
              </p>
              <div className="p-4 bg-gray-50 rounded-xl text-left text-xs text-gray-700 space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-success" />
                  <span>Personalized skill-gap analysis against live job market demand</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-success" />
                  <span>Adaptive learning roadmap recommendations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircleIcon className="h-4 w-4 text-success" />
                  <span>Continuous milestones and progress tracking</span>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Basic Info */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-900">Step 2: Tell Us About Yourself</h2>
              <p className="text-sm text-gray-500">
                Provide a brief summary and your current location.
              </p>
              <Input
                label="Location (City, Country)"
                placeholder="San Francisco, CA or London, UK"
                value={basicInfo.location}
                onChange={(e) => setBasicInfo({ ...basicInfo, location: e.target.value })}
              />
              <Input
                label="Phone Number"
                placeholder="+1 (555) 000-0000"
                value={basicInfo.phone}
                onChange={(e) => setBasicInfo({ ...basicInfo, phone: e.target.value })}
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Short Career Objective / Bio
                </label>
                <textarea
                  rows={3}
                  className="w-full rounded-md border border-gray-300 p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
                  placeholder="Aspiring Software Engineer interested in distributed systems and AI applications..."
                  value={basicInfo.bio}
                  onChange={(e) => setBasicInfo({ ...basicInfo, bio: e.target.value })}
                />
              </div>
            </div>
          )}

          {/* Step 3: Add Skills */}
          {currentStep === 3 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-900">Step 3: What Skills Do You Have?</h2>
              <p className="text-sm text-gray-500">
                Add at least 2 or 3 skills to get started. You can add more anytime later.
              </p>

              <div className="flex gap-2">
                <Input
                  placeholder="e.g. Python, SQL, React"
                  value={skillInput.skill_name}
                  onChange={(e) => setSkillInput({ ...skillInput, skill_name: e.target.value })}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkillToQueue())}
                />
                <Button variant="primary" onClick={addSkillToQueue}>
                  Add
                </Button>
              </div>

              {skillsList.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {skillsList.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-primary-50 text-primary-900 border border-primary-200 rounded-full text-xs font-semibold flex items-center gap-1.5"
                    >
                      {s.skill_name}
                      <button
                        onClick={() => setSkillsList(skillsList.filter((_, i) => i !== idx))}
                        className="text-primary-700 hover:text-danger"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 4: Interests */}
          {currentStep === 4 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-900">Step 4: Your Target Interests</h2>
              <p className="text-sm text-gray-500">
                What domains or fields excite you the most?
              </p>

              <div className="flex gap-2">
                <Input
                  placeholder="e.g. Machine Learning, Cloud Architecture, Cyber Security"
                  value={interestInput.interest_name}
                  onChange={(e) =>
                    setInterestInput({ ...interestInput, interest_name: e.target.value })
                  }
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addInterestToQueue())}
                />
                <Button variant="secondary" onClick={addInterestToQueue}>
                  Add
                </Button>
              </div>

              {interestsList.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {interestsList.map((item, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-purple-50 text-secondary-700 border border-purple-200 rounded-full text-xs font-semibold flex items-center gap-1.5"
                    >
                      {item.interest_name}
                      <button
                        onClick={() => setInterestsList(interestsList.filter((_, i) => i !== idx))}
                        className="text-purple-700 hover:text-danger"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 5: Resume */}
          {currentStep === 5 && (
            <div className="space-y-4 text-center">
              <h2 className="text-xl font-bold text-gray-900">Step 5: Attach Your Resume (Optional)</h2>
              <p className="text-sm text-gray-500">
                You can upload your PDF or DOCX file now for automated parser extraction.
              </p>

              <label className="border-2 border-dashed border-gray-300 hover:border-primary-600 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors bg-gray-50">
                <DocumentArrowUpIcon className="h-10 w-10 text-primary-900 mb-2" />
                <span className="text-sm font-semibold text-gray-800">
                  {resumeFile ? resumeFile.name : 'Choose PDF / DOCX file'}
                </span>
                <span className="text-xs text-gray-400 mt-1">Up to 10MB</span>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc"
                  className="hidden"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                />
              </label>
            </div>
          )}

          {/* Navigation Controls */}
          <div className="flex justify-between items-center pt-6 mt-6 border-t border-gray-100">
            {currentStep > 1 ? (
              <Button variant="outline" icon={ArrowLeftIcon} onClick={handleBack}>
                Back
              </Button>
            ) : (
              <div />
            )}

            <Button
              variant="primary"
              onClick={handleNext}
              isLoading={loading}
              icon={currentStep === 5 ? undefined : ArrowRightIcon}
            >
              {currentStep === 5 ? 'Finish & Launch Dashboard' : 'Next Step'}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default OnboardingPage;
