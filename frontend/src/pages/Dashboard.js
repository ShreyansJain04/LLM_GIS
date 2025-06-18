import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BookOpenIcon,
  AcademicCapIcon,
  ChartBarIcon,
  ClockIcon,
  TrophyIcon,
  FireIcon,
} from '@heroicons/react/24/outline';
import { useUser } from '../contexts/UserContext';
import { userAPI } from '../services/api';

const StatCard = ({ title, value, subtitle, icon: Icon, color, trend }) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    className="card"
  >
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-secondary-600">{title}</p>
        <div className="flex items-baseline space-x-2">
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
          {trend && (
            <span className={`text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? '+' : ''}{trend}%
            </span>
          )}
        </div>
        {subtitle && <p className="text-xs text-secondary-500 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-3 rounded-full ${color.replace('text-', 'bg-').replace('-600', '-100')}`}>
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
    </div>
  </motion.div>
);

const QuickActionCard = ({ title, description, buttonText, onClick, icon: Icon, color }) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    className="card"
  >
    <div className="flex items-start space-x-4">
      <div className={`p-2 rounded-lg ${color.replace('text-', 'bg-').replace('-600', '-100')}`}>
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <div className="flex-1">
        <h3 className="font-medium text-secondary-900">{title}</h3>
        <p className="text-sm text-secondary-600 mt-1">{description}</p>
        <button
          onClick={onClick}
          className="mt-3 text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          {buttonText} →
        </button>
      </div>
    </div>
  </motion.div>
);

const Dashboard = ({ onNavigate }) => {
  const { user, profile } = useUser();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInsights = async () => {
      if (!user?.username) return;
      
      try {
        const data = await userAPI.getUserInsights(user.username);
        setInsights(data);
      } catch (error) {
        console.error('Failed to fetch insights:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [user]);

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-secondary-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="card">
                <div className="h-20 bg-secondary-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const performance = insights?.performance_summary || {};
  const recommendations = insights?.personalized_recommendations || {};

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">
          Welcome back, {user?.username}!
        </h1>
        <p className="text-secondary-600 mt-1">
          Here's your learning progress and recommendations
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Topics Studied"
          value={performance.topics_studied || 0}
          subtitle="Total concepts learned"
          icon={BookOpenIcon}
          color="text-primary-600"
        />
        <StatCard
          title="Average Mastery"
          value={`${Math.round((performance.average_mastery || 0) * 100)}%`}
          subtitle="Overall understanding"
          icon={TrophyIcon}
          color="text-green-600"
          trend={5}
        />
        <StatCard
          title="Study Streak"
          value={`${performance.study_streak || 0}`}
          subtitle="Days in a row"
          icon={FireIcon}
          color="text-orange-600"
        />
        <StatCard
          title="Weak Areas"
          value={performance.weak_areas_count || 0}
          subtitle="Need improvement"
          icon={ChartBarIcon}
          color="text-red-600"
        />
      </div>

      {/* Learning Trajectory */}
      {insights?.learning_trajectory && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <h2 className="text-lg font-semibold text-secondary-900 mb-3">
            Learning Progress
          </h2>
          <p className="text-secondary-700">{insights.learning_trajectory}</p>
        </motion.div>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-secondary-900 mb-4">
          Recommended Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {profile?.recommended_topics?.length > 0 && (
            <QuickActionCard
              title="Review Weak Areas"
              description={`Focus on: ${profile.recommended_topics.slice(0, 2).join(', ')}`}
              buttonText="Start Review"
              onClick={() => onNavigate('review')}
              icon={AcademicCapIcon}
              color="text-orange-600"
            />
          )}
          
          <QuickActionCard
            title="Learn New Topic"
            description="Explore new concepts and expand your knowledge"
            buttonText="Start Learning"
            onClick={() => onNavigate('learn')}
            icon={BookOpenIcon}
            color="text-primary-600"
          />
          
          <QuickActionCard
            title="Take a Test"
            description="Evaluate your understanding with practice questions"
            buttonText="Take Test"
            onClick={() => onNavigate('test')}
            icon={ClockIcon}
            color="text-green-600"
          />
        </div>
      </div>

      {/* Personalized Recommendations */}
      {recommendations && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          {/* Study Schedule */}
          <div className="card">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">
              Personalized Schedule
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                <div>
                  <p className="font-medium text-secondary-900">Optimal Study Time</p>
                  <p className="text-sm text-secondary-600">
                    {recommendations.optimal_study_time || 'Morning'}
                  </p>
                </div>
                <ClockIcon className="w-5 h-5 text-primary-600" />
              </div>
              <div className="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                <div>
                  <p className="font-medium text-secondary-900">Session Length</p>
                  <p className="text-sm text-secondary-600">
                    {recommendations.suggested_session_length || 30} minutes
                  </p>
                </div>
                <ChartBarIcon className="w-5 h-5 text-primary-600" />
              </div>
            </div>
          </div>

          {/* Learning Tips */}
          <div className="card">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">
              Learning Tips
            </h3>
            <div className="space-y-2">
              {recommendations.learning_style_adjustments?.slice(0, 3).map((tip, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-sm text-secondary-700">{tip}</p>
                </div>
              )) || (
                <p className="text-sm text-secondary-500">No specific tips available yet. Keep learning!</p>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard; 