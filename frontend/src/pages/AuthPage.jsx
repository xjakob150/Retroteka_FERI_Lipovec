import { Navigate, useLocation } from 'react-router'
import LoginForm from '../components/LoginForm'
import RegisterForm from '../components/RegisterForm'
import { useAuth } from '../context/AuthContext'

export default function AuthPage() {
  const { user } = useAuth()
  const { pathname } = useLocation()

  if (user) {
    return <Navigate to="/collections" replace />
  }

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold">Welcome to Retroteka</h1>
        <p className="mt-2 text-gray-500">Know what you own and what it's worth.</p>
      </div>
      <div className="grid items-start gap-6 md:grid-cols-2">
        <LoginForm />
        <div className={pathname === '/register' ? 'max-md:order-first' : ''}>
          <RegisterForm />
        </div>
      </div>
    </div>
  )
}
