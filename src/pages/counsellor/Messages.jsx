import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'
import { Card, Stat, Risk as RiskBadge, Badge, Disclaimer, Modal, Loading } from '../../components/common/ui'
import Chat from '../../components/common/Chat'
import { cases, brief, appointmentsC } from '../../data/mock'
import Calendar, { iso, fmt } from '../../components/forms/Calendar'


export function CMessages() {
  return (<><h1 className="h3">Messages</h1><Chat replyAs="them" threads={[{ name: 'Swift-Baobab-208', online: true, unread: 2, priority: true, msgs: [{ from: 'them', text: 'I don’t think I can do this week.', time: '08:12' }] }, { name: 'Calm-Mango-532', online: false, unread: 1, msgs: [{ from: 'them', text: 'Can we move to Friday?', time: 'Yesterday' }] }, { name: 'Gentle-River-119', online: false, unread: 0, msgs: [{ from: 'me', text: 'See you Monday.', time: 'Mon', read: true }] }]} /></>)
}

export default CMessages
