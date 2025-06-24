import React from 'react';
import { motion } from 'framer-motion';
import {
  HomeIcon,
  BookOpenIcon,
  AcademicCapIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
  UserCircleIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';
import { useUser } from '../contexts/UserContext';

const navigationItems = [
  { id: 'dashboard', name: 'Dashboard', icon: HomeIcon },
  { id: 'chat', name: 'Chat', icon: ChatBubbleLeftRightIcon },
  { id: 'learn', name: 'Learn', icon: BookOpenIcon },
  { id: 'review', name: 'Review', icon: AcademicCapIcon },
  { id: 'test', name: 'Test', icon: DocumentTextIcon },
  { id: 'insights', name: 'Insights', icon: ChartBarIcon },
  { id: 'sources', name: 'Sources', icon: DocumentTextIcon },
  { id: 'settings', name: 'Settings', icon: CogIcon },
];

const Sidebar = ({ activeTab, onTabChange, isCollapsed, onToggleCollapse }) => {
  const { user, logoutUser } = useUser();

  const handleLogout = () => {
    logoutUser();
  };

  return (
    <motion.div
      className={`bg-white border-r border-secondary-200 flex flex-col transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
      initial={false}
      animate={{ width: isCollapsed ? 64 : 256 }}
    >
      {/* Header */}
      <div className="p-4 border-b border-secondary-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
            <BookOpenIcon className="w-6 h-6 text-white" />
          </div>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="min-w-0 flex-1"
            >
              <h1 className="text-lg font-semibold text-secondary-900 truncate">
                AI Tutoring
              </h1>
              <p className="text-sm text-secondary-500 truncate">System</p>
            </motion.div>
          )}
        </div>
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-secondary-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <UserCircleIcon className="w-5 h-5 text-primary-600" />
          </div>
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="min-w-0 flex-1"
            >
              <p className="text-sm font-medium text-secondary-900 truncate">
                {user?.username}
              </p>
              <p className="text-xs text-secondary-500">Student</p>
            </motion.div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <motion.button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-primary-50 text-primary-700 border border-primary-200'
                  : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-sm font-medium truncate"
                >
                  {item.name}
                </motion.span>
              )}
            </motion.button>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-4 border-t border-secondary-200">
        <motion.button
          onClick={onToggleCollapse}
          className="w-full flex items-center justify-center p-2 text-secondary-500 hover:text-secondary-700 hover:bg-secondary-50 rounded-lg transition-colors duration-200"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <motion.div
            animate={{ rotate: isCollapsed ? 0 : 180 }}
            transition={{ duration: 0.3 }}
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5" />
          </motion.div>
        </motion.button>
      </div>

      {/* Logout */}
      <div className="p-4">
        <motion.button
          onClick={handleLogout}
          className={`w-full flex items-center space-x-3 px-3 py-2 text-red-600 hover:bg-red-50 hover:text-red-700 rounded-lg transition-colors duration-200 ${
            isCollapsed ? 'justify-center' : ''
          }`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <ArrowRightOnRectangleIcon className="w-5 h-5 flex-shrink-0" />
          {!isCollapsed && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-sm font-medium"
            >
              Logout
            </motion.span>
          )}
        </motion.button>
      </div>
    </motion.div>
  );
};

export default Sidebar; 