import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { userAPI } from '../services/api';

const UserContext = createContext();

// Action types
const USER_ACTIONS = {
  SET_USER: 'SET_USER',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  UPDATE_PROFILE: 'UPDATE_PROFILE',
  CLEAR_USER: 'CLEAR_USER',
};

// Initial state
const initialState = {
  user: null,
  profile: null,
  loading: false,
  error: null,
  isAuthenticated: false,
};

// Reducer
function userReducer(state, action) {
  switch (action.type) {
    case USER_ACTIONS.SET_USER:
      return {
        ...state,
        user: action.payload.user,
        profile: action.payload.profile,
        isAuthenticated: true,
        loading: false,
        error: null,
      };
    case USER_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    case USER_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    case USER_ACTIONS.UPDATE_PROFILE:
      return {
        ...state,
        profile: { ...state.profile, ...action.payload },
      };
    case USER_ACTIONS.CLEAR_USER:
      return initialState;
    default:
      return state;
  }
}

// Provider component
export function UserProvider({ children }) {
  const [state, dispatch] = useReducer(userReducer, initialState);

  // Load user from localStorage on app start
  useEffect(() => {
    const savedUsername = localStorage.getItem('tutoring_username');
    if (savedUsername) {
      loginUser(savedUsername);
    }
  }, []);

  const loginUser = async (username) => {
    dispatch({ type: USER_ACTIONS.SET_LOADING, payload: true });
    try {
      // Create or get user
      const userData = await userAPI.createUser(username);
      const profileData = await userAPI.getUserProfile(username);
      
      dispatch({
        type: USER_ACTIONS.SET_USER,
        payload: {
          user: { username, ...userData },
          profile: profileData,
        },
      });

      // Save to localStorage
      localStorage.setItem('tutoring_username', username);
    } catch (error) {
      dispatch({
        type: USER_ACTIONS.SET_ERROR,
        payload: error.response?.data?.detail || 'Failed to login user',
      });
    }
  };

  const logoutUser = () => {
    localStorage.removeItem('tutoring_username');
    dispatch({ type: USER_ACTIONS.CLEAR_USER });
  };

  const refreshProfile = async () => {
    if (!state.user) return;
    
    try {
      const profileData = await userAPI.getUserProfile(state.user.username);
      dispatch({
        type: USER_ACTIONS.UPDATE_PROFILE,
        payload: profileData,
      });
    } catch (error) {
      console.error('Failed to refresh profile:', error);
    }
  };

  const updateProfile = (updates) => {
    dispatch({
      type: USER_ACTIONS.UPDATE_PROFILE,
      payload: updates,
    });
  };

  const clearError = () => {
    dispatch({ type: USER_ACTIONS.SET_ERROR, payload: null });
  };

  const value = {
    ...state,
    loginUser,
    logoutUser,
    refreshProfile,
    updateProfile,
    clearError,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

// Hook to use the user context
export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}

export default UserContext; 