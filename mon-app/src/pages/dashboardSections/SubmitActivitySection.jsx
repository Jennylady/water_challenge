import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'

import api from '../../api/api'
import { getCookie } from '../../utils/cookies'

const CHALLENGES_ENDPOINT =
  '/challenges/defis/'

const STORAGE_KEYS = {
  SELECTED_CHALLENGE:
    'waterChallengeSelectedChallenge',

  CURRENT_CHALLENGE:
    'waterChallengeCurrentChallenge',
}

/* =========================================================
   UTILITAIRES
   ========================================================= */

const normalizeId = (value) => {
  return String(value ?? '').trim()
}

const getChallengeId = (challenge) => {
  return normalizeId(
    challenge?.id ??
      challenge?.defi_id
  )
}

const getChallengeTitle = (
  challenge
) => {
  const challengeId =
    getChallengeId(challenge)

  return String(
    challenge?.titre ??
      challenge?.title ??
      challenge?.defi_titre ??
      (
        challengeId
          ? `Challenge ${challengeId}`
          : 'Challenge'
      )
  ).trim()
}

const getChallengePoints = (
  challenge
) => {
  const points = Number(
    challenge?.points_recompense ??
      challenge?.points ??
      0
  )

  return Number.isFinite(points)
    ? points
    : 0
}

const normalizeChallenge = (
  challenge
) => {
  if (
    !challenge ||
    typeof challenge !== 'object'
  ) {
    return null
  }

  const id =
    getChallengeId(challenge)

  if (!id) {
    return null
  }

  return {
    ...challenge,
    id,
    titre:
      getChallengeTitle(
        challenge
      ),
    points_recompense:
      getChallengePoints(
        challenge
      ),
  }
}

/*
 * On récupère seulement l'identifiant.
 * Le titre sera toujours repris depuis la liste API.
 */
const readStoredChallengeId = () => {
  if (
    typeof window === 'undefined'
  ) {
    return ''
  }

  const keys = [
    STORAGE_KEYS
      .SELECTED_CHALLENGE,

    STORAGE_KEYS
      .CURRENT_CHALLENGE,
  ]

  for (const key of keys) {
    try {
      const storedValue =
        sessionStorage.getItem(
          key
        )

      if (!storedValue) {
        continue
      }

      const parsedValue =
        JSON.parse(storedValue)

      const challengeId =
        getChallengeId(
          parsedValue
        )

      if (challengeId) {
        return challengeId
      }
    } catch (storageError) {
      console.error(
        'Impossible de lire le challenge enregistré :',
        storageError
      )
    }
  }

  return ''
}

const mergeChallenges = (
  ...challengeLists
) => {
  const challengeMap =
    new Map()

  challengeLists
    .flat()
    .forEach((challenge) => {
      const normalizedChallenge =
        normalizeChallenge(
          challenge
        )

      if (!normalizedChallenge) {
        return
      }

      const challengeId =
        getChallengeId(
          normalizedChallenge
        )

      const existingChallenge =
        challengeMap.get(
          challengeId
        )

      challengeMap.set(
        challengeId,
        {
          ...(existingChallenge ||
            {}),
          ...normalizedChallenge,
        }
      )
    })

  return Array.from(
    challengeMap.values()
  ).sort(
    (
      firstChallenge,
      secondChallenge
    ) => {
      return (
        Number(
          firstChallenge?.ordre ??
            0
        ) -
        Number(
          secondChallenge?.ordre ??
            0
        )
      )
    }
  )
}

/* =========================================================
   COMPOSANT
   ========================================================= */

