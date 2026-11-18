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
  getSkills,
  addSkills,
  updateSkill,
  deleteSkill,
} from '../services/profile';
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  WrenchScrewdriverIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';

const PROFICIENCY_LABELS = {
  1: 'Novice / Beginner (1)',
  2: 'Intermediate (2)',
  3: 'Competent (3)',
  4: 'Proficient / Advanced (4)',
  5: 'Expert / Master (5)',
};

export const SkillsPage = () => {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all'); // all | technical | soft
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState(null);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { isSubmitting },
  } = useForm({
    defaultValues: {
      skill_name: '',
      proficiency_level: 3,
      skill_type: 'technical',
      years_experience: 1,
    },
  });

  const proficiencyLevel = watch('proficiency_level', 3);

  const fetchSkillsList = async () => {
    try {
      const data = await getSkills();
      const list = Array.isArray(data) ? data : data.skills || [];
      setSkills(list);
    } catch (err) {
      console.error('Error fetching skills:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkillsList();
  }, []);

  const openAddModal = () => {
    setEditingSkill(null);
    reset({
      skill_name: '',
      proficiency_level: 3,
      skill_type: 'technical',
      years_experience: 1,
    });
    setIsModalOpen(true);
  };

  const openEditModal = (skill) => {
    setEditingSkill(skill);
    reset({
      skill_name: skill.skill_name,
      proficiency_level: skill.proficiency_level || 3,
      skill_type: skill.skill_type || 'technical',
      years_experience: skill.years_experience || 1,
    });
    setIsModalOpen(true);
  };

  const onSubmit = async (data) => {
    try {
      const payload = {
        skill_name: data.skill_name.trim(),
        proficiency_level: Number(data.proficiency_level),
        skill_type: data.skill_type,
        years_experience: Number(data.years_experience),
      };

      if (editingSkill) {
        await updateSkill(editingSkill.id, payload);
        toast.success(`Skill "${payload.skill_name}" updated`);
      } else {
        // Backend addSkills accepts array or single
        await addSkills([payload]);
        toast.success(`Skill "${payload.skill_name}" added`);
      }
      setIsModalOpen(false);
      fetchSkillsList();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save skill');
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"?`)) return;
    try {
      await deleteSkill(id);
      toast.success(`Deleted ${name}`);
      setSkills((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete skill');
    }
  };

  const filteredSkills = skills.filter((s) => {
    if (filterType === 'all') return true;
    return s.skill_type === filterType;
  });

  const technicalCount = skills.filter((s) => s.skill_type === 'technical').length;
  const softCount = skills.filter((s) => s.skill_type === 'soft').length;

  if (loading) {
    return <LoadingSpinner text="Retrieving skills catalog..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Skills Portfolio</h1>
          <p className="text-sm text-gray-500 mt-1">
            Catalog your technical capabilities and soft skills for accurate pathway gap analysis.
          </p>
        </div>
        <Button variant="primary" icon={PlusIcon} onClick={openAddModal}>
          Add New Skill
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 border-b border-gray-200 pb-3">
        <button
          onClick={() => setFilterType('all')}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            filterType === 'all'
              ? 'bg-primary-900 text-white'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          All Skills ({skills.length})
        </button>
        <button
          onClick={() => setFilterType('technical')}
          className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            filterType === 'technical'
              ? 'bg-primary-900 text-white'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <WrenchScrewdriverIcon className="h-4 w-4 mr-1.5" />
          Technical ({technicalCount})
        </button>
        <button
          onClick={() => setFilterType('soft')}
          className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            filterType === 'soft'
              ? 'bg-primary-900 text-white'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <UserGroupIcon className="h-4 w-4 mr-1.5" />
          Soft Skills ({softCount})
        </button>
      </div>

      {/* Skills Grid */}
      {filteredSkills.length === 0 ? (
        <Card className="text-center py-12">
          <WrenchScrewdriverIcon className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-2 text-base font-semibold text-gray-900">No skills added yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by adding your programming languages, frameworks, or leadership skills.
          </p>
          <div className="mt-6">
            <Button variant="primary" icon={PlusIcon} onClick={openAddModal}>
              Add First Skill
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((skill) => (
            <Card key={skill.id} className="p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 text-base">{skill.skill_name}</h3>
                    <Badge
                      variant={skill.skill_type === 'technical' ? 'primary' : 'secondary'}
                      size="sm"
                    >
                      {skill.skill_type}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {skill.years_experience || 0} {skill.years_experience === 1 ? 'yr' : 'yrs'} experience
                  </p>
                </div>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => openEditModal(skill)}
                    className="p-1.5 text-gray-400 hover:text-primary-700 hover:bg-gray-100 rounded-md transition-colors"
                    title="Edit"
                  >
                    <PencilSquareIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(skill.id, skill.skill_name)}
                    className="p-1.5 text-gray-400 hover:text-danger hover:bg-red-50 rounded-md transition-colors"
                    title="Delete"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Proficiency Level Indicator */}
              <div className="mt-4 pt-3 border-t border-gray-100">
                <div className="flex justify-between items-center text-xs mb-1">
                  <span className="text-gray-500 font-medium">Proficiency:</span>
                  <span className="font-semibold text-primary-900">
                    Level {skill.proficiency_level} / 5
                  </span>
                </div>
                <div className="grid grid-cols-5 gap-1 h-2">
                  {[1, 2, 3, 4, 5].map((lvl) => (
                    <div
                      key={lvl}
                      className={`rounded-sm transition-colors ${
                        lvl <= (skill.proficiency_level || 1)
                          ? 'bg-primary-700'
                          : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Add / Edit Skill Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingSkill ? 'Edit Skill Record' : 'Add New Skill'}
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Skill Name"
            placeholder="e.g., Python, React, Project Management"
            required
            {...register('skill_name', { required: true })}
          />

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Skill Classification
              </label>
              <select
                {...register('skill_type')}
                className="block w-full rounded-md border border-gray-300 text-sm px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600"
              >
                <option value="technical">Technical Skill</option>
                <option value="soft">Soft / Interpersonal Skill</option>
              </select>
            </div>

            <Input
              label="Years of Experience"
              type="number"
              min="0"
              max="50"
              step="0.5"
              required
              {...register('years_experience', { required: true, valueAsNumber: true })}
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-sm font-medium text-gray-700">
                Proficiency Level (1 to 5)
              </label>
              <span className="text-xs font-semibold text-primary-900">
                {PROFICIENCY_LABELS[proficiencyLevel] || `${proficiencyLevel}/5`}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-900"
              {...register('proficiency_level', { valueAsNumber: true })}
            />
            <div className="flex justify-between text-[11px] text-gray-400 mt-1">
              <span>Novice</span>
              <span>Intermediate</span>
              <span>Competent</span>
              <span>Proficient</span>
              <span>Expert</span>
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
            <Button type="submit" variant="primary" isLoading={isSubmitting}>
              {editingSkill ? 'Save Changes' : 'Add Skill'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default SkillsPage;
