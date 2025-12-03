import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { useToast } from '../hooks/useToast';
import { scrape } from '../services/api';
import Tooltip from './Tooltip';
import ScrapeSummaryModal from './ScrapeSummaryModal';

/**
 * ScrapePanel Component
 * Form for triggering Reddit scraping with custom parameters
 */
function ScrapePanel({ onScrape }) {
  // Default values from pipeline configuration
  const defaultSubreddits = 'CamGirlProblems, OnlyFansAdvice, AdultContentCreators, SexWorkers, CreatorsAdvice, OnlyFans, OnlyFansCentral, OnlyfansCreators, OnlyFansBabes, CamGirls, Camming, Fansly, fanslypromotions';
  const defaultKeywords = 'leak, stolen, dmca, help, advice, piracy';
  
  // Form state
  const [subreddits, setSubreddits] = useState(defaultSubreddits);
  const [keywords, setKeywords] = useState(defaultKeywords);
  const [postLimit, setPostLimit] = useState(10);
  const [maxAgeDays, setMaxAgeDays] = useState(30);
  
  // Validation errors
  const [errors, setErrors] = useState({});
  
  // Scrape result state
  const [result, setResult] = useState(null);
  const [scrapingStatus, setScrapingStatus] = useState('');
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  
  // API and toast hooks
  const { loading, execute } = useApi();
  const { showToast } = useToast();

  /**
   * Validate form inputs
   * @returns {boolean} True if form is valid
   */
  const validateForm = () => {
    const newErrors = {};

    // Validate subreddits (required)
    if (!subreddits.trim()) {
      newErrors.subreddits = 'Subreddits are required';
    }

    // Validate keywords (required)
    if (!keywords.trim()) {
      newErrors.keywords = 'Keywords are required';
    }

    // Validate post_limit range (5-50)
    if (postLimit < 5 || postLimit > 50) {
      newErrors.postLimit = 'Post limit must be between 5 and 50';
    }

    // Validate max_age_days range (7-120)
    if (maxAgeDays < 7 || maxAgeDays > 120) {
      newErrors.maxAgeDays = 'Max age must be between 7 and 120 days';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous result and status
    setResult(null);
    setScrapingStatus('');

    // Validate form
    if (!validateForm()) {
      showToast('Please fix form errors', 'error');
      return;
    }

    try {
      // Parse comma-separated values into arrays
      const subredditsArray = subreddits
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);
      
      const keywordsArray = keywords
        .split(',')
        .map(k => k.trim())
        .filter(k => k.length > 0);

      // Prepare params
      const params = {
        subreddits: subredditsArray,
        keywords: keywordsArray,
        post_limit: postLimit,
        max_age_days: maxAgeDays,
      };

      // Calculate estimated time (rough estimate: 20-30 seconds per subreddit-keyword combo)
      const totalCombos = subredditsArray.length * keywordsArray.length;
      const estimatedMinutes = Math.ceil((totalCombos * 25) / 60); // 25 seconds average per combo
      
      // Show what's being scraped with estimate
      setScrapingStatus(
        `Scraping ${subredditsArray.length} subreddit(s) × ${keywordsArray.length} keyword(s) = ${totalCombos} searches\n` +
        `Estimated time: ${estimatedMinutes} minute${estimatedMinutes !== 1 ? 's' : ''}`
      );

      // Call parent handler if provided, otherwise call API directly
      let response;
      if (onScrape) {
        response = await execute(() => onScrape(params));
      } else {
        response = await execute(() => scrape(params));
      }

      // Store result and show summary modal
      setResult(response);
      setScrapingStatus('');
      setShowSummaryModal(true);
    } catch (error) {
      // Error handling is done by parent or useApi hook
      console.error('Scrape error:', error);
      setScrapingStatus('');
    }
  };

  return (
    <>
      {/* Summary Modal */}
      {showSummaryModal && (
        <ScrapeSummaryModal
          result={result}
          onClose={() => setShowSummaryModal(false)}
        />
      )}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-50 mb-4">
          Scrape Reddit Posts
        </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Subreddits Input */}
        <div>
          <label 
            htmlFor="subreddits" 
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            <Tooltip content="Enter subreddit names to scrape (comma-separated)" position="right">
              <span>Subreddits <span className="text-red-500">*</span></span>
            </Tooltip>
          </label>
          <input
            id="subreddits"
            type="text"
            value={subreddits}
            onChange={(e) => setSubreddits(e.target.value)}
            placeholder="e.g., webdev, programming, javascript"
            disabled={loading}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed ${
              errors.subreddits ? 'border-red-500' : 'border-gray-300'
            }`}
            aria-required="true"
            aria-invalid={!!errors.subreddits}
            aria-describedby={errors.subreddits ? 'subreddits-error' : 'subreddits-help'}
          />
          {errors.subreddits && (
            <p id="subreddits-error" className="mt-1 text-sm text-red-500">
              {errors.subreddits}
            </p>
          )}
          <p id="subreddits-help" className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Enter subreddit names separated by commas
          </p>
        </div>

        {/* Keywords Input */}
        <div>
          <label 
            htmlFor="keywords" 
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
          >
            <Tooltip content="Keywords to search for in post titles and content" position="right">
              <span>Keywords <span className="text-red-500">*</span></span>
            </Tooltip>
          </label>
          <input
            id="keywords"
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="e.g., help, question, advice"
            disabled={loading}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed ${
              errors.keywords ? 'border-red-500' : 'border-gray-300'
            }`}
            aria-required="true"
            aria-invalid={!!errors.keywords}
            aria-describedby={errors.keywords ? 'keywords-error' : 'keywords-help'}
          />
          {errors.keywords && (
            <p id="keywords-error" className="mt-1 text-sm text-red-500">
              {errors.keywords}
            </p>
          )}
          <p id="keywords-help" className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Enter keywords to search for, separated by commas
          </p>
        </div>

        {/* Post Limit and Max Age - Responsive Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Post Limit Select */}
          <div>
            <label 
              htmlFor="postLimit" 
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              <Tooltip content="Maximum number of posts to scrape per subreddit (5-50)" position="right">
                <span>Post Limit</span>
              </Tooltip>
            </label>
            <select
              id="postLimit"
              value={postLimit}
              onChange={(e) => setPostLimit(Number(e.target.value))}
              disabled={loading}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value={5}>5 posts</option>
              <option value={10}>10 posts</option>
              <option value={20}>20 posts</option>
              <option value={50}>50 posts</option>
            </select>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Maximum posts to scrape per subreddit
            </p>
          </div>

          {/* Max Age Days Select */}
          <div>
            <label 
              htmlFor="maxAgeDays" 
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              <Tooltip content="Only scrape posts newer than this age (7-120 days)" position="right">
                <span>Max Post Age</span>
              </Tooltip>
            </label>
            <select
              id="maxAgeDays"
              value={maxAgeDays}
              onChange={(e) => setMaxAgeDays(Number(e.target.value))}
              disabled={loading}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={120}>120 days</option>
            </select>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Only scrape posts newer than this
            </p>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium px-6 py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg 
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" 
                  xmlns="http://www.w3.org/2000/svg" 
                  fill="none" 
                  viewBox="0 0 24 24"
                >
                  <circle 
                    className="opacity-25" 
                    cx="12" 
                    cy="12" 
                    r="10" 
                    stroke="currentColor" 
                    strokeWidth="4"
                  />
                  <path 
                    className="opacity-75" 
                    fill="currentColor" 
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Scraping...
              </span>
            ) : (
              'Start Scraping'
            )}
          </button>
          
          {/* Progress status message */}
          {loading && scrapingStatus && (
            <div className="mt-3 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex items-start">
                <svg 
                  className="animate-spin h-5 w-5 text-blue-600 dark:text-blue-400 mr-3 mt-0.5 flex-shrink-0" 
                  xmlns="http://www.w3.org/2000/svg" 
                  fill="none" 
                  viewBox="0 0 24 24"
                >
                  <circle 
                    className="opacity-25" 
                    cx="12" 
                    cy="12" 
                    r="10" 
                    stroke="currentColor" 
                    strokeWidth="4"
                  />
                  <path 
                    className="opacity-75" 
                    fill="currentColor" 
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-800 dark:text-blue-200 whitespace-pre-line">
                    {scrapingStatus}
                  </p>
                  <div className="mt-3 space-y-1 text-xs text-blue-600 dark:text-blue-300">
                    <p>⏳ Searching Reddit posts...</p>
                    <p>🤖 Classifying relevance with AI...</p>
                    <p>💬 Fetching comments...</p>
                    <p>✍️ Generating replies...</p>
                    <p>👥 Extracting redditors...</p>
                  </div>
                  <p className="text-xs text-blue-500 dark:text-blue-400 mt-3 font-medium">
                    Please keep this tab open and wait for completion.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Result Display */}
        {result && !loading && (
          <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-2">
              Scraping Complete
            </h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {result.processed}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Processed</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {result.skipped}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Skipped</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {result.failed}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
    </>
  );
}

export default ScrapePanel;
