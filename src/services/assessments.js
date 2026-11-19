import { http, MOCK, wait } from './http'
export const assessmentApi = { submit: a => (MOCK ? wait(a, 600) : http.post('/assessments', a)) }
