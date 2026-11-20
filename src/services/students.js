import { http } from './http'
export const studentApi = {
  profile: () => http.get('/auth/me').then(response => ({ pseudonym: response.data.pseudonym })),
}
