import { http, MOCK, wait } from './http'
export const checkinApi = { saveMood: m => (MOCK ? wait(m, 250) : http.post('/checkins/mood', m)) }
