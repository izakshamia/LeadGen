import { useState } from 'react';

/**
 * RedditorsList Component
 * Displays a list of target redditors with their scores and details
 */
function RedditorsList({ redditors = [], loading = false, onRefresh }) {
  const [displayCount, setDisplayCount] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState({});
  const [addUsername, setAddUsername] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  // Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 animate-pulse">
      <div className="flex items-start justify-between mb-4">
        <div className="h-6 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-6 w-20 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
      </div>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
      <div className="flex gap-2">
        <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    </div>
  );

  // Empty state component
  const EmptyState = () => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 border border-gray-200 dark:border-gray-700 text-center">
      <div className="flex justify-center mb-4">
        <svg
          className="w-16 h-16 text-gray-400 dark:text-gray-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
      </div>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-2">
        No Target Redditors Yet
      </h3>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Run the redditor extraction pipeline to discover and score potential leads.
      </p>
      <div className="text-sm text-gray-500 dark:text-gray-500">
        <p>Target redditors are scored based on:</p>
        <ul className="mt-2 space-y-1">
          <li>• Authenticity (account age, karma, activity)</li>
          <li>• Need for DMCA services (comment analysis)</li>
          <li>• Engagement patterns and relevance</li>
        </ul>
      </div>
    </div>
  );



  // Show loading skeletons
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, index) => (
          <LoadingSkeleton key={index} />
        ))}
      </div>
    );
  }

  // Show empty state
  if (!redditors || redditors.length === 0) {
    return <EmptyState />;
  }

  // Filter redditors by search query
  const filteredRedditors = searchQuery
    ? redditors.filter(r => r.username.toLowerCase().includes(searchQuery.toLowerCase()))
    : redditors;

  // Get redditors to display based on pagination
  const displayedRedditors = filteredRedditors.slice(0, displayCount);
  const hasMore = filteredRedditors.length > displayCount;

  // Handle load more
  const handleLoadMore = () => {
    setDisplayCount(prev => Math.min(prev + 20, redditors.length));
  };

  // Handle status update
  const handleStatusUpdate = async (redditorId, newStatus) => {
    setUpdatingStatus(prev => ({ ...prev, [redditorId]: true }));
    
    try {
      const response = await fetch(`http://localhost:8002/redditors/${redditorId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contacted_status: newStatus
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update status');
      }

      // Refresh the list to show updated status
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      alert('Error updating status: ' + error.message);
    } finally {
      setUpdatingStatus(prev => ({ ...prev, [redditorId]: false }));
    }
  };

  // Get status badge styling
  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      approved: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
      contacted: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
      responded: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
      rejected: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
    };
    
    return styles[status] || styles.pending;
  };

  // Handle adding a redditor by username
  const handleAddRedditor = async () => {
    if (!addUsername.trim()) {
      alert('Please enter a username');
      return;
    }

    setIsAdding(true);
    try {
      const cleanUsername = addUsername.trim().replace(/^u\//, '').replace(/^\/u\//, '');
      const response = await fetch(`http://localhost:8002/redditors/add-by-username?username=${encodeURIComponent(cleanUsername)}`, {
        method: 'POST'
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add redditor');
      }

      const result = await response.json();
      alert(`✓ Successfully added u/${cleanUsername}!\n\nAccount age: ${result.redditor.account_age_days} days\nTotal karma: ${result.redditor.total_karma}`);
      setAddUsername('');
      if (onRefresh) onRefresh();
    } catch (error) {
      if (error.message.includes('409') || error.message.includes('already exists')) {
        alert(`u/${addUsername} is already in the database.`);
      } else if (error.message.includes('404') || error.message.includes('not found')) {
        alert(`u/${addUsername} not found on Reddit or profile is private.`);
      } else {
        alert('Error adding redditor: ' + error.message);
      }
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div>
      {/* Add Redditor Box */}
      <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50 mb-3">
          ➕ Add Redditor Manually
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Enter a Reddit username to fetch their profile and add them to your target list.
        </p>
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">
              u/
            </span>
            <input
              type="text"
              placeholder="username"
              value={addUsername}
              onChange={(e) => setAddUsername(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddRedditor()}
              disabled={isAdding}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
          <button
            onClick={handleAddRedditor}
            disabled={isAdding || !addUsername.trim()}
            className="px-6 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:cursor-not-allowed"
          >
            {isAdding ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Adding...
              </span>
            ) : (
              'Add Redditor'
            )}
          </button>
        </div>
      </div>

      {/* Search box */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search by username..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Header with count and buttons */}
      <div className="mb-4 flex items-center justify-between">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Showing {displayedRedditors.length} of {filteredRedditors.length} redditors
          {searchQuery && ` (filtered from ${redditors.length})`}
        </div>
        <div className="flex gap-2">
          <button
            onClick={async () => {
              if (!confirm('Fetch profiles for ALL redditors? This will update social links for everyone (may take a few minutes).')) {
                return;
              }
              try {
                const response = await fetch('http://localhost:8002/redditors/fetch-profiles?fetch_all=true&limit=100', {
                  method: 'POST'
                });
                const result = await response.json();
                alert(`Profile fetch complete:\n✓ ${result.success} updated\n✗ ${result.failed} failed\n? ${result.not_found} not found`);
                if (onRefresh) onRefresh();
              } catch (error) {
                alert('Error fetching profiles: ' + error.message);
              }
            }}
            className="px-4 py-2 text-sm bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
          >
            <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Fetch All Profiles
          </button>
          <button
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8002/redditors/fetch-profiles', {
                  method: 'POST'
                });
                const result = await response.json();
                alert(`Profile fetch complete:\n✓ ${result.success} updated\n✗ ${result.failed} failed\n? ${result.not_found} not found`);
                if (onRefresh) onRefresh();
              } catch (error) {
                alert('Error fetching profiles: ' + error.message);
              }
            }}
            className="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
          >
            <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Fetch New Profiles
          </button>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
            >
              <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          )}
        </div>
      </div>

      {/* Redditors list */}
      <div className="space-y-4">
        {displayedRedditors.map((redditor) => (
          <div
            key={redditor.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
          >
            {/* Header with username and status */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                  u/{redditor.username}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  First seen: {new Date(redditor.first_seen).toLocaleDateString()}
                </p>
              </div>
              <div>
                <span className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusBadge(redditor.contacted_status || 'pending')}`}>
                  {(redditor.contacted_status || 'pending').toUpperCase()}
                </span>
              </div>
            </div>

            {/* Stats - Reddit Profile Style */}
            <div className="grid grid-cols-2 gap-6 mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
              {/* Karma */}
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-50">
                  {redditor.total_karma?.toLocaleString() || '0'}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Karma</div>
                <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  {redditor.post_karma?.toLocaleString() || '0'} post · {redditor.comment_karma?.toLocaleString() || '0'} comment
                </div>
              </div>
              
              {/* Reddit Age */}
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-50">
                  {redditor.account_age_days ? `${Math.floor(redditor.account_age_days / 365)}y` : 'N/A'}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Reddit Age</div>
                <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  {redditor.account_age_days ? `${redditor.account_age_days} days` : 'Unknown'}
                </div>
              </div>
            </div>

            {/* Additional Info */}
            <div className="mb-4 text-sm">
              <div className="mb-2">
                <span className="text-gray-600 dark:text-gray-400">Status:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-gray-50">
                  {redditor.is_active ? '✓ Active' : '✗ Inactive'}
                </span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Found in:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-gray-50">
                  {redditor.source_posts?.length || 0} {redditor.source_posts?.length === 1 ? 'post' : 'posts'}
                </span>
                {redditor.source_posts && redditor.source_posts.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {redditor.source_posts.map((postUrl, idx) => (
                      <a
                        key={idx}
                        href={postUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
                        title={postUrl}
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                        Post {idx + 1}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Social Links */}
            {redditor.social_links && Object.keys(redditor.social_links).length > 0 && (
              <div className="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                <h4 className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 mb-2">
                  Social Links
                </h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(redditor.social_links).map(([platform, url]) => (
                    <a
                      key={platform}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-3 py-1 text-xs bg-blue-50 hover:bg-blue-100 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-200 rounded-full transition-colors"
                    >
                      {platform === 'instagram' && '📷'}
                      {platform === 'twitter' && '🐦'}
                      {platform === 'onlyfans' && '🔞'}
                      {platform === 'tiktok' && '🎵'}
                      {platform === 'youtube' && '▶️'}
                      {platform === 'twitch' && '🎮'}
                      <span className="capitalize">{platform}</span>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-wrap gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
              <a
                href={`https://reddit.com/user/${redditor.username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
              >
                View Reddit Profile
              </a>
              
              {/* Status action buttons */}
              {redditor.contacted_status === 'pending' && (
                <>
                  <button
                    onClick={() => handleStatusUpdate(redditor.id, 'approved')}
                    disabled={updatingStatus[redditor.id]}
                    className="px-4 py-2 text-sm bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                  >
                    {updatingStatus[redditor.id] ? 'Updating...' : '✓ Approve'}
                  </button>
                  <button
                    onClick={() => handleStatusUpdate(redditor.id, 'rejected')}
                    disabled={updatingStatus[redditor.id]}
                    className="px-4 py-2 text-sm bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 disabled:bg-gray-400 text-gray-700 dark:text-gray-300 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                  >
                    {updatingStatus[redditor.id] ? 'Updating...' : '✗ Reject'}
                  </button>
                </>
              )}
              
              {redditor.contacted_status === 'approved' && (
                <>
                  <button
                    onClick={() => handleStatusUpdate(redditor.id, 'contacted')}
                    disabled={updatingStatus[redditor.id]}
                    className="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                  >
                    {updatingStatus[redditor.id] ? 'Updating...' : '✉️ Mark Contacted'}
                  </button>
                  <button
                    onClick={() => handleStatusUpdate(redditor.id, 'rejected')}
                    disabled={updatingStatus[redditor.id]}
                    className="px-4 py-2 text-sm bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 disabled:bg-gray-400 text-gray-700 dark:text-gray-300 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                  >
                    {updatingStatus[redditor.id] ? 'Updating...' : '✗ Reject'}
                  </button>
                </>
              )}
              
              {(redditor.contacted_status === 'contacted' || redditor.contacted_status === 'rejected') && (
                <button
                  onClick={() => handleStatusUpdate(redditor.id, 'pending')}
                  disabled={updatingStatus[redditor.id]}
                  className="px-4 py-2 text-sm bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-400 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                >
                  {updatingStatus[redditor.id] ? 'Updating...' : '↺ Reset to Pending'}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Load More button */}
      {hasMore && (
        <div className="mt-6 text-center">
          <button
            onClick={handleLoadMore}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 shadow-md hover:shadow-lg"
          >
            Load More ({filteredRedditors.length - displayCount} remaining)
          </button>
        </div>
      )}
    </div>
  );
}

export default RedditorsList;
