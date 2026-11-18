import React, { useState, useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  getAcademics,
  addAcademic,
  updateAcademic,
  deleteAcademic,
} from '../services/profile';
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  AcademicCapIcon,
  ArrowUpTrayIcon,
} from '@heroicons/react/24/outline';

export const AcademicsPage = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const csvInputRef = useRef(null);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { isSubmitting },
  } = useForm({
    defaultValues: {
      institution: '',
      degree: "Bachelor's",
      field_of_study: '',
      cgpa: 3.5,
      start_year: 2021,
      end_year: 2025,
      is_current: false,
    },
  });

  const isCurrent = watch('is_current', false);

  const fetchRecords = async () => {
    try {
      const data = await getAcademics();
      const list = Array.isArray(data) ? data : data.records || [];
      setRecords(list);
    } catch (err) {
      console.error('Error fetching academic history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const openAddModal = () => {
    setEditingRecord(null);
    reset({
      institution: '',
      degree: "Bachelor's",
      field_of_study: '',
      cgpa: 3.5,
      start_year: new Date().getFullYear() - 3,
      end_year: new Date().getFullYear() + 1,
      is_current: false,
    });
    setIsModalOpen(true);
  };

  const openEditModal = (rec) => {
    setEditingRecord(rec);
    reset({
      institution: rec.institution,
      degree: rec.degree,
      field_of_study: rec.field_of_study,
      cgpa: rec.cgpa,
      start_year: rec.start_year,
      end_year: rec.end_year || new Date().getFullYear(),
      is_current: rec.is_current,
    });
    setIsModalOpen(true);
  };

  const onSubmit = async (data) => {
    try {
      const payload = {
        institution: data.institution.trim(),
        degree: data.degree.trim(),
        field_of_study: data.field_of_study.trim(),
        cgpa: Number(data.cgpa),
        start_year: Number(data.start_year),
        end_year: data.is_current ? null : Number(data.end_year),
        is_current: Boolean(data.is_current),
      };

      if (editingRecord) {
        await updateAcademic(editingRecord.id, payload);
        toast.success('Academic record updated');
      } else {
        await addAcademic(payload);
        toast.success('Academic record added');
      }
      setIsModalOpen(false);
      fetchRecords();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save academic record');
    }
  };

  const handleDelete = async (id, degree, institution) => {
    if (!window.confirm(`Delete record for ${degree} at ${institution}?`)) return;
    try {
      await deleteAcademic(id);
      toast.success('Record deleted');
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete record');
    }
  };

  // CSV Import parser
  const handleCsvUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const text = event.target?.result;
        if (typeof text !== 'string') return;

        const lines = text.split('\n').map((l) => l.trim()).filter(Boolean);
        if (lines.length <= 1) {
          toast.error('CSV appears empty or has only headers');
          return;
        }

        // Expected format: institution,degree,field_of_study,cgpa,start_year,end_year
        const imported = [];
        for (let i = 1; i < lines.length; i++) {
          const parts = lines[i].split(',').map((p) => p.trim());
          if (parts.length >= 4) {
            imported.push({
              institution: parts[0],
              degree: parts[1],
              field_of_study: parts[2],
              cgpa: parseFloat(parts[3]) || 3.0,
              start_year: parseInt(parts[4]) || 2020,
              end_year: parts[5] ? parseInt(parts[5]) : null,
              is_current: !parts[5],
            });
          }
        }

        for (const item of imported) {
          await addAcademic(item);
        }

        toast.success(`Imported ${imported.length} academic record(s) from CSV!`);
        fetchRecords();
      } catch (err) {
        console.error('CSV parse error:', err);
        toast.error('Failed to parse CSV file. Ensure columns match.');
      }
    };
    reader.readAsText(file);
    if (csvInputRef.current) csvInputRef.current.value = '';
  };

  if (loading) {
    return <LoadingSpinner text="Retrieving academic records..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Academic Background</h1>
          <p className="text-sm text-gray-500 mt-1">
            Maintain your university degrees, GPA, and graduation timelines.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <input
            type="file"
            ref={csvInputRef}
            accept=".csv"
            onChange={handleCsvUpload}
            className="hidden"
          />
          <Button
            variant="outline"
            icon={ArrowUpTrayIcon}
            onClick={() => csvInputRef.current?.click()}
          >
            Import CSV
          </Button>
          <Button variant="primary" icon={PlusIcon} onClick={openAddModal}>
            Add Degree / Record
          </Button>
        </div>
      </div>

      {records.length === 0 ? (
        <Card className="text-center py-12">
          <AcademicCapIcon className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-2 text-base font-semibold text-gray-900">No academic records found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add your undergraduate, graduate, or certification degrees.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <Button variant="primary" icon={PlusIcon} onClick={openAddModal}>
              Add First Degree
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {records.map((rec) => (
            <Card key={rec.id} className="p-5 hover:border-primary-300 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-gray-900 text-base">{rec.degree}</h3>
                    {rec.is_current && (
                      <Badge variant="primary" size="sm">
                        Current
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm font-medium text-primary-900 mt-0.5">
                    {rec.field_of_study}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{rec.institution}</p>
                </div>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => openEditModal(rec)}
                    className="p-1.5 text-gray-400 hover:text-primary-700 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    <PencilSquareIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(rec.id, rec.degree, rec.institution)}
                    className="p-1.5 text-gray-400 hover:text-danger hover:bg-red-50 rounded-md transition-colors"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-600">
                <span>
                  Timeline: {rec.start_year} – {rec.is_current ? 'Present' : rec.end_year || 'Completed'}
                </span>
                <span className="font-semibold text-gray-900 bg-gray-100 px-2.5 py-1 rounded">
                  CGPA: {rec.cgpa}
                </span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Add / Edit Academic Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingRecord ? 'Edit Academic Record' : 'Add Academic Degree'}
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Institution / University Name"
            placeholder="e.g., Stanford University, MIT"
            required
            {...register('institution', { required: true })}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Degree Level"
              placeholder="e.g., B.S., M.S., Ph.D."
              required
              {...register('degree', { required: true })}
            />
            <Input
              label="Field of Study / Major"
              placeholder="e.g., Computer Science"
              required
              {...register('field_of_study', { required: true })}
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <Input
              label="Cumulative CGPA"
              type="number"
              step="0.01"
              min="0"
              max="10"
              required
              {...register('cgpa', { required: true, valueAsNumber: true })}
            />
            <Input
              label="Start Year"
              type="number"
              min="1980"
              max="2035"
              required
              {...register('start_year', { required: true, valueAsNumber: true })}
            />
            <Input
              label="End Year"
              type="number"
              min="1980"
              max="2035"
              disabled={isCurrent}
              {...register('end_year', { valueAsNumber: true })}
            />
          </div>

          <div className="flex items-center">
            <input
              id="is_current"
              type="checkbox"
              className="h-4 w-4 text-primary-900 rounded border-gray-300 focus:ring-primary-500"
              {...register('is_current')}
            />
            <label htmlFor="is_current" className="ml-2 text-sm text-gray-700 font-medium">
              I am currently enrolled / pursuing this degree
            </label>
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
              {editingRecord ? 'Save Changes' : 'Add Degree'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AcademicsPage;