function SubmitActivitySection({
  t,
  data,
  onAddActivity,
}) {
  const [
    initialChallengeId,
  ] = useState(() =>
    readStoredChallengeId()
  )

  const [
    selectedFromChallenges,
    setSelectedFromChallenges,
  ] = useState(
    Boolean(initialChallengeId)
  )

  const [
    challenges,
    setChallenges,
  ] = useState([])

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [
    isSubmitting,
    setIsSubmitting,
  ] = useState(false)

  const [
    message,
    setMessage,
  ] = useState('')

  const [
    error,
    setError,
  ] = useState('')

  const [
    photos,
    setPhotos,
  ] = useState([])

  const [
    video,
    setVideo,
  ] = useState(null)

  const [
    form,
    setForm,
  ] = useState({
    challengeId:
      initialChallengeId,

    date: '',
    place: '',
    people: '',
    description: '',
  })

  const labels = useMemo(
    () => ({
      title:
        t?.submit?.title ||
        'Soumettre une activité',

      subtitle:
        t?.submit?.subtitle ||
        'Renseignez les informations de votre activité et ajoutez les preuves demandées.',

      challenge:
        t?.submit?.challenge ||
        'Challenge',

      date:
        t?.submit?.date ||
        "Date de l'activité",

      place:
        t?.submit?.place ||
        'Lieu',

      people:
        t?.submit?.people ||
        'Nombre de personnes sensibilisées',

      photo:
        t?.submit?.photo ||
        'Photos',

      video:
        t?.submit?.video ||
        'Vidéo',

      description:
        t?.submit?.description ||
        "Rapport de l'activité",

      fileNote:
        t?.submit?.fileNote ||
        'Ajoutez des fichiers permettant de vérifier votre activité.',

      submitButton:
        t?.submit
          ?.submitButton ||
        'Envoyer la soumission',

      saved:
        t?.submit?.saved ||
        'Votre activité a été soumise avec succès.',
    }),
    [t]
  )

  const fallbackChallenges =
    useMemo(() => {
      return Array.isArray(
        data?.challenges
      )
        ? data.challenges
        : []
    }, [data?.challenges])

  const getAccessToken =
    useCallback(() => {
      return (
        getCookie(
          'accessToken'
        ) ||
        getCookie('access') ||
        ''
      )
    }, [])

  const clearStoredChallenge =
    useCallback(() => {
      try {
        sessionStorage.removeItem(
          STORAGE_KEYS
            .SELECTED_CHALLENGE
        )

        sessionStorage.removeItem(
          STORAGE_KEYS
            .CURRENT_CHALLENGE
        )
      } catch (storageError) {
        console.error(
          'Impossible de supprimer le challenge enregistré :',
          storageError
        )
      }
    }, [])

  /* =======================================================
     CHARGEMENT DES CHALLENGES
     ======================================================= */

  const loadChallenges =
    useCallback(async () => {
      setIsLoading(true)
      setError('')

      try {
        const accessToken =
          getAccessToken()

        const response =
          await api.get(
            CHALLENGES_ENDPOINT,
            {
              headers:
                accessToken
                  ? {
                      Authorization:
                        `Bearer ${accessToken}`,
                    }
                  : {},
            }
          )

        const responseData =
          response?.data || {}

        if (
          responseData.success ===
          false
        ) {
          throw new Error(
            responseData.erreur ||
              responseData.detail ||
              responseData.message ||
              'Impossible de charger les challenges.'
          )
        }

        const apiChallenges =
          Array.isArray(
            responseData.defis
          )
            ? responseData.defis
            : Array.isArray(
                responseData
                  .challenges
              )
              ? responseData
                  .challenges
              : Array.isArray(
                  responseData
                    .results
                )
                ? responseData
                    .results
                : []

        /*
         * L'API est placée après les données locales :
         * ses vrais titres remplacent donc les titres
         * éventuellement statiques de data.challenges.
         */
        const mergedChallenges =
          mergeChallenges(
            fallbackChallenges,
            apiChallenges
          )

        setChallenges(
          mergedChallenges
        )

        if (
          initialChallengeId
        ) {
          const challengeExists =
            mergedChallenges.some(
              (challenge) =>
                getChallengeId(
                  challenge
                ) ===
                initialChallengeId
            )

          if (challengeExists) {
            setForm(
              (previous) => ({
                ...previous,

                challengeId:
                  initialChallengeId,
              })
            )

            setSelectedFromChallenges(
              true
            )
          } else {
            /*
             * Le challenge enregistré n'existe plus :
             * on affiche alors la liste normalement.
             */
            clearStoredChallenge()

            setSelectedFromChallenges(
              false
            )

            setForm(
              (previous) => ({
                ...previous,
                challengeId: '',
              })
            )
          }
        }
      } catch (requestError) {
        console.error(
          'Erreur de chargement des challenges :',
          requestError
        )

        const localChallenges =
          mergeChallenges(
            fallbackChallenges
          )

        setChallenges(
          localChallenges
        )

        const storedChallengeExists =
          localChallenges.some(
            (challenge) =>
              getChallengeId(
                challenge
              ) ===
              initialChallengeId
          )

        if (
          initialChallengeId &&
          storedChallengeExists
        ) {
          setForm(
            (previous) => ({
              ...previous,

              challengeId:
                initialChallengeId,
            })
          )
        } else {
          clearStoredChallenge()

          setSelectedFromChallenges(
            false
          )

          setForm(
            (previous) => ({
              ...previous,
              challengeId: '',
            })
          )
        }

        if (
          localChallenges.length ===
          0
        ) {
          const responseData =
            requestError?.response
              ?.data

          setError(
            responseData?.erreur ||
              responseData?.detail ||
              responseData?.message ||
              requestError?.message ||
              'Impossible de charger les challenges.'
          )
        }
      } finally {
        setIsLoading(false)
      }
    }, [
      clearStoredChallenge,
      fallbackChallenges,
      getAccessToken,
      initialChallengeId,
    ])

  useEffect(() => {
    loadChallenges()
  }, [loadChallenges])

  /* =======================================================
     CHALLENGE SÉLECTIONNÉ
     ======================================================= */

  const selectedChallenge =
    useMemo(() => {
      return (
        challenges.find(
          (challenge) =>
            getChallengeId(
              challenge
            ) ===
            normalizeId(
              form.challengeId
            )
        ) || null
      )
    }, [
      challenges,
      form.challengeId,
    ])

  const minimumPhotos =
    Math.max(
      0,
      Number(
        selectedChallenge
          ?.nombre_photos_min ??
          0
      ) || 0
    )

  const receivedMaximumPhotos =
    Number(
      selectedChallenge
        ?.nombre_photos_max ??
        0
    ) || 0

  const maximumPhotos =
    receivedMaximumPhotos > 0
      ? receivedMaximumPhotos
      : null

  const videoIsRequired =
    Boolean(
      selectedChallenge
        ?.video_obligatoire
    )

  /* =======================================================
     FORMULAIRE
     ======================================================= */

  const handleChange =
    useCallback((event) => {
      const {
        name,
        value,
      } = event.target

      setForm(
        (previous) => ({
          ...previous,
          [name]: value,
        })
      )

      setMessage('')
      setError('')
    }, [])

  const handleChallengeChange =
    useCallback((event) => {
      const challengeId =
        event.target.value

      setForm(
        (previous) => ({
          ...previous,
          challengeId,
        })
      )

      setPhotos([])
      setVideo(null)
      setMessage('')
      setError('')

      const photosInput =
        document.getElementById(
          'activity-photos'
        )

      const videoInput =
        document.getElementById(
          'activity-video'
        )

      if (photosInput) {
        photosInput.value = ''
      }

      if (videoInput) {
        videoInput.value = ''
      }
    }, [])

  const handlePhotosChange =
    useCallback((event) => {
      setPhotos(
        Array.from(
          event.target.files ||
            []
        )
      )

      setMessage('')
      setError('')
    }, [])

  const handleVideoChange =
    useCallback((event) => {
      setVideo(
        event.target.files?.[0] ||
          null
      )

      setMessage('')
      setError('')
    }, [])

  const validateForm =
    useCallback(() => {
      if (!form.challengeId) {
        return 'Sélectionnez un challenge.'
      }

      if (!selectedChallenge) {
        return 'Le challenge sélectionné est introuvable.'
      }

      if (!form.date) {
        return "Indiquez la date de l'activité."
      }

      if (!form.place.trim()) {
        return "Indiquez le lieu de l'activité."
      }

      if (
        form.people === '' ||
        Number(form.people) < 0
      ) {
        return 'Indiquez un nombre de personnes valide.'
      }

      if (
        !form.description.trim()
      ) {
        return "Décrivez l'activité réalisée."
      }

      if (
        photos.length <
        minimumPhotos
      ) {
        return (
          `Ajoutez au moins ${minimumPhotos} photo` +
          `${minimumPhotos > 1 ? 's' : ''}.`
        )
      }

      if (
        maximumPhotos !== null &&
        photos.length >
          maximumPhotos
      ) {
        return (
          `Vous pouvez ajouter au maximum ${maximumPhotos} photo` +
          `${maximumPhotos > 1 ? 's' : ''}.`
        )
      }

      if (
        videoIsRequired &&
        !video
      ) {
        return 'Ajoutez la vidéo demandée pour ce challenge.'
      }

      return ''
    }, [
      form.challengeId,
      form.date,
      form.description,
      form.people,
      form.place,
      maximumPhotos,
      minimumPhotos,
      photos.length,
      selectedChallenge,
      video,
      videoIsRequired,
    ])

  /* =======================================================
     SOUMISSION
     ======================================================= */

  const handleSubmit =
    useCallback(
      async (event) => {
        event.preventDefault()

        const validationError =
          validateForm()

        if (validationError) {
          setError(
            validationError
          )

          setMessage('')
          return
        }

        setIsSubmitting(true)
        setError('')
        setMessage('')

        try {
          const accessToken =
            getAccessToken()

          if (!accessToken) {
            throw new Error(
              'Votre session a expiré. Veuillez vous reconnecter.'
            )
          }

          const payload =
            new FormData()

          payload.append(
            'rapport',
            form.description.trim()
          )

          payload.append(
            'date_activite',
            form.date
          )

          payload.append(
            'lieu',
            form.place.trim()
          )

          payload.append(
            'nombre_personnes_sensibilisees',
            String(
              Number(
                form.people
              ) || 0
            )
          )

          photos.forEach(
            (photo) => {
              payload.append(
                'photos',
                photo
              )
            }
          )

          if (video) {
            payload.append(
              'video',
              video
            )
          }

          const response =
            await api.post(
              `/challenges/defis/${encodeURIComponent(
                form.challengeId
              )}/soumettre/`,

              payload,

              {
                headers: {
                  Authorization:
                    `Bearer ${accessToken}`,
                },
              }
            )

          const responseData =
            response?.data || {}

          if (
            responseData.success ===
            false
          ) {
            throw new Error(
              responseData.erreur ||
                responseData.detail ||
                responseData.message ||
                'Impossible d’envoyer la soumission.'
            )
          }

          const submission =
            responseData.soumission ||
            {}

          if (
            typeof onAddActivity ===
            'function'
          ) {
            onAddActivity({
              id:
                submission.id ||
                `activity-${Date.now()}`,

              challengeId:
                form.challengeId,

              challengeTitle:
                submission.defi_titre ||
                getChallengeTitle(
                  selectedChallenge
                ),

              points:
                submission.validation
                  ?.points_attribues ??
                getChallengePoints(
                  selectedChallenge
                ),

              date:
                submission.date_activite ||
                form.date,

              place:
                submission.lieu ||
                form.place.trim(),

              people:
                submission
                  .nombre_personnes_sensibilisees ??
                Number(
                  form.people
                ) ??
                0,

              description:
                submission.rapport ||
                form.description.trim(),

              photos:
                submission.photos ||
                [],

              videoUrl:
                submission.video_url ||
                '',

              status:
                submission.statut ||
                'en_attente',

              submission,
            })
          }

          setMessage(
            responseData.message ||
              labels.saved
          )

          clearStoredChallenge()

          setSelectedFromChallenges(
            false
          )

          setForm({
            challengeId: '',
            date: '',
            place: '',
            people: '',
            description: '',
          })

          setPhotos([])
          setVideo(null)

          const photosInput =
            document.getElementById(
              'activity-photos'
            )

          const videoInput =
            document.getElementById(
              'activity-video'
            )

          if (photosInput) {
            photosInput.value = ''
          }

          if (videoInput) {
            videoInput.value = ''
          }
        } catch (requestError) {
          console.error(
            'Erreur pendant la soumission :',
            requestError
          )

          const responseData =
            requestError?.response
              ?.data

          setError(
            responseData?.erreur ||
              responseData?.detail ||
              responseData?.message ||
              requestError?.message ||
              'Impossible d’envoyer la soumission.'
          )
        } finally {
          setIsSubmitting(false)
        }
      },
      [
        clearStoredChallenge,
        form,
        getAccessToken,
        labels.saved,
        onAddActivity,
        photos,
        selectedChallenge,
        validateForm,
        video,
      ]
    )

  /* =======================================================
     AFFICHAGE
     ======================================================= */

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <h1>
            {labels.title}
          </h1>

          <p>
            {labels.subtitle}
          </p>
        </div>
      </div>

      {message && (
        <div className="activity-item validated">
          <h3>
            ✅ {message}
          </h3>

          <p>
            {labels.fileNote}
          </p>
        </div>
      )}

      {error && (
        <div
          className="activity-item rejected"
          role="alert"
        >
          <h3>
            ⚠️ Une erreur est survenue
          </h3>

          <p>{error}</p>
        </div>
      )}

      <div className="dash-form-card">
        <form
          className="dash-form"
          onSubmit={handleSubmit}
        >
          <div className="dash-form-grid">
            <div className="dash-form-group full">
              <label htmlFor="challengeId">
                {labels.challenge}
              </label>

              <select
                id="challengeId"
                name="challengeId"
                value={
                  form.challengeId
                }
                onChange={
                  handleChallengeChange
                }
                disabled={
                  isLoading ||
                  selectedFromChallenges
                }
                required
              >
                <option value="">
                  {isLoading
                    ? 'Chargement des challenges...'
                    : 'Sélectionner un challenge'}
                </option>

                {challenges.map(
                  (challenge) => {
                    const challengeId =
                      getChallengeId(
                        challenge
                      )

                    return (
                      <option
                        value={
                          challengeId
                        }
                        key={
                          challengeId
                        }
                      >
                        {getChallengeTitle(
                          challenge
                        )}
                        {' — '}
                        {getChallengePoints(
                          challenge
                        )}{' '}
                        pts
                      </option>
                    )
                  }
                )}
              </select>

              {selectedFromChallenges && (
                <p className="dash-form-note">
                  Ce challenge a été sélectionné depuis la page Challenges.
                </p>
              )}

              {!selectedFromChallenges &&
                !isLoading &&
                challenges.length ===
                  0 && (
                  <p className="dash-form-note">
                    Aucun challenge disponible.
                  </p>
                )}
            </div>

            <div className="dash-form-group">
              <label htmlFor="activity-date">
                {labels.date}
              </label>

              <input
                id="activity-date"
                type="date"
                name="date"
                value={form.date}
                onChange={handleChange}
                required
              />
            </div>

            <div className="dash-form-group">
              <label htmlFor="activity-place">
                {labels.place}
              </label>

              <input
                id="activity-place"
                type="text"
                name="place"
                value={form.place}
                onChange={handleChange}
                placeholder="Ex : Fianarantsoa"
                required
              />
            </div>

            <div className="dash-form-group">
              <label htmlFor="activity-people">
                {labels.people}
              </label>

              <input
                id="activity-people"
                type="number"
                min="0"
                name="people"
                value={form.people}
                onChange={handleChange}
                placeholder="Ex : 12"
                required
              />
            </div>

            <div className="dash-form-group">
              <label htmlFor="activity-photos">
                {labels.photo}

                {minimumPhotos > 0
                  ? ` — minimum ${minimumPhotos}`
                  : ''}

                {maximumPhotos !== null
                  ? `, maximum ${maximumPhotos}`
                  : ''}
              </label>

              <input
                id="activity-photos"
                type="file"
                accept="image/*"
                multiple
                onChange={
                  handlePhotosChange
                }
                required={
                  minimumPhotos > 0
                }
              />

              {photos.length > 0 && (
                <p className="dash-form-note">
                  {photos.length}{' '}
                  photo
                  {photos.length > 1
                    ? 's'
                    : ''}{' '}
                  sélectionnée
                  {photos.length > 1
                    ? 's'
                    : ''}
                </p>
              )}
            </div>

            <div className="dash-form-group">
              <label htmlFor="activity-video">
                {labels.video}

                {videoIsRequired
                  ? ' — demandée'
                  : ''}
              </label>

              <input
                id="activity-video"
                type="file"
                accept="video/*"
                onChange={
                  handleVideoChange
                }
                required={
                  videoIsRequired
                }
              />

              {video && (
                <p className="dash-form-note">
                  {video.name}
                </p>
              )}
            </div>

            <div className="dash-form-group full">
              <label htmlFor="activity-description">
                {labels.description}
              </label>

              <textarea
                id="activity-description"
                name="description"
                value={
                  form.description
                }
                onChange={handleChange}
                placeholder="Décris ce que tu as fait, les personnes impliquées et l’impact observé..."
                required
              />
            </div>
          </div>

          <p className="dash-form-note">
            {labels.fileNote}
          </p>

          <button
            type="submit"
            className="dash-primary-btn"
            disabled={
              isSubmitting ||
              isLoading ||
              !form.challengeId
            }
          >
            {isSubmitting
              ? 'Envoi en cours...'
              : labels.submitButton}
          </button>
        </form>
      </div>
    </section>
  )
}

export default SubmitActivitySection