import React from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import 'bootstrap/dist/css/bootstrap.min.css'
import './styles.css'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
createRoot(document.getElementById('root')).render(<HashRouter><AuthProvider><App /></AuthProvider></HashRouter>)

if (import.meta.env.PROD && 'serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}))
