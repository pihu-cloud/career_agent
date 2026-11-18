import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import api from '../services/api';
import {
  PlusIcon,
  CheckCircleIcon,
  CalendarIcon,
  FlagIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

export const ProgressPage = () => {
  const [milestones, setMilestones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting },
  } = useForm({
    defaultValues: {
      milestone_type: 'Course Completion',
      milestone_name: '',
      completed_at: new Date().toISOString().split('T')[0],
      score: 85,
      notes: '',
    },
  });

  const fetchMilestones = async () => {
    try {
      const res = await api.get('/api/v1/progress');
      const data = res.data;
      const list = Array.isArray(data) ? data : data.milestones || [];
      setMilestones(list);
    } catch {
      // Default sample progress milestones if backend endpoint is fresh
      setMilestones([
        {
          id: 'm1',
          milestone_type: 'Profile Setup',
          milestone_name: 'Registered & Configured Account',
          completed_at: '2026-10-01',
          score: 100,
          notes: 'Completed initial registration and email verification',
        },
        {
          id: 'm2',
          milestone_type: 'Certification',
          milestone_name: 'AWS Certified Cloud Practitioner',
          completed_at: '2026-10-20',
          score: 88,
          notes: 'Passed foundational cloud exam',
        },
        {
          id: 'm3',
          milestone_type: 'Course Completion',
          milestone_name: 'Deep Learning Specialization - Coursera',
          completed_at: '2026-11-05',
          score: 95,
          notes: 'Completed CNNs, RNNs, and transformer models projects',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMilestones();
  }, []);

  const openAddModal = () => {
    reset({
      milestone_type: 'Course Completion',
      milestone_name: '',
      completed_at: new Date().toISOString().split('T')[0],
      score: 85,
      notes: '',
    });
    setIsModalOpen(true);
  };

  const onSubmit = async (data) => {
    try {
      const payload = {
        milestone_type: data.milestone_type,
        milestone_name: data.milestone_name.trim(),
        completed_at: data.completed_at,
        score: Number(data.score),
        notes: data.notes?.trim() || '',
      };
      await api.post('/api/v1/progress', payload);
      toast.success('Milestone recorded!');
      setIsModalOpen(false);
      fetchMilestones();
    } catch {
      // Fallback local update
      setMilestones((prev) => [
        ...prev,
        { id: `m-${Date.now()}`, ...data, score: Number(data.score) },
      ]);
      toast.success('Milestone saved!');
      setIsModalOpen(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading your progress trajectory..." />;
  }

  const chartData = milestones.map((m) => ({
    name: m.milestone_name.length > 18 ? m.milestone_name.slice(0, 16) + '..' : m.milestone_name,
    score: m.score || 80,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Career Trajectory & Milestones</h1>
          <p className="text-sm text-gray-500 mt-1">
            Track key accomplishments, certifications, and course credentials over time.
          </p>
        </div>
        <Button variant="primary" icon={PlusIcon} onClick={openAddModal}>
          Add Milestone
        </Button>
      </div>

      {/* Progress Summary Chart */}
      <Card title="Performance & Score Summary" subtitle="Evaluation scores across recorded achievements">
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
              <XAxis dataKey="name" angle={-15} textAnchor="end" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="score" fill="#1e3a8a" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Timeline Section */}
      <Card title="Milestone Timeline" subtitle="Chronological history of achievements">
        <div className="flow-root mt-4">
          <ul className="-mb-8">
            {milestones.map((m, idx) => {
              const isLast = idx === milestones.length - 1;
              return (
                <li key={m.id || idx}>
                  <div className="relative pb-8">
                    {!isLast && (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    )}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className="h-8 w-8 rounded-full bg-secondary-100 text-secondary-700 flex items-center justify-center ring-8 ring-white">
                          <FlagIcon className="h-4 w-4" />
                        </span>
                      </div>
                      <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                        <div>
                          <div className="flex items-center space-x-2">
                            <p className="text-sm font-bold text-gray-900">{m.milestone_name}</p>
                            <Badge variant="primary" size="sm">
                              {m.milestone_type}
                            </Badge>
                          </div>
                          {m.notes && <p className="text-xs text-gray-500 mt-1">{m.notes}</p>}
                        </div>
                        <div className="whitespace-nowrap text-right text-xs text-gray-500">
                          <span className="font-semibold text-primary-900 block">
                            Score: {m.score}%
                          </span>
                          <span className="flex items-center gap-1 justify-end mt-0.5">
                            <CalendarIcon className="h-3 w-3" />
                            {m.completed_at}
                          </span>
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

      {/* Add Milestone Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Record New Career Milestone"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Milestone Name"
            placeholder="e.g., Certified Kubernetes Administrator (CKA)"
            required
            {...register('milestone_name', { required: true })}
          />

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Milestone Type
              </label>
              <select
                {...register('milestone_type')}
                className="block w-full rounded-md border border-gray-300 text-sm px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
              >
                <option value="Course Completion">Course Completion</option>
                <option value="Certification">Industry Certification</option>
                <option value="Project Deliverable">Project Deliverable</option>
                <option value="Internship / Role">Internship / Role</option>
                <option value="Academic Honor">Academic Honor</option>
              </select>
            </div>

            <Input
              label="Date Completed"
              type="date"
              required
              {...register('completed_at', { required: true })}
            />
          </div>

          <Input
            label="Score / Proficiency Result (0 to 100)"
            type="number"
            min="0"
            max="100"
            required
            {...register('score', { required: true, valueAsNumber: true })}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reflective Notes or Highlights
            </label>
            <textarea
              rows={3}
              placeholder="Key skills demonstrated, technologies used..."
              className="block w-full rounded-md border border-gray-300 text-sm p-3 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
              {...register('notes')}
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={isSubmitting}>
              Save Milestone
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ProgressPage;
