import React, { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import { sourcesAPI, chatAPI } from "../services/api";
import { useUser } from "../contexts/UserContext";

const Sources = () => {
  const { user } = useUser();
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSource, setSelectedSource] = useState(null);
  const [filterType, setFilterType] = useState("all");
  const [sortBy, setSortBy] = useState("name");
  const [sourceStats, setSourceStats] = useState({});

  useEffect(() => {
    loadSources();
  }, []);

  const parseSourcesString = (sourcesString) => {
    const lines = sourcesString.split("\n");
    const stats = {};
    const sourcesList = [];

    for (const line of lines) {
      if (line.includes(":")) {
        const [key, value] = line.split(":").map((s) => s.trim());
        if (key && value) {
          stats[key] = value;
        }
      }

      // Parse document sources (lines starting with "  - ")
      if (line.startsWith("  - ")) {
        const sourceInfo = line.substring(4); // Remove "  - "
        const match = sourceInfo.match(/^(.+): (\d+) chunks$/);
        if (match) {
          sourcesList.push({
            name: match[1],
            chunks: parseInt(match[2]),
            type: getSourceType(match[1]),
            description: `${match[2]} text chunks from ${match[1]}`,
            size: parseInt(match[2]) * 1000, // Estimate size based on chunks
          });
        }
      }
    }

    return { stats, sources: sourcesList };
  };

  const getSourceType = (sourceName) => {
    const lowerName = sourceName.toLowerCase();
    if (lowerName.includes("pdf") || lowerName.includes(".pdf")) return "pdf";
    if (lowerName.includes("markdown") || lowerName.includes(".md"))
      return "markdown";
    if (lowerName.includes("json") || lowerName.includes(".json"))
      return "json";
    if (lowerName.includes("guide") || lowerName.includes("tutorial"))
      return "guide";
    if (lowerName.includes("text") || lowerName.includes(".txt")) return "text";
    return "document";
  };

  const loadSources = async () => {
    try {
      setLoading(true);
      const response = await sourcesAPI.getSources();

      if (response.sources) {
        const { stats, sources: parsedSources } = parseSourcesString(
          response.sources
        );
        setSourceStats(stats);
        setSources(parsedSources);
      } else {
        setSources([]);
        setSourceStats({});
      }
    } catch (error) {
      console.error("Error loading sources:", error);
      toast.error("Failed to load document sources");
      setSources([]);
      setSourceStats({});
    } finally {
      setLoading(false);
    }
  };

  const handleSourceClick = async (source) => {
    try {
      setSelectedSource(source);

      // Get detailed information about the source using the command API
      const response = await chatAPI.executeCommand(
        user?.username || "current_user",
        "!sources",
        source.name
      );

      if (response.response) {
        setSelectedSource({
          ...source,
          details: response.response,
        });
      }
    } catch (error) {
      console.error("Error getting source details:", error);
      toast.error("Failed to load source details");
    }
  };

  const filteredSources = sources.filter((source) => {
    const matchesSearch =
      source.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      source.description?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilter =
      filterType === "all" ||
      source.type?.toLowerCase() === filterType.toLowerCase();

    return matchesSearch && matchesFilter;
  });

  const sortedSources = [...filteredSources].sort((a, b) => {
    switch (sortBy) {
      case "name":
        return (a.name || "").localeCompare(b.name || "");
      case "type":
        return (a.type || "").localeCompare(b.type || "");
      case "size":
        return (a.size || 0) - (b.size || 0);
      case "chunks":
        return (a.chunks || 0) - (b.chunks || 0);
      default:
        return 0;
    }
  });

  const getSourceIcon = (type) => {
    switch (type?.toLowerCase()) {
      case "pdf":
        return "📄";
      case "markdown":
        return "📝";
      case "json":
        return "📊";
      case "text":
        return "📃";
      case "guide":
        return "📚";
      case "tutorial":
        return "🎓";
      case "document":
        return "📄";
      default:
        return "📄";
    }
  };

  const getSourceTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case "pdf":
        return "bg-red-100 text-red-800";
      case "markdown":
        return "bg-blue-100 text-blue-800";
      case "json":
        return "bg-green-100 text-green-800";
      case "text":
        return "bg-gray-100 text-gray-800";
      case "guide":
        return "bg-purple-100 text-purple-800";
      case "tutorial":
        return "bg-orange-100 text-orange-800";
      case "document":
        return "bg-indigo-100 text-indigo-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return "Unknown";
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + " " + sizes[i];
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
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
        <h1 className="text-3xl font-bold text-secondary-900 mb-8">
          Document Sources
        </h1>
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
          <div>
            <p className="text-secondary-600">
              Browse and explore the knowledge base used by the AI tutor
            </p>
          </div>
          <div className="mt-4 lg:mt-0">
            <span className="text-sm text-secondary-600">
              {filteredSources.length} of {sources.length} sources
            </span>
          </div>
        </div>

        {/* System Statistics */}
        {Object.keys(sourceStats).length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-4 mb-6">
            <h2 className="text-lg font-semibold text-secondary-900 mb-3">
              System Overview
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              {Object.entries(sourceStats).map(([key, value]) => (
                <div key={key} className="text-center">
                  <div className="font-medium text-secondary-900">{value}</div>
                  <div className="text-secondary-600">{key}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search sources..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Types</option>
                <option value="pdf">PDF</option>
                <option value="markdown">Markdown</option>
                <option value="json">JSON</option>
                <option value="text">Text</option>
                <option value="guide">Guide</option>
                <option value="tutorial">Tutorial</option>
                <option value="document">Document</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="name">Sort by Name</option>
                <option value="type">Sort by Type</option>
                <option value="chunks">Sort by Chunks</option>
                <option value="size">Sort by Size</option>
              </select>
            </div>
          </div>
        </div>

        {/* Sources Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedSources.map((source, index) => (
            <div
              key={index}
              onClick={() => handleSourceClick(source)}
              className="bg-white rounded-lg shadow-sm border border-secondary-200 p-4 cursor-pointer hover:shadow-md transition-shadow hover:border-primary-300"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="text-2xl">{getSourceIcon(source.type)}</div>
                <span
                  className={`px-2 py-1 text-xs rounded-full ${getSourceTypeColor(
                    source.type
                  )}`}
                >
                  {source.type || "Unknown"}
                </span>
              </div>

              <h3 className="font-semibold text-secondary-900 mb-2 line-clamp-2">
                {source.name || "Untitled"}
              </h3>

              {source.description && (
                <p className="text-sm text-secondary-600 mb-3 line-clamp-3">
                  {source.description}
                </p>
              )}

              <div className="flex items-center justify-between text-xs text-secondary-500">
                <span>{source.chunks} chunks</span>
                <span>{formatFileSize(source.size)}</span>
              </div>
            </div>
          ))}
        </div>

        {sortedSources.length === 0 && (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-lg font-medium text-secondary-900 mb-2">
              {sources.length === 0
                ? "No documents are currently available. Please add documents to the docs folder."
                : "Try adjusting your search terms or filters"}
            </h3>
            <p className="text-secondary-600">
              {sources.length === 0
                ? "No documents are currently available. Please add documents to the docs folder."
                : "Try adjusting your search terms or filters"}
            </p>
          </div>
        )}

        {/* Source Details Modal */}
        {selectedSource && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden">
              <div className="flex items-center justify-between p-6 border-b border-secondary-200">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">
                    {getSourceIcon(selectedSource.type)}
                  </span>
                  <div>
                    <h2 className="text-xl font-semibold text-secondary-900">
                      {selectedSource.name}
                    </h2>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${getSourceTypeColor(
                        selectedSource.type
                      )}`}
                    >
                      {selectedSource.type || "Unknown"}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedSource(null)}
                  className="text-secondary-400 hover:text-secondary-600"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {selectedSource.description && (
                  <div className="mb-4">
                    <h3 className="font-medium text-secondary-900 mb-2">
                      Description
                    </h3>
                    <p className="text-secondary-600">
                      {selectedSource.description}
                    </p>
                  </div>
                )}

                {selectedSource.details && (
                  <div className="mb-4">
                    <h3 className="font-medium text-secondary-900 mb-2">
                      Content Preview
                    </h3>
                    <div className="bg-secondary-50 rounded-lg p-4 text-sm text-secondary-700 whitespace-pre-wrap">
                      {selectedSource.details}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-secondary-600">Chunks:</span>
                    <span className="ml-2 font-medium">
                      {selectedSource.chunks}
                    </span>
                  </div>
                  <div>
                    <span className="text-secondary-600">Size:</span>
                    <span className="ml-2 font-medium">
                      {formatFileSize(selectedSource.size)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sources;
