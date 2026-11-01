import { Link, Outlet } from 'react-router'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link to="/" className="text-xl font-bold">
            Retroteka
          </Link>
          {user ? (
            <span className="font-medium">{user.username}</span>
          ) : (
            <Link
              to="/register"
              className="rounded-md bg-gray-800 px-3 py-1.5 font-medium text-white hover:bg-gray-700"
            >
              Sign up
            </Link>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
