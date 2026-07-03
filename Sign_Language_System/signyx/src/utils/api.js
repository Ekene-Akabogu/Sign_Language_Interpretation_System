import { BACKEND_URL } from './constants';

/**
 * Sends a base64-encoded JPEG frame to the FastAPI /predict endpoint.
 * Returns the prediction result or null if the request fails.
 *
 * @param {string} base64 - Base64-encoded JPEG string (no data URI prefix)
 * @returns {Promise<{hand_detected, sign, confidence, bbox, top5} | null>}
 */
export async function predictFrame(base64) {
  try {
    const res = await fetch(`${BACKEND_URL}/predict`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ image: base64 }),
    });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Prediction request failed:', err);
    return null;
  }
}

/**
 * Pings the /health endpoint to check if the backend is reachable.
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${BACKEND_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}