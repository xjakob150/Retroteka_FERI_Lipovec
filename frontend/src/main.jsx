import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router'
import Layout from './components/Layout'
import { AuthProvider } from './context/AuthContext'
import AuthPage from './pages/AuthPage'
import MyCollectionsPage from './pages/MyCollectionsPage'
import NotFoundPage from './pages/NotFoundPage'
import SearchPage from './pages/SearchPage'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<SearchPage />} />
            <Route path="/register" element={<AuthPage />} />
            <Route path="/collections" element={<MyCollectionsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </StrictMode>,
)
