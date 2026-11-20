import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Phone, Search } from 'lucide-react'
import { Card, Badge, Empty, Loading, Disclaimer, Modal, Risk } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { useApp } from '../../context/AuthContext'
import { moods, moodHistory, resources, counsellors, slots, helpContacts, assistantReplies } from '../../data/mock'
import { SHORT, FULL, FREQ, WHO_OPT } from '../../data/instruments'
import { scoreAll, routeRisk } from '../../utils/scoring'
import Calendar, { fmt, startOfToday } from '../../components/forms/Calendar'
import { checkinApi, assessmentApi, bookingApi, consentApi } from '../../services/api'


export function Messages() {
  return (<><h1 className="h3">Messages</h1><Chat replyAs="them" threads={[{ name: 'Dr. Amina Wekesa', online: true, unread: 0, msgs: [{ from: 'them', text: 'Hi, looking forward to Friday. Bring anything you want to talk about.', time: 'Yesterday', read: true }] }, { name: 'Counselling front desk', online: false, unread: 1, msgs: [{ from: 'them', text: 'Reminder: you can reschedule up to 24 hours before.', time: 'Mon' }] }]} /></>)
}

export default Messages
