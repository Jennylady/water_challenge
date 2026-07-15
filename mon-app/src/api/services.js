import api from './api'

const unwrap = (response, key) => {
  const payload = response?.data ?? {}

  if (payload?.success === false) {
    const error = new Error(
      payload.erreur ||
        payload.detail ||
        payload.message ||
        'La requête a échoué.'
    )

    error.response = response
    throw error
  }

  return key ? payload?.[key] : payload
}

export const formationApi = {
  listModules: async (params = {}) =>
    unwrap(await api.get('/formation/modules/', { params }), 'modules'),

  getProgression: async () =>
    unwrap(await api.get('/formation/progression/'), 'progression'),

  getModule: async (moduleSlug) =>
    unwrap(
      await api.get(
        `/formation/modules/${encodeURIComponent(moduleSlug)}/`
      ),
      'module'
    ),

  markRead: async (moduleSlug) =>
    unwrap(
      await api.post(
        `/formation/modules/${encodeURIComponent(moduleSlug)}/lire/`
      ),
      'progression'
    ),

  getQuiz: async (moduleSlug) =>
    unwrap(
      await api.get(
        `/formation/modules/${encodeURIComponent(moduleSlug)}/quiz/`
      ),
      'quiz'
    ),

  answerQuestion: async (tentativeId, questionId, payload) =>
    unwrap(
      await api.post(
        `/formation/quiz/tentatives/${encodeURIComponent(
          tentativeId
        )}/questions/${encodeURIComponent(questionId)}/reponse/`,
        payload
      ),
      'reponse'
    ),

  submitAttempt: async (tentativeId) =>
    unwrap(
      await api.post(
        `/formation/quiz/tentatives/${encodeURIComponent(
          tentativeId
        )}/soumettre/`
      ),
      'tentative'
    ),

  listAttempts: async (moduleSlug) =>
    unwrap(
      await api.get(
        `/formation/modules/${encodeURIComponent(
          moduleSlug
        )}/quiz/tentatives/`
      ),
      'tentatives'
    ),

  getRanking: async (moduleSlug) =>
    unwrap(
      await api.get(
        `/formation/modules/${encodeURIComponent(
          moduleSlug
        )}/classement/`
      ),
      'classement'
    ),
}

export const challengesApi = {
  list: async (params = {}) =>
    unwrap(await api.get('/challenges/defis/', { params }), 'defis'),

  get: async (defiId) =>
    unwrap(
      await api.get(
        `/challenges/defis/${encodeURIComponent(defiId)}/`
      ),
      'defi'
    ),

  start: async (defiId) =>
    unwrap(
      await api.post(
        `/challenges/defis/${encodeURIComponent(defiId)}/commencer/`
      ),
      'defi'
    ),

  submit: async (defiId, formData) =>
    unwrap(
      await api.post(
        `/challenges/defis/${encodeURIComponent(defiId)}/soumettre/`,
        formData
      ),
      'soumission'
    ),

  listSubmissions: async (params = {}) =>
    unwrap(
      await api.get('/challenges/mes-soumissions/', { params }),
      'soumissions'
    ),

  getSubmission: async (soumissionId) =>
    unwrap(
      await api.get(
        `/challenges/mes-soumissions/${encodeURIComponent(
          soumissionId
        )}/`
      ),
      'soumission'
    ),

  cancelSubmission: async (soumissionId) =>
    unwrap(
      await api.delete(
        `/challenges/mes-soumissions/${encodeURIComponent(
          soumissionId
        )}/annuler/`
      ),
      'soumission'
    ),

  getStatistics: async () =>
    unwrap(
      await api.get('/challenges/mes-statistiques/'),
      'statistiques'
    ),
}

export const rewardsApi = {
  mine: async () => {
    const data = unwrap(
      await api.get('/recompenses/mes-recompenses/')
    )

    return {
      badges: Array.isArray(data?.badges) ? data.badges : [],
      certificats: Array.isArray(data?.certificats)
        ? data.certificats
        : [],
    }
  },
}

export const notificationsApi = {
  list: async () => {
    const data = unwrap(await api.get('/notifications/'))
    return Array.isArray(data) ? data : []
  },

  markRead: async (notificationId) =>
    unwrap(
      await api.post(
        `/notifications/${encodeURIComponent(notificationId)}/lire/`
      )
    ),

  markAllRead: async () =>
    unwrap(await api.post('/notifications/tout-lire/')),
}

export const accountApi = {
  me: async () => unwrap(await api.get('/auth/me/'), 'user'),
  profile: async () => unwrap(await api.get('/auth/me/profile/')),
  updateProfile: async (formData) =>
    unwrap(await api.patch('/auth/me/profile/update/', formData)),
  logout: async (refresh) =>
    unwrap(await api.post('/auth/logout/', { refresh })),
}
