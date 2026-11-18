import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  UserIcon,
  WrenchScrewdriverIcon,
  HeartIcon,
  SparklesIcon,
  AcademicCapIcon,
  DocumentArrowUpIcon,
  ChartBarIcon,
  CheckBadgeIcon,
} from '@heroicons/react/24/outline';

export const Sidebar = () => {
  const links = [
    { name: 'Dashboard', path: '/dashboard', icon: HomeIcon },
    { name: 'Profile Overview', path: '/profile', icon: UserIcon, end: true },
    { name: 'Skills', path: '/profile/skills', icon: WrenchScrewdriverIcon },
    { name: 'Interests', path: '/profile/interests', icon: HeartIcon },
    { name: 'Personality (OCEAN)', path: '/profile/personality', icon: SparklesIcon },
    { name: 'Academics', path: '/profile/academics', icon: AcademicCapIcon },
    { name: 'Resume', path: '/resume', icon: DocumentArrowUpIcon },
    { name: 'Milestones & Progress', path: '/progress', icon: ChartBarIcon },
    { name: 'Completion Status', path: '/profile/complete', icon: CheckBadgeIcon },
  ];

  return (
    <aside className="w-full md:w-64 bg-white border-r border-gray-200 flex-shrink-0 min-h-[calc(100vh-4rem)] p-4">
      <div className="mb-4 px-3 py-2 bg-gradient-to-r from-primary-900 to-secondary-700 rounded-lg text-white">
        <p className="text-xs font-semibold uppercase tracking-wider text-primary-200">Career Navigator</p>
        <p className="text-sm font-medium mt-0.5">Student Control Center</p>
      </div>

      <nav className="space-y-1">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.name}
              to={link.path}
              end={link.end}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-900 font-semibold shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
              <span className="truncate">{link.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="mt-8 pt-4 border-t border-gray-100">
        <div className="rounded-lg bg-blue-50/70 p-3 text-xs text-primary-950">
          <p className="font-semibold mb-1">Adaptive Guidance</p>
          <p className="text-gray-600 leading-relaxed">
            Fill in your skills, interests, and personality to unlock high-match career paths.
          </p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
