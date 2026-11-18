import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  getInterests,
  addInterests,
  deleteInterest,
} from '../services/profile';
import {
  PlusIcon,
  TrashIcon,
  HeartIcon,
  TagIcon,
} from '@heroicons/react/24/outline';

const PREDEFINED_CATEGORIES = [
  'Technology & Software',
  'Artificial Intelligence & Data',
  'Business & Management',
  'Design & Creative Media',
  'Healthcare & Medicine',
  'Finance & FinTech',
  'Science & Research',
  'Education & Training',
  'Marketing & Sales',
  'Engineering & Hardware',
];

export const InterestsPage = () => {
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { isSubmitting },
  } = useForm({
    defaultValues: {
      category: PREDEFINED_CATEGORIES[0],
      interest_name: '',
      strength: 7,
    },
  });

  const strengthVal = watch('strength', 7);

  const fetchInterestsList = async () => {
    try {
      const data = await getInterests();
      const list = Array.isArray(data) ? data : data.interests || [];
      setInterests(list);
    } catch (err) {
      console.error('Error fetching interests:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInterestsList();
  }, []);

  const openAddModal = () => {
    reset({
      category: PREDEFINED_CATEGORIES[0],
      interest_name: '',
      strength: 7,
    });
    setIsModalOpen(true);
  };

  const onSubmit = async (data) => {
    try {
      const payload = {
        category: data.category,
        interest_name: data.interest_name.trim(),
        strength: Number(data.strength),
      };
      await addInterests([payload]);
      toast.success(`Interest "${payload.interest_name}" saved!`);
      setIsModalOpen(false);
      fetchInterestsList();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save interest');
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Remove interest "${name}"?`)) return;
    try {
      await deleteInterest(id);
      toast.success(`Removed ${name}`);
      setInterests((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete interest');
    }
  };

  // Group interests by category
  const groupedInterests = interests.reduce((acc, item) => {
    const cat = item.category || 'General';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {});

  if (loading) {
    return <LoadingSpinner text="Loading career interests..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Career Interests & Passions</h1>
          <p className="text-sm text-gray-500 mt-1">
            Specify the fields and sectors that excite you most to influence intelligent pathway scoring.
          </p>
        </div>
        <Button variant="primary" icon={PlusIcon} onClick={openAddModal}>
          Add Interest
        </Button>
      </div>

      {interests.length === 0 ? (
        <Card className="text-center py-12">
          <HeartIcon className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-2 text-base font-semibold text-gray-900">No interests selected</h3>
          <p className="mt-1 text-sm text-gray-500">
            Select domains like Machine Learning, Cloud Architecture, or UI/UX Design.
          </p>
          <div className="mt-6">
            <Button variant="primary" icon={PlusIcon} onClick={openAddModal}>
              Add First Interest
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedInterests).map(([category, items]) => (
            <div key={category} className="space-y-3">
              <div className="flex items-center space-x-2">
                <TagIcon className="h-5 w-5 text-secondary-600" />
                <h2 className="text-lg font-bold text-gray-800">{category}</h2>
                <Badge variant="secondary" size="sm">
                  {items.length}
                </Badge>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {items.map((item) => (
                  <Card key={item.id} className="p-4 hover:border-secondary-300 transition-all">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0 pr-2">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {item.interest_name}
                        </h3>
                        <p className="text-xs text-gray-500 mt-0.5">Strength Rating: {item.strength || 5}/10</p>
                      </div>
                      <button
                        onClick={() => handleDelete(item.id, item.interest_name)}
                        className="text-gray-400 hover:text-danger p-1 rounded hover:bg-red-50 transition-colors"
                        title="Delete"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>

                    {/* Strength indicator */}
                    <div className="mt-3">
                      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-secondary-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${((item.strength || 5) / 10) * 100}%` }}
                        />
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Interest Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add Career Interest"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category / Industry Domain
            </label>
            <select
              {...register('category')}
              className="block w-full rounded-md border border-gray-300 text-sm px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-secondary-500/20 focus:border-secondary-600"
            >
              {PREDEFINED_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Specific Interest or Domain Focus"
            placeholder="e.g., Computer Vision, Distributed Systems, Product Strategy"
            required
            {...register('interest_name', { required: true })}
          />

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-sm font-medium text-gray-700">
                Interest Strength (1 to 10)
              </label>
              <span className="text-xs font-semibold text-secondary-700">
                Level {strengthVal} / 10
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-secondary-600"
              {...register('strength', { valueAsNumber: true })}
            />
            <div className="flex justify-between text-[11px] text-gray-400 mt-1">
              <span>Mild Interest (1)</span>
              <span>Moderate (5)</span>
              <span>Core Passion (10)</span>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="secondary" isLoading={isSubmitting}>
              Add Interest
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default InterestsPage;
