import React, { useState } from "react";
import { motion } from "framer-motion";
import { useLocation, useNavigate } from "react-router-dom";
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
} from "@heroicons/react/24/outline";
import { useUser } from "../contexts/UserContext";

const navigationItems = [
  { id: "dashboard", name: "Dashboard", icon: HomeIcon, path: "/dashboard" },
  { id: "chat", name: "Chat", icon: ChatBubbleLeftRightIcon, path: "/chat" },
  { id: "learn", name: "Learn", icon: BookOpenIcon, path: "/learn" },
  { id: "review", name: "Review", icon: AcademicCapIcon, path: "/review" },
  { id: "test", name: "Test", icon: DocumentTextIcon, path: "/test" },
  { id: "insights", name: "Insights", icon: ChartBarIcon, path: "/insights" },
  { id: "sources", name: "Sources", icon: DocumentTextIcon, path: "/sources" },
  { id: "settings", name: "Settings", icon: CogIcon, path: "/settings" },
];

const Sidebar = () => {
  const { user, logoutUser } = useUser();
  const location = useLocation();
  const navigate = useNavigate();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleLogout = () => {
    logoutUser();
  };

  const handleToggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <motion.div
      className={`bg-white border-r border-secondary-200 flex flex-col h-screen transition-all duration-300 ${
        isCollapsed ? "w-24" : "w-64"
      }`}
      initial={false}
      animate={{ width: isCollapsed ? 100 : 256 }}
    >
      {/* Header */}
      <div className="p-4 border-b border-secondary-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
            <BookOpenIcon className="w-6 h-6 text-white" />
          </div>
          {!isCollapsed && (
            <div className="min-w-0 flex-1">
              <h1 className="text-lg font-semibold text-secondary-900 truncate">
                AI Tutoring
              </h1>
              <p className="text-sm text-secondary-500 truncate">System</p>
            </div>
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
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-secondary-900 truncate">
                {user?.username}
              </p>
              <p className="text-xs text-secondary-500">Student</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <motion.button
              key={item.id}
              onClick={() => handleNavigation(item.path)}
              className={`
                ${
                  isCollapsed
                    ? "flex items-center justify-center w-12 h-12 rounded-lg transition-all duration-200"
                    : "w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200"
                }
                ${
                  isActive
                    ? "bg-primary-50 text-primary-700 border border-primary-200"
                    : "text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900"
                }
              `}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && (
                <span className="text-sm font-medium truncate">
                  {item.name}
                </span>
              )}
            </motion.button>
          );
        })}
      </nav>

      {/* Collapse Toggle & Logout at the bottom */}
      <div className="mt-auto">
        <div className="p-4 border-t border-secondary-200">
          <motion.button
            onClick={handleToggleCollapse}
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
        <div className="p-4">
          <motion.button
            onClick={handleLogout}
            className={`w-full flex items-center space-x-3 px-3 py-2 text-red-600 hover:bg-red-50 hover:text-red-700 rounded-lg transition-colors duration-200 ${
              isCollapsed ? "justify-center" : ""
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && (
              <span className="text-sm font-medium">Logout</span>
            )}
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar;
