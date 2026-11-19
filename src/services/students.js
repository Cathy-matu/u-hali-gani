import { http, MOCK, wait } from './http'
import { PSEUDONYM } from '../data/mock'
export const studentApi = { profile: () => (MOCK ? wait({ pseudonym: PSEUDONYM }, 250) : http.get('/students/me')) }
