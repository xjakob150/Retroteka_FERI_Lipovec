import { Link, NavLink, Outlet, useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
          <nav className="flex items-center gap-4 sm:gap-6">
            <Link to="/" className="text-xl font-bold">
              Retroteka
            </Link>
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                isActive ? 'font-semibold underline underline-offset-8' : 'text-gray-600 hover:text-gray-900'
              }
            >
              Search
            </NavLink>
          </nav>
          {user ? (
            <div className="flex min-w-0 items-center gap-3">
              <span className="truncate font-medium">{user.username}</span>
              <button
                type="button"
                onClick={handleLogout}
                className="shrink-0 rounded-md border border-gray-300 px-2.5 py-1.5 font-medium whitespace-nowrap hover:bg-gray-100 sm:px-3"
              >
                Log out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 sm:gap-3">
              <Link
                to="/login"
                className="rounded-md border border-gray-300 px-2.5 py-1.5 font-medium whitespace-nowrap hover:bg-gray-100 sm:px-3"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="rounded-md bg-gray-800 px-2.5 py-1.5 font-medium whitespace-nowrap text-white hover:bg-gray-700 sm:px-3"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
