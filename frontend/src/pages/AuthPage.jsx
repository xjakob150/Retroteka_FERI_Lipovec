import { Navigate } from 'react-router'
import RegisterForm from '../components/RegisterForm'
import { useAuth } from '../context/AuthContext'

export default function AuthPage() {
  const { user } = useAuth()

  if (user) {
    return <Navigate to="/collections" replace />
  }

  return (
    <div className="mx-auto max-w-xl">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold">Welcome to Retroteka</h1>
        <p className="mt-2 text-gray-500">Know what you own and what it's worth.</p>
      </div>
      <RegisterForm />
    </div>
  )
}
