import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getProfileCompletion } from '../../services/profile';
import {
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon,
  UserCircleIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

export const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [completion, setCompletion] = useState(0);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCompletion = async () => {
      try {
        const res = await getProfileCompletion();
        const score = res.completion_percentage ?? res.percentage ?? res.score ?? 0;
        setCompletion(score);
      } catch {
        // Default estimate if backend endpoint is not populated yet
        setCompletion(65);
      }
    };
    if (user) {
      fetchCompletion();
    }
  }, [user, location.pathname]);

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Profile', path: '/profile' },
    { name: 'Resume', path: '/resume' },
    { name: 'Progress', path: '/progress' },
    { name: 'Recommendations', path: '/recommendations' },
    ...(isAdmin ? [{ name: 'Admin', path: '/admin' }] : []),
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Desktop Nav Links */}
          <div className="flex items-center space-x-8">
            <Link to="/dashboard" className="flex items-center space-x-2.5">
              <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-primary-900 to-secondary-600 flex items-center justify-center text-white shadow-md">
                <SparklesIcon className="h-5 w-5" />
              </div>
              <span className="font-bold text-xl tracking-tight text-gray-900">
                CareerPilot <span className="text-secondary-600">AI</span>
              </span>
            </Link>

            <div className="hidden md:flex md:space-x-1 lg:space-x-3">
              {navLinks.map((link) => {
                const isActive = location.pathname.startsWith(link.path);
                return (
                  <Link
                    key={link.name}
                    to={link.path}
                    className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-primary-50 text-primary-900 font-semibold'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right side: Profile completion badge & User Menu */}
          <div className="hidden md:flex md:items-center md:space-x-4">
            {/* Quick Profile Completion Pill */}
            <Link
              to="/profile"
              className="flex items-center space-x-2 px-3 py-1 bg-gray-50 border border-gray-200 rounded-full hover:bg-gray-100 transition-colors"
              title="Profile Completion Score"
            >
              <div className="w-16 bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-primary-900 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${completion}%` }}
                />
              </div>
              <span className="text-xs font-semibold text-gray-700">{completion}% Profile</span>
            </Link>

            {/* User display name */}
            <div className="flex items-center space-x-2 pl-2 border-l border-gray-200">
              <UserCircleIcon className="h-8 w-8 text-gray-400" />
              <div className="text-left">
                <p className="text-sm font-medium text-gray-800 leading-none">
                  {user?.full_name || user?.username || 'Student'}
                </p>
                <p className="text-xs text-gray-500 mt-0.5 capitalize">{user?.role || 'Student'}</p>
              </div>
            </div>

            {/* Logout button */}
            <button
              onClick={handleLogout}
              className="p-2 text-gray-500 hover:text-danger hover:bg-red-50 rounded-lg transition-colors"
              title="Log out"
              aria-label="Log out"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Mobile hamburger button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 px-4 pt-2 pb-4 space-y-1 bg-white">
          <div className="py-2 mb-2 border-b border-gray-100 flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">
              {user?.full_name || user?.username}
            </span>
            <span className="text-xs font-bold text-primary-900 bg-primary-50 px-2 py-0.5 rounded-full">
              {completion}% Complete
            </span>
          </div>
          {navLinks.map((link) => {
            const isActive = location.pathname.startsWith(link.path);
            return (
              <Link
                key={link.name}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  isActive
                    ? 'bg-primary-50 text-primary-900 font-semibold'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {link.name}
              </Link>
            );
          })}
          <div className="pt-3 border-t border-gray-200">
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                handleLogout();
              }}
              className="flex w-full items-center px-3 py-2 text-base font-medium text-danger hover:bg-red-50 rounded-md"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5 mr-2" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
