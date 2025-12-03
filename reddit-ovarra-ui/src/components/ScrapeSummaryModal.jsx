import { useEffect } from 'react';

/**
 * ScrapeSummaryModal Component
 * Displays a comprehensive summary of scraping results
 */
function ScrapeSummaryModal({ result, onClose }) {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  if (!result) return null;

  const totalSearched = result.processed + result.skipped + result.failed;
  const successRate = totalSearched > 0 ? Math.round((result.processed / totalSearched) * 100) : 0;

  // Determine overall status
  const getStatusInfo = () => {
    if (result.status === 'success' && result.processed > 0) {
      return {
        icon: '✅',
        title: 'Scraping Completed Successfully!',
        color: 'text-green-600 dark:text-green-400',
        bgColor: 'bg-green-50 dark:bg-green-900/20',
        borderColor: 'border-green-200 dark:border-green-800'
      };
    } else if (result.status === 'partial' || (result.processed > 0 && result.failed > 0)) {
      return {
        icon: '⚠️',
        title: 'Scraping Completed with Issues',
        color: 'text-yellow-600 dark:text-yellow-400',
        bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
        borderColor: 'border-yellow-200 dark:border-yellow-800'
      };
    } else if (result.skipped > 0 && result.processed === 0) {
      return {
        icon: 'ℹ️',
        title: 'All Posts Were Duplicates',
        color: 'text-blue-600 dark:text-blue-400',
        bgColor: 'bg-blue-50 dark:bg-blue-900/20',
        borderColor: 'border-blue-200 dark:border-blue-800'
      };
    } else {
      return {
        icon: '❌',
        title: 'No New Posts Found',
        color: 'text-red-600 dark:text-red-400',
        bgColor: 'bg-red-50 dark:bg-red-900/20',
        borderColor: 'border-red-200 dark:border-red-800'
      };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className={`p-6 border-b ${statusInfo.borderColor} ${statusInfo.bgColor}`}>
          <div className="flex items-start justify-between">
            <div>
              <h2 className={`text-2xl font-bold ${statusInfo.color} flex items-center gap-2`}>
                <span className="text-3xl">{statusInfo.icon}</span>
                {statusInfo.title}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Scraping operation completed
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              aria-label="Close"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Key Metrics */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-3">
              📊 Key Metrics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* New Posts */}
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {result.processed}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  New Posts
                </div>
              </div>

              {/* Duplicates */}
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
                  {result.skipped}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Duplicates
                </div>
              </div>

              {/* Failed */}
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-red-600 dark:text-red-400">
                  {result.failed}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Failed
                </div>
              </div>

              {/* Success Rate */}
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {successRate}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Success Rate
                </div>
              </div>
            </div>
          </div>

          {/* Redditors */}
          {result.redditors_extracted > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-3">
                👥 Target Redditors
              </h3>
              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                      {result.redditors_saved} saved
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      from {result.redditors_extracted} unique redditors found
                    </div>
                  </div>
                  <div className="text-4xl">
                    🎯
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Breakdown */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-3">
              📈 Detailed Breakdown
            </h3>
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700 dark:text-gray-300">Total Posts Searched:</span>
                <span className="font-semibold text-gray-900 dark:text-gray-50">{totalSearched}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700 dark:text-gray-300">✅ Successfully Processed:</span>
                <span className="font-semibold text-green-600 dark:text-green-400">{result.processed}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700 dark:text-gray-300">⏭️ Skipped (Duplicates):</span>
                <span className="font-semibold text-yellow-600 dark:text-yellow-400">{result.skipped}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700 dark:text-gray-300">❌ Failed to Process:</span>
                <span className="font-semibold text-red-600 dark:text-red-400">{result.failed}</span>
              </div>
              {result.redditors_extracted > 0 && (
                <>
                  <div className="border-t border-gray-300 dark:border-gray-600 pt-3 mt-3"></div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700 dark:text-gray-300">👥 Redditors Extracted:</span>
                    <span className="font-semibold text-purple-600 dark:text-purple-400">{result.redditors_extracted}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700 dark:text-gray-300">💾 Redditors Saved:</span>
                    <span className="font-semibold text-purple-600 dark:text-purple-400">{result.redditors_saved}</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Insights */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-3">
              💡 Insights
            </h3>
            <div className="space-y-2 text-sm">
              {result.processed > 0 && (
                <div className="flex items-start gap-2 text-green-700 dark:text-green-300">
                  <span>✓</span>
                  <span>Found {result.processed} new relevant post{result.processed !== 1 ? 's' : ''} with AI-generated replies</span>
                </div>
              )}
              {result.skipped > 0 && (
                <div className="flex items-start gap-2 text-yellow-700 dark:text-yellow-300">
                  <span>ℹ</span>
                  <span>{result.skipped} post{result.skipped !== 1 ? 's were' : ' was'} skipped as duplicate{result.skipped !== 1 ? 's' : ''} (already in database)</span>
                </div>
              )}
              {result.failed > 0 && (
                <div className="flex items-start gap-2 text-red-700 dark:text-red-300">
                  <span>⚠</span>
                  <span>{result.failed} post{result.failed !== 1 ? 's' : ''} failed to process (may be deleted or inaccessible)</span>
                </div>
              )}
              {result.redditors_saved > 0 && (
                <div className="flex items-start gap-2 text-purple-700 dark:text-purple-300">
                  <span>🎯</span>
                  <span>Discovered {result.redditors_saved} new potential lead{result.redditors_saved !== 1 ? 's' : ''} for outreach</span>
                </div>
              )}
              {result.processed === 0 && result.skipped === 0 && result.failed === 0 && (
                <div className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
                  <span>ℹ</span>
                  <span>No posts found matching your criteria. Try different keywords or subreddits.</span>
                </div>
              )}
            </div>
          </div>

          {/* Next Steps */}
          {result.processed > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-3">
                🚀 Next Steps
              </h3>
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 space-y-2 text-sm">
                <div className="flex items-start gap-2 text-blue-700 dark:text-blue-300">
                  <span>1.</span>
                  <span>Check the <strong>Suggestions</strong> tab to review new posts and AI-generated replies</span>
                </div>
                {result.redditors_saved > 0 && (
                  <div className="flex items-start gap-2 text-blue-700 dark:text-blue-300">
                    <span>2.</span>
                    <span>Check the <strong>Target Redditors</strong> tab to review potential leads</span>
                  </div>
                )}
                <div className="flex items-start gap-2 text-blue-700 dark:text-blue-300">
                  <span>{result.redditors_saved > 0 ? '3' : '2'}.</span>
                  <span>Approve suggestions and mark redditors for outreach</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <button
            onClick={onClose}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium px-6 py-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Close Summary
          </button>
        </div>
      </div>
    </div>
  );
}

export default ScrapeSummaryModal;
