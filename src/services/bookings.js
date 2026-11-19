import { http, MOCK, wait } from './http'
import { counsellors, slots } from '../data/mock'
export const bookingApi = { counsellors: () => (MOCK ? wait(counsellors) : http.get('/counsellors')), slots: () => (MOCK ? wait(slots, 250) : http.get('/slots')), book: b => (MOCK ? wait(b, 500) : http.post('/bookings', b)) }
