import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import ScrapePanel from './components/ScrapePanel';
import Dashboard from './components/Dashboard';
import SuggestionsList from './components/SuggestionsList';
import RedditorsList from './components/RedditorsList';
import { Toast } from './components/Toast';
import { useFilteredSuggestions } from './hooks/useFilteredSuggestions';
import { useToast } from './hooks/useToast';
import api from './services/api';
import { getUserFriendlyErrorMessage, logError } from './utils/errorHandling';

function App() {
  // State management for active tab
  const [activeTab, setActiveTab] = useState('suggestions');
  
  // State management for suggestions and filters
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [timeWindow, setTimeWindow] = useState(24);
  
  // State management for redditors
  const [redditors, setRedditors] = useState([]);
  const [redditorsLoading, setRedditorsLoading] = useState(false);
  
  const { showToast } = useToast();
  
  // Use the filtering hook for statusFilter and searchQuery
  const {
    filteredSuggestions,
    statusFilter,
    searchQuery,
    handleStatusFilterChange,
    handleSearchChange
  } = useFilteredSuggestions(suggestions);

  // Load suggestions from API based on timeWindow
  const loadSuggestions = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.getSuggestions(timeWindow);
      setSuggestions(response.suggestions || []);
    } catch (error) {
      // Log error with context for debugging
      logError(error, 'loadSuggestions', { timeWindow });
      
      // Show user-friendly error message
      const errorMessage = getUserFriendlyErrorMessage(error, 'loading suggestions');
      showToast(errorMessage, 'error', 5000);
    } finally {
      setLoading(false);
    }
  }, [timeWindow, showToast]);

  // Load redditors from API
  const loadRedditors = useCallback(async () => {
    setRedditorsLoading(true);
    try {
      // Fetch more redditors (100 instead of 50)
      const response = await api.getRedditors(100, 0);
      setRedditors(response.redditors || []);
    } catch (error) {
      // Log error with context for debugging
      logError(error, 'loadRedditors');
      
      // Show user-friendly error message
      const errorMessage = getUserFriendlyErrorMessage(error, 'loading redditors');
      showToast(errorMessage, 'error', 5000);
    } finally {
      setRedditorsLoading(false);
    }
  }, [showToast]);

  // Load suggestions on mount and when time window changes
  useEffect(() => {
    loadSuggestions();
    loadRedditors();
  }, [loadSuggestions, loadRedditors]);

  // Handle scrape function that triggers scraping and refreshes suggestions
  const handleScrape = async (params) => {
    try {
      // Scraping is now synchronous - the API waits for completion
      const result = await api.scrape(params);
      
      // Refresh both suggestions and redditors after scraping completes
      await Promise.all([
        loadSuggestions(),
        loadRedditors()
      ]);
      
      // Show simple toast - detailed summary will be in modal
      const toastType = result.status === 'success' ? 'success' : result.status === 'partial' ? 'info' : 'error';
      const icon = result.status === 'success' ? '✓' : result.status === 'partial' ? '⚠' : 'ℹ';
      showToast(`${icon} Scraping complete! ${result.processed} new posts found.`, toastType, 4000);
      
      return result;
    } catch (error) {
      // Log error with context for debugging
      logError(error, 'handleScrape', { params });
      
      // Show user-friendly error message
      const errorMessage = getUserFriendlyErrorMessage(error, 'scraping');
      showToast(errorMessage, 'error', 5000);
      throw error;
    }
  };

  // Handle refresh function that re-fetches suggestions
  const handleRefresh = () => {
    loadSuggestions();
  };

  // Handle redditors refresh
  const handleRedditorsRefresh = () => {
    loadRedditors();
  };

  // Handle time window change
  const handleTimeWindowChange = (newTimeWindow) => {
    setTimeWindow(newTimeWindow);
  };

  // Handle suggestion actions (placeholder for now)
  const handleSuggestionAction = (action, suggestion) => {
    console.log('Action:', action, 'Suggestion:', suggestion);
    // Future: Implement actual action handlers
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Toast notifications */}
      <Toast />
      
      {/* Header with API status and theme toggle */}
      <Header />
      
      {/* Main content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-50 mb-2">
              Reddit Ovarra Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Manage Reddit post suggestions with AI-generated replies
            </p>
          </div>
          
          {/* Scrape control panel */}
          <ScrapePanel onScrape={handleScrape} />
          
          {/* Tab Navigation */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('suggestions')}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === 'suggestions'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <svg className="w-5 h-5 inline mr-2 -mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                Suggestions
                {suggestions.length > 0 && (
                  <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {suggestions.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('redditors')}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === 'redditors'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <svg className="w-5 h-5 inline mr-2 -mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                Target Redditors
                {redditors.length > 0 && (
                  <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {redditors.length}
                  </span>
                )}
              </button>
            </nav>
          </div>

          {/* Conditional rendering based on active tab */}
          {activeTab === 'suggestions' ? (
            <>
              {/* Dashboard with stats and filters */}
              <Dashboard
                suggestions={suggestions}
                timeWindow={timeWindow}
                statusFilter={statusFilter}
                searchQuery={searchQuery}
                onTimeWindowChange={handleTimeWindowChange}
                onStatusFilterChange={handleStatusFilterChange}
                onSearchChange={handleSearchChange}
                onRefresh={handleRefresh}
              />
              
              {/* Suggestions list with filtered results */}
              <SuggestionsList
                suggestions={filteredSuggestions}
                loading={loading}
                onAction={handleSuggestionAction}
              />
            </>
          ) : (
            <>
              {/* Redditors list */}
              <RedditorsList
                redditors={redditors}
                loading={redditorsLoading}
                onRefresh={handleRedditorsRefresh}
              />
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
