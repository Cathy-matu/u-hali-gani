import { http, MOCK, wait } from './http'
export const consentApi = { update: c => (MOCK ? wait(c, 250) : http.put('/consent', c)) }
