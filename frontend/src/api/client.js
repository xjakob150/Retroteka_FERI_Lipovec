import axios from 'axios'

export const REFRESH_TOKEN_KEY = 'refreshToken'

// Pri teh poteh 401 ne pomeni poteklega access žetona.
const PATHS_WITHOUT_REFRESH = ['/auth/login/', '/auth/register/', '/auth/refresh/', '/auth/logout/']

let accessToken = null
let onSessionExpired = () => {}
let refreshing = null

export function setAccessToken(token) {
  accessToken = token
}

export function setOnSessionExpired(callback) {
  onSessionExpired = callback
}

const client = axios.create({ baseURL: import.meta.env.VITE_API_URL })

client.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

export function refreshAccessToken() {
  if (!refreshing) {
    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)
    refreshing = client
      .post('/auth/refresh/', { refresh })
      .then((response) => setAccessToken(response.data.access))
      .finally(() => {
        refreshing = null
      })
  }
  return refreshing
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    if (
      response?.status !== 401 ||
      config.retried ||
      PATHS_WITHOUT_REFRESH.includes(config.url)
    ) {
      throw error
    }
    try {
      await refreshAccessToken()
    } catch (refreshError) {
      if (refreshError.response?.status === 401) {
        onSessionExpired()
      }
      throw error
    }
    config.retried = true
    return client(config)
  },
)

export default client
