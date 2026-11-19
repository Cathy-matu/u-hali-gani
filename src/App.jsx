import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useApp } from './context/AuthContext'
import { Loading } from './components/common/ui'
import PublicLayout from './layouts/PublicLayout'
import StudentLayout from './layouts/StudentLayout'
import CounsellorLayout from './layouts/CounsellorLayout'
import AdminLayout from './layouts/AdminLayout'
import ResearcherLayout from './layouts/ResearcherLayout'
const PublicLanding = lazy(() => import('./pages/public/Landing'))
const PublicLogin = lazy(() => import('./pages/public/Login'))
const PublicOnboarding = lazy(() => import('./pages/public/Onboarding'))
const StudentDashboard = lazy(() => import('./pages/student/Dashboard'))
const StudentMood = lazy(() => import('./pages/student/Mood'))
const StudentAssessment = lazy(() => import('./pages/student/Assessment'))
const StudentResources = lazy(() => import('./pages/student/Resources'))
const StudentBook = lazy(() => import('./pages/student/Book'))
const StudentMessages = lazy(() => import('./pages/student/Messages'))
const StudentAssistant = lazy(() => import('./pages/student/Assistant'))
const StudentPrivacy = lazy(() => import('./pages/student/Privacy'))
const StudentHelp = lazy(() => import('./pages/student/Help'))
const CounsellorOverview = lazy(() => import('./pages/counsellor/Overview'))
const CounsellorCases = lazy(() => import('./pages/counsellor/Cases'))
const CounsellorCaseDetail = lazy(() => import('./pages/counsellor/CaseDetail'))
const CounsellorRisk = lazy(() => import('./pages/counsellor/Risk'))
const CounsellorAppointments = lazy(() => import('./pages/counsellor/Appointments'))
const CounsellorMessages = lazy(() => import('./pages/counsellor/Messages'))
const AdminOverview = lazy(() => import('./pages/admin/Overview'))
const AdminAnalytics = lazy(() => import('./pages/admin/Analytics'))
const AdminPrivacyRules = lazy(() => import('./pages/admin/PrivacyRules'))
const AdminManagement = lazy(() => import('./pages/admin/Management'))
const ResearcherOverview = lazy(() => import('./pages/researcher/Overview'))
const ResearcherConsent = lazy(() => import('./pages/researcher/Consent'))

const Guard = ({ need, children }) => { const { role } = useApp(); return role === need ? children : <Navigate to="/login" replace /> }
export default function App() {
  return (<>
    <Toaster position="top-center" />
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route path="/" element={<PublicLanding />} /><Route path="/login" element={<PublicLogin />} /><Route path="/onboarding" element={<PublicOnboarding />} />
        </Route>
        <Route path="/student" element={<Guard need="student"><StudentLayout /></Guard>}>
          <Route index element={<StudentDashboard />} /><Route path="mood" element={<StudentMood />} /><Route path="assessment" element={<StudentAssessment />} />
          <Route path="resources" element={<StudentResources />} /><Route path="book" element={<StudentBook />} /><Route path="messages" element={<StudentMessages />} />
          <Route path="assistant" element={<StudentAssistant />} /><Route path="privacy" element={<StudentPrivacy />} /><Route path="help" element={<StudentHelp />} />
        </Route>
        <Route path="/counsellor" element={<Guard need="counsellor"><CounsellorLayout /></Guard>}>
          <Route index element={<CounsellorOverview />} /><Route path="cases" element={<CounsellorCases />} /><Route path="cases/:id" element={<CounsellorCaseDetail />} />
          <Route path="risk" element={<CounsellorRisk />} /><Route path="appointments" element={<CounsellorAppointments />} /><Route path="messages" element={<CounsellorMessages />} />
        </Route>
        <Route path="/admin" element={<Guard need="admin"><AdminLayout /></Guard>}>
          <Route index element={<AdminOverview />} /><Route path="analytics" element={<AdminAnalytics />} /><Route path="privacy" element={<AdminPrivacyRules />} /><Route path="management" element={<AdminManagement />} />
        </Route>
        <Route path="/researcher" element={<Guard need="researcher"><ResearcherLayout /></Guard>}>
          <Route index element={<ResearcherOverview />} /><Route path="consent" element={<ResearcherConsent />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense></>)
}
