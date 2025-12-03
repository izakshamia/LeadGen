/**
 * API Service for Reddit Ovarra Backend
 * Handles all HTTP communication with the Railway-hosted API
 */

// Use local backend for development, Railway for production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

/**
 * Check API health status
 * @returns {Promise<{status: string}>}
 * @throws {Error} If health check fails
 */
export async function health() {
  try {
    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout for health check
    
    const response = await fetch(`${API_BASE_URL}/health`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`Health check failed: HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    // Handle different error types
    if (error.name === 'TypeError' || error.name === 'NetworkError') {
      throw new Error('Network error: Unable to reach server');
    }
    if (error.name === 'AbortError') {
      throw new Error('Network error: Request timed out');
    }
    throw error;
  }
}

/**
 * Fetch suggestions within time window
 * @param {number} hours - Time window in hours (default: 24)
 * @returns {Promise<{suggestions: Array}>}
 * @throws {Error} If request fails
 */
export async function getSuggestions(hours = 24) {
  try {
    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
    const response = await fetch(`${API_BASE_URL}/suggestions?hours=${hours}`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.message || errorData.detail || 'Failed to fetch suggestions';
      throw new Error(`${errorMessage} (HTTP ${response.status})`);
    }
    
    return await response.json();
  } catch (error) {
    // Handle different error types
    if (error.name === 'TypeError' || error.name === 'NetworkError') {
      throw new Error('Network error: Unable to reach server');
    }
    if (error.name === 'AbortError') {
      throw new Error('Network error: Request timed out');
    }
    throw error;
  }
}

/**
 * Trigger Reddit scraping
 * @param {Object} params - Scraping parameters
 * @param {string[]} params.subreddits - List of subreddit names
 * @param {string[]} params.keywords - List of keywords
 * @param {number} params.post_limit - Maximum posts to scrape (5-50)
 * @param {number} params.max_age_days - Maximum post age in days (7-120)
 * @returns {Promise<{status: string, processed: number, skipped: number, failed: number}>}
 * @throws {Error} If scrape request fails
 */
export async function scrape(params) {
  try {
    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minute timeout for scraping
    
    const response = await fetch(`${API_BASE_URL}/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.message || errorData.detail || 'Scrape request failed';
      throw new Error(`${errorMessage} (HTTP ${response.status})`);
    }
    
    return await response.json();
  } catch (error) {
    // Handle different error types
    if (error.name === 'TypeError' || error.name === 'NetworkError') {
      throw new Error('Network error: Unable to reach server');
    }
    if (error.name === 'AbortError') {
      throw new Error('Network error: Request timed out - scraping may take longer than expected');
    }
    throw error;
  }
}

/**
 * Fetch target redditors
 * @param {number} limit - Maximum number of redditors to return (default: 50)
 * @param {number} offset - Number of records to skip for pagination (default: 0)
 * @returns {Promise<{redditors: Array}>}
 * @throws {Error} If request fails
 */
export async function getRedditors(limit = 50, offset = 0) {
  try {
    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
    const response = await fetch(`${API_BASE_URL}/redditors?limit=${limit}&offset=${offset}`, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.message || errorData.detail || 'Failed to fetch redditors';
      throw new Error(`${errorMessage} (HTTP ${response.status})`);
    }
    
    return await response.json();
  } catch (error) {
    // Handle different error types
    if (error.name === 'TypeError' || error.name === 'NetworkError') {
      throw new Error('Network error: Unable to reach server');
    }
    if (error.name === 'AbortError') {
      throw new Error('Network error: Request timed out');
    }
    throw error;
  }
}

export default {
  health,
  getSuggestions,
  scrape,
  getRedditors,
};
