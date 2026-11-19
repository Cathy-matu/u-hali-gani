import { http, MOCK, wait } from './http'
export const authApi = { login: role => (MOCK ? wait({ role }, 200) : http.post('/auth/login', { role })) }
