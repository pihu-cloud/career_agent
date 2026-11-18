import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ProgressBar from '../components/ui/ProgressBar';
import {
  uploadResume,
  getResumes,
  downloadResume,
  deleteResume,
} from '../services/resume';
import {
  DocumentArrowUpIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

export const ResumePage = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const fetchResumes = async () => {
    try {
      const data = await getResumes();
      const list = Array.isArray(data) ? data : data.resumes || [];
      setResumes(list);
    } catch (err) {
      console.error('Error fetching resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    if (rejectedFiles && rejectedFiles.length > 0) {
      const rej = rejectedFiles[0];
      if (rej.errors?.[0]?.code === 'file-too-large') {
        toast.error('File exceeds 10MB maximum limit');
      } else {
        toast.error('Only PDF and DOCX documents are accepted');
      }
      return;
    }

    if (!acceptedFiles || acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadProgress(20);

    // Simulated progress steps for smoother UX
    const timer = setInterval(() => {
      setUploadProgress((prev) => (prev < 85 ? prev + 15 : prev));
    }, 150);

    try {
      await uploadResume(file);
      clearInterval(timer);
      setUploadProgress(100);
      toast.success(`Resume "${file.name}" uploaded successfully!`);
      setTimeout(() => {
        setUploading(false);
        setUploadProgress(0);
        fetchResumes();
      }, 500);
    } catch (err) {
      clearInterval(timer);
      setUploading(false);
      setUploadProgress(0);
      toast.error(err.response?.data?.detail || 'Resume upload failed');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  });

  const handleDownload = async (resume) => {
    try {
      const blob = await downloadResume(resume.id);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', resume.filename || 'resume.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      toast.error('Failed to download resume file');
    }
  };

  const handleDelete = async (id, filename) => {
    if (!window.confirm(`Delete resume "${filename}"?`)) return;
    try {
      await deleteResume(id);
      toast.success('Resume deleted');
      setResumes((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete resume');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 KB';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  if (loading) {
    return <LoadingSpinner text="Retrieving resume files..." />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Resume Management</h1>
        <p className="text-sm text-gray-500 mt-1">
          Upload and organize your CV for automated skill-gap analysis and entity extraction.
        </p>
      </div>

      {/* Drag & Drop Zone */}
      <Card>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-600 bg-primary-50/50'
              : 'border-gray-300 hover:border-primary-400 bg-gray-50/50'
          }`}
        >
          <input {...getInputProps()} />
          <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-primary-900 mb-3" />
          <h3 className="text-base font-semibold text-gray-900">
            {isDragActive ? 'Drop your resume file here...' : 'Upload your resume'}
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            Drag and drop your file here, or{' '}
            <span className="text-primary-700 font-semibold underline">browse local files</span>
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Accepted formats: PDF or DOCX (Max size: 10 MB)
          </p>
        </div>

        {uploading && (
          <div className="mt-4 p-4 bg-blue-50/50 rounded-lg border border-blue-100">
            <ProgressBar
              label="Uploading & parsing document..."
              progress={uploadProgress}
              color="primary"
            />
          </div>
        )}
      </Card>

      {/* Uploaded Resumes List */}
      <div>
        <h2 className="text-lg font-bold text-gray-900 mb-3">Uploaded Documents</h2>
        {resumes.length === 0 ? (
          <Card className="text-center py-8">
            <DocumentTextIcon className="mx-auto h-10 w-10 text-gray-300" />
            <p className="text-sm text-gray-500 mt-2">No resumes uploaded yet.</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {resumes.map((res) => (
              <Card key={res.id} className="p-4 hover:border-primary-200 transition-all">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div className="flex items-center space-x-3">
                    <div className="p-2.5 bg-primary-50 text-primary-900 rounded-lg">
                      <DocumentTextIcon className="h-6 w-6" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="text-sm font-bold text-gray-900">{res.filename}</h4>
                        {res.is_primary && (
                          <Badge variant="success" size="sm">
                            Primary
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center space-x-3 text-xs text-gray-500 mt-0.5">
                        <span>{formatFileSize(res.file_size)}</span>
                        <span>•</span>
                        <span>
                          Uploaded{' '}
                          {res.uploaded_at
                            ? new Date(res.uploaded_at).toLocaleDateString()
                            : 'Recently'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 self-end sm:self-center">
                    <Button
                      variant="outline"
                      size="sm"
                      icon={ArrowDownTrayIcon}
                      onClick={() => handleDownload(res)}
                    >
                      Download
                    </Button>
                    <button
                      onClick={() => handleDelete(res.id, res.filename)}
                      className="p-1.5 text-gray-400 hover:text-danger hover:bg-red-50 rounded-md transition-colors"
                      title="Delete Resume"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumePage;
