import { http } from './http'

class InvalidAuthResponseError extends Error {}

const userFromResponse = response => {
  const user = response.data
  if (
    !user ||
    typeof user !== 'object' ||
    Array.isArray(user) ||
    typeof user.id !== 'string' ||
    typeof user.full_name !== 'string' ||
    !['student', 'counsellor'].includes(user.role)
  ) {
    throw new InvalidAuthResponseError('The Hali API returned an unexpected response. Check that the backend is running and VITE_API_BASE_URL is configured correctly.')
  }
  return user
}

export const authApi = {
  login: credentials => http.post('/auth/login', credentials).then(userFromResponse),
  register: details => http.post('/auth/register', details).then(userFromResponse),
  me: () => http.get('/auth/me').then(userFromResponse),
  updateConsent: consent => http.patch('/auth/consent', consent).then(userFromResponse),
  logout: () => http.post('/auth/logout'),
}

export function getAuthErrorMessage(error, fallback) {
  if (error instanceof InvalidAuthResponseError) return error.message
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map(item => item.msg).filter(Boolean).join(' ') || fallback
  }
  return fallback
}
