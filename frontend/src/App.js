import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { UserProvider, useUser } from "./contexts/UserContext";
import LoginForm from "./components/LoginForm";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Learn from "./pages/Learn";
import Chat from "./pages/Chat";
import Settings from "./pages/Settings";
import Sources from "./pages/Sources";
// import Review from './pages/Review';
// import Test from './pages/Test';
// import Insights from './pages/Insights';

// Placeholder components for pages not yet created
const PlaceholderPage = ({ title }) => (
  <div className="p-6">
    <div className="max-w-2xl mx-auto text-center">
      <h1 className="text-3xl font-bold text-secondary-900 mb-4">{title}</h1>
      <p className="text-secondary-600">This page is coming soon!</p>
    </div>
  </div>
);

const Review = () => <PlaceholderPage title="Review Mode" />;
const Test = () => <PlaceholderPage title="Test Mode" />;
const Insights = () => <PlaceholderPage title="Learning Insights" />;

const MainApp = () => {
  const { isAuthenticated, loading } = useUser();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-secondary-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm />;
  }

  return (
    <div className="flex h-screen bg-secondary-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/learn" element={<Learn />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/review" element={<Review />} />
          <Route path="/test" element={<Test />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/sources" element={<Sources />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <UserProvider>
      <Router>
        <div className="App">
          <MainApp />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: "#363636",
                color: "#fff",
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: "#10B981",
                  secondary: "#fff",
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: "#EF4444",
                  secondary: "#fff",
                },
              },
            }}
          />
        </div>
      </Router>
    </UserProvider>
  );
}

export default App;
