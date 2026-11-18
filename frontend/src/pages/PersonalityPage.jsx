import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { getPersonality, addPersonality } from '../services/profile';
import { SparklesIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

const BIG_FIVE_QUESTIONS = [
  { id: 'q1', trait: 'Extraversion', text: 'I see myself as extraverted, enthusiastic, and socially outgoing.', reverse: false },
  { id: 'q2', trait: 'Agreeableness', text: 'I see myself as critical, quarrelsome, or quick to find fault.', reverse: true },
  { id: 'q3', trait: 'Conscientiousness', text: 'I see myself as dependable, self-disciplined, and organized.', reverse: false },
  { id: 'q4', trait: 'Neuroticism', text: 'I see myself as calm, emotionally stable, and resilient under stress.', reverse: true },
  { id: 'q5', trait: 'Openness', text: 'I see myself as open to new experiences, complex, and intellectually curious.', reverse: false },
  { id: 'q6', trait: 'Extraversion', text: 'I see myself as reserved, quiet, and reflective.', reverse: true },
  { id: 'q7', trait: 'Agreeableness', text: 'I see myself as sympathetic, warm, and cooperative.', reverse: false },
  { id: 'q8', trait: 'Conscientiousness', text: 'I see myself as disorganized, careless, or easily distracted.', reverse: true },
  { id: 'q9', trait: 'Neuroticism', text: 'I see myself as anxious, easily upset, or prone to worry.', reverse: false },
  { id: 'q10', trait: 'Openness', text: 'I see myself as conventional, routine-focused, or prefer familiar tasks.', reverse: true },
];

const LIKERT_OPTIONS = [
  { value: 1, label: 'Strongly Disagree' },
  { value: 2, label: 'Disagree' },
  { value: 3, label: 'Neutral' },
  { value: 4, label: 'Agree' },
  { value: 5, label: 'Strongly Agree' },
];

export const PersonalityPage = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [responses, setResponses] = useState({});
  const [oceanScores, setOceanScores] = useState({
    Openness: 7,
    Conscientiousness: 8,
    Extraversion: 6,
    Agreeableness: 8,
    Neuroticism: 4,
  });
  const [hasCompleted, setHasCompleted] = useState(false);

  useEffect(() => {
    const fetchExistingPersonality = async () => {
      try {
        const res = await getPersonality();
        const traits = Array.isArray(res) ? res : res.traits || [];
        if (traits.length >= 5) {
          const loaded = {};
          traits.forEach((t) => {
            const key = t.trait_name || t.name;
            if (key) loaded[key] = t.score;
          });
          setOceanScores((prev) => ({ ...prev, ...loaded }));
          setHasCompleted(true);
        }
      } catch (err) {
        console.error('Error fetching personality traits:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchExistingPersonality();
  }, []);

  const handleSelectOption = (questionId, value) => {
    setResponses((prev) => ({ ...prev, [questionId]: value }));
  };

  const calculateOceanScores = () => {
    const rawScores = {
      Openness: [],
      Conscientiousness: [],
      Extraversion: [],
      Agreeableness: [],
      Neuroticism: [],
    };

    BIG_FIVE_QUESTIONS.forEach((q) => {
      let val = responses[q.id] || 3;
      if (q.reverse) {
        val = 6 - val; // Reverse 1->5, 2->4, 3->3, 4->2, 5->1
      }
      rawScores[q.trait].push(val);
    });

    // Average and map 1..5 scale to 1..10 scale: score * 2
    const calculated = {};
    Object.keys(rawScores).forEach((trait) => {
      const vals = rawScores[trait];
      const avg = vals.reduce((a, b) => a + b, 0) / (vals.length || 1);
      calculated[trait] = Math.round(avg * 2 * 10) / 10;
    });

    return calculated;
  };

  const handleSubmitAssessment = async () => {
    // Check if all 10 are answered
    const unanswered = BIG_FIVE_QUESTIONS.filter((q) => !responses[q.id]);
    if (unanswered.length > 0) {
      toast.error(`Please answer all questions (${unanswered.length} remaining)`);
      return;
    }

    setSaving(true);
    const newScores = calculateOceanScores();
    setOceanScores(newScores);

    try {
      const payload = Object.entries(newScores).map(([trait, score]) => ({
        trait_name: trait,
        score: Number(score),
        assessment_type: 'BigFive_TIPI',
      }));

      await addPersonality(payload);
      setHasCompleted(true);
      toast.success('Personality profile assessed and saved successfully!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save personality scores');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading personality assessment..." />;
  }

  const radarData = [
    { trait: 'Openness', score: oceanScores.Openness || 5, fullMark: 10 },
    { trait: 'Conscientiousness', score: oceanScores.Conscientiousness || 5, fullMark: 10 },
    { trait: 'Extraversion', score: oceanScores.Extraversion || 5, fullMark: 10 },
    { trait: 'Agreeableness', score: oceanScores.Agreeableness || 5, fullMark: 10 },
    { trait: 'Emotional Stability', score: 10 - (oceanScores.Neuroticism || 5), fullMark: 10 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Big Five Personality Assessment</h1>
        <p className="text-sm text-gray-500 mt-1">
          Evaluate your OCEAN dimensions to uncover optimal working environments and cultural role fits.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Assessment Questionnaire Form */}
        <div className="lg:col-span-2 space-y-4">
          <Card
            title="Psychometric Questionnaire"
            subtitle="Rate how accurately each statement describes you (1 to 5)"
          >
            <div className="space-y-6">
              {BIG_FIVE_QUESTIONS.map((q, idx) => (
                <div key={q.id} className="p-4 bg-gray-50/70 rounded-xl border border-gray-100">
                  <p className="text-sm font-semibold text-gray-800">
                    {idx + 1}. {q.text}
                  </p>
                  <div className="grid grid-cols-5 gap-2 mt-3">
                    {LIKERT_OPTIONS.map((opt) => {
                      const isSelected = responses[q.id] === opt.value;
                      return (
                        <button
                          key={opt.value}
                          type="button"
                          onClick={() => handleSelectOption(q.id, opt.value)}
                          className={`py-2 px-1 text-center rounded-lg border text-xs font-medium transition-all ${
                            isSelected
                              ? 'bg-primary-900 text-white border-primary-900 shadow-sm'
                              : 'bg-white text-gray-700 border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="font-bold text-sm">{opt.value}</div>
                          <div className="hidden sm:block text-[10px] mt-0.5 truncate">{opt.label}</div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}

              <div className="flex justify-end pt-4 border-t border-gray-100">
                <Button
                  variant="primary"
                  onClick={handleSubmitAssessment}
                  isLoading={saving}
                  size="lg"
                >
                  Calculate & Save OCEAN Profile
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Results & Radar Chart Panel */}
        <div className="space-y-6">
          <Card title="OCEAN Radar Profile" subtitle="Scale: 1 (Lowest) to 10 (Highest)">
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis dataKey="trait" tick={{ fill: '#4b5563', fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 10]} stroke="#9ca3af" />
                  <Radar
                    name="Student Profile"
                    dataKey="score"
                    stroke="#1e3a8a"
                    fill="#3b82f6"
                    fillOpacity={0.45}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 space-y-2.5 pt-3 border-t border-gray-100">
              {Object.entries(oceanScores).map(([trait, score]) => (
                <div key={trait} className="flex justify-between items-center text-xs">
                  <span className="font-medium text-gray-700">{trait}</span>
                  <span className="font-bold text-primary-900 bg-primary-50 px-2 py-0.5 rounded">
                    {score} / 10
                  </span>
                </div>
              ))}
            </div>

            {hasCompleted && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2 text-xs text-green-800">
                <CheckCircleIcon className="h-4 w-4 text-success flex-shrink-0" />
                <span>Your OCEAN traits are synchronized with the recommendation engine.</span>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PersonalityPage;
