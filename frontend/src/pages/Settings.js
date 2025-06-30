import React, { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import { llmAPI, chatAPI } from "../services/api";
import { useUser } from "../contexts/UserContext";

const Settings = () => {
  const { user } = useUser();
  const [providers, setProviders] = useState([]);
  const [activeProvider, setActiveProvider] = useState("");
  const [loading, setLoading] = useState(true);
  const [testingProvider, setTestingProvider] = useState("");

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const providersResponse = await llmAPI.getProviders();

      setProviders(providersResponse.providers || []);

      // Find active provider
      const active = providersResponse.providers?.find((p) => p.active);
      setActiveProvider(active?.name || "");
    } catch (error) {
      console.error("Error loading settings:", error);
      toast.error("Failed to load settings");
    } finally {
      setLoading(false);
    }
  };

  const handleProviderChange = async (providerName) => {
    try {
      const response = await llmAPI.setProvider(providerName);

      if (response.success) {
        setActiveProvider(providerName);
        toast.success(`Switched to ${providerName}`);

        // Reload settings to update the UI immediately
        await loadSettings();
      } else {
        toast.error("Failed to switch provider");
      }
    } catch (error) {
      console.error("Error switching provider:", error);
      toast.error("Failed to switch provider");
    }
  };

  const handleTestProvider = async (providerName) => {
    try {
      setTestingProvider(providerName);
      const response = await llmAPI.testProvider(providerName);

      if (response.success) {
        toast.success(`${providerName} connection successful!`);
      } else {
        toast.error(`${providerName} connection failed`);
      }
    } catch (error) {
      console.error("Error testing provider:", error);
      toast.error(`${providerName} connection failed`);
    } finally {
      setTestingProvider("");
    }
  };

  const handleClearChatHistory = async () => {
    if (
      !window.confirm(
        "Are you sure you want to clear your chat history? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      const response = await chatAPI.clearChatHistory(
        user?.username || "current_user"
      );
      if (response.success) {
        toast.success("Chat history cleared successfully");
      }
    } catch (error) {
      console.error("Error clearing chat history:", error);
      toast.error("Failed to clear chat history");
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 mt-16">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-secondary-900 mb-8">Settings</h1>

        {/* LLM Provider Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">
            AI Provider Settings
          </h2>
          <p className="text-secondary-600 mb-6">
            Configure your preferred AI language model provider. API keys should
            be configured via environment variables.
          </p>

          <div className="space-y-4">
            {providers.map((provider) => (
              <div
                key={provider.name}
                className="border border-secondary-200 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        provider.active ? "bg-green-500" : "bg-gray-300"
                      }`}
                    ></div>
                    <h3 className="font-medium text-secondary-900">
                      {provider.name}
                    </h3>
                    {provider.active && (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                        Active
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    {!provider.active && (
                      <button
                        onClick={() => handleProviderChange(provider.name)}
                        className="px-3 py-1 text-sm bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
                      >
                        Set Active
                      </button>
                    )}
                    <button
                      onClick={() => handleTestProvider(provider.name)}
                      disabled={testingProvider === provider.name}
                      className="px-3 py-1 text-sm bg-secondary-100 text-secondary-700 rounded hover:bg-secondary-200 transition-colors disabled:opacity-50"
                    >
                      {testingProvider === provider.name
                        ? "Testing..."
                        : "Test"}
                    </button>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-sm text-secondary-600">
                    API Key Status:
                  </span>
                  <span
                    className={`text-sm ${
                      provider.has_key ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {provider.has_key ? "✓ Configured" : "✗ Not configured"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data Management */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">
            Data Management
          </h2>
          <p className="text-secondary-600 mb-6">
            Manage your learning data and preferences.
          </p>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border border-secondary-200 rounded-lg">
              <div>
                <h3 className="font-medium text-secondary-900">Chat History</h3>
                <p className="text-sm text-secondary-600">
                  Clear your conversation history
                </p>
              </div>
              <button
                onClick={handleClearChatHistory}
                className="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Clear History
              </button>
            </div>
          </div>
        </div>

        {/* System Information */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">
            System Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-secondary-600">Active Provider:</span>
              <span className="ml-2 font-medium text-secondary-900">
                {activeProvider || "None"}
              </span>
            </div>
            <div>
              <span className="text-secondary-600">Total Providers:</span>
              <span className="ml-2 font-medium text-secondary-900">
                {providers.length}
              </span>
            </div>
            <div>
              <span className="text-secondary-600">Configured Keys:</span>
              <span className="ml-2 font-medium text-secondary-900">
                {providers.filter((p) => p.has_key).length}
              </span>
            </div>
            <div>
              <span className="text-secondary-600">System Status:</span>
              <span className="ml-2 font-medium text-green-600">Online</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
