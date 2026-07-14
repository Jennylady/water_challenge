import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import api from '../api/api'
import './SignupPage.css'

function SignupPage({ onNavigate }) {
  const [language, setLanguage] = useState('FR')
  const [currentStep, setCurrentStep] = useState(1)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [isLoading, setIsLoading] = useState(false)
  const [devConfirmationLink, setDevConfirmationLink] = useState('')
  const [signupSuccess, setSignupSuccess] = useState(false)
  const [successEmail, setSuccessEmail] = useState('')
  const [isResending, setIsResending] = useState(false)
  const [resendMessage, setResendMessage] = useState({ type: '', text: '' })

  const formRef = useRef(null)

  const initialFormData = {
    nom: '',
    prenom: '',
    email: '',
    motDePasse: '',
    confirmationMotDePasse: '',
    telephone: '',
    dateNaissance: '',
    scoutType: '',
    section: '',
    sampana: '',
    position: '',
    fivondronana: '',
    faritra: '',
    diosezy: '',
  }

  const [formData, setFormData] = useState(initialFormData)

  // Non-scout users don't need the location (Faritra / Fivondronana / Diosezy) step
  const isNonScout = formData.scoutType === 'non-scout'
  const totalSteps = isNonScout ? 2 : 3

  const scoutOptions = {
    FR: [
      { value: 'fanilon', label: "Fanilon'i Madagasikara" },
      { value: 'mpanazavan', label: "Mpanazavan'I Madagasikara" },
      { value: 'kiadin', label: "Kiadin'I Madagasikara" },
      { value: 'antilin', label: "Antilin'i Madagasikara" },
      { value: 'tilin', label: "Tilin'i Madagasikara" },
      { value: 'non-scout', label: 'Je ne suis pas scout' },
      { value: 'autre', label: 'Autre' },
    ],
    MLG: [
      { value: 'fanilon', label: "Fanilon'i Madagasikara" },
      { value: 'mpanazavan', label: "Mpanazavan'I Madagasikara" },
      { value: 'kiadin', label: "Kiadin'I Madagasikara" },
      { value: 'antilin', label: "Antilin'i Madagasikara" },
      { value: 'tilin', label: "Tilin'i Madagasikara" },
      { value: 'non-scout', label: 'Tsy scout aho' },
      { value: 'autre', label: 'Hafa' },
    ],
  }

  const sections = {
    FR: {
      mavo: 'Bleu (Mavo)',
      maitso: 'Vert (Maitso)',
      mena: 'Rouge (Mena)',
      cheftaine: 'Cheftaine',
    },
    MLG: {
      mavo: 'Bleu (Mavo)',
      maitso: 'Vert (Maitso)',
      mena: 'Rouge (Mena)',
      cheftaine: 'Cheftaine',
    },
  }

  const positions = {
    FR: {
      cheftaine: 'Cheftaine',
      tonia: 'Tonia',
      filoha: 'Filoha',
      beazina: 'Beazina',
      eleve: 'Élève',
    },
    MLG: {
      cheftaine: 'Cheftaine',
      tonia: 'Tonia',
      filoha: 'Filoha',
      beazina: 'Beazina',
      eleve: 'Mpianatra',
    },
  }

  // Different position options for users who are not scouts
  const nonScoutPositions = {
    FR: {
      etudiant: 'Étudiant',
      association: 'Association',
      professionnel: 'Professionnel',
      autre: 'Autre',
    },
    MLG: {
      etudiant: 'Mpianatra',
      association: 'Fikambanana',
      professionnel: 'Matihanina',
      autre: 'Hafa',
    },
  }

  const content = {
    FR: {
      title: 'Créer un compte',
      step1: 'Informations personnelles',
      step2: 'Informations de scout',
      step3: 'Localisation',

      nomLabel: 'Nom',
      prenomLabel: 'Prénom',
      emailLabel: 'Email',
      passwordLabel: 'Mot de passe',
      confirmPasswordLabel: 'Confirmer le mot de passe',
      telephoneLabel: 'Téléphone',
      dateNaissanceLabel: 'Date de naissance',

      scoutTypeLabel: 'Guide et Scout',
      sectionLabel: 'Section (Sampana)',
      positionLabel: 'Position',

      fivondronanaLabel: 'Fivondronana (District)',
      faritraLabel: 'Faritra (Région)',
      diosezLabel: 'Diosezy (Diocèse)',

      nextBtn: 'Suivant',
      backBtn: 'Retour',
      signupBtn: "S'inscrire",
      loadingBtn: 'Création du compte...',
      loginLink: 'Vous avez déjà un compte ? Se connecter',
      selectOption: 'Choisir une option',

      passwordPlaceholder: 'Minimum 8 caractères',
      confirmPasswordPlaceholder: 'Confirmer le mot de passe',

      requiredError: 'Veuillez remplir tous les champs obligatoires.',
      passwordLengthError: 'Le mot de passe doit contenir au moins 8 caractères.',
      passwordMatchError: 'Les mots de passe ne correspondent pas.',
      successMessage:
        'Compte créé avec succès. Vérifiez votre email pour confirmer votre compte avant de vous connecter.',
      networkError:
        'Impossible de contacter le serveur. Vérifiez que Django est lancé.',
      devLinkText: 'Mode développement : lien de confirmation disponible.',
      devLinkBtn: 'Ouvrir le lien de confirmation',

      // Success / email confirmation screen
      successTitle: 'Vérifiez votre boîte mail',
      successText: 'Un lien d’activation a été envoyé à',
      successSubText:
        'Cliquez sur ce lien pour activer votre compte avant de vous connecter.',
      resendBtn: "Renvoyer l'email",
      resendLoadingBtn: 'Envoi en cours...',
      resendSuccess: 'Email renvoyé avec succès.',
      resendError: "Impossible de renvoyer l'email. Réessayez plus tard.",
      backToLoginBtn: 'Retour à la connexion',
      newSignupBtn: "S'inscrire avec un autre compte",
    },

    MLG: {
      title: 'Famoronana kaonty',
      step1: 'Fampahalalana momba ny tena',
      step2: 'Fampahalalana momba ny Scout',
      step3: 'Toerana',

      nomLabel: 'Anarana',
      prenomLabel: 'Fanampin’anarana',
      emailLabel: 'Email',
      passwordLabel: 'Teny miafina',
      confirmPasswordLabel: 'Hamafiso ny teny miafina',
      telephoneLabel: 'Telefôna',
      dateNaissanceLabel: 'Andro nahaterahana',

      scoutTypeLabel: 'Guide sy Scout',
      sectionLabel: 'Sampana',
      positionLabel: 'Toerana andraikitra',

      fivondronanaLabel: 'Fivondronana',
      faritraLabel: 'Faritra',
      diosezLabel: 'Diosezy',

      nextBtn: 'Manaraka',
      backBtn: 'Miverina',
      signupBtn: 'Hisoratra',
      loadingBtn: 'Mamora kaonty...',
      loginLink: 'Manana kaonty ve ? Hiditra',
      selectOption: 'Misafidiana',

      passwordPlaceholder: 'Tarehintsoratra 8 farafahakeliny',
      confirmPasswordPlaceholder: 'Hamafiso ny teny miafina',

      requiredError: 'Fenoy daholo ireo saha ilaina.',
      passwordLengthError:
        'Tsy maintsy manana tarehintsoratra 8 farafahakeliny ny teny miafina.',
      passwordMatchError: 'Tsy mitovy ny teny miafina.',
      successMessage:
        'Vita soa aman-tsara ny fisoratana. Jereo ny email-nao hanamarinana ny kaonty.',
      networkError:
        'Tsy afaka mifandray amin’ny serveur. Alefaso aloha Django.',
      devLinkText: 'Mode développement : misy rohy fanamarinana.',
      devLinkBtn: 'Sokafy ny rohy fanamarinana',

      // Success / email confirmation screen
      successTitle: 'Jereo ny email-nao',
      successText: 'Misy rohy fanamarinana nalefa tany amin\'ny',
      successSubText:
        'Tsindrio io rohy io mba hanamarinana ny kaontinao alohan\'ny hidiranao.',
      resendBtn: 'Alefaso indray ny email',
      resendLoadingBtn: 'Mandefa...',
      resendSuccess: 'Voalefa soa aman-tsara ny email.',
      resendError: 'Tsy afaka mandefa ny email. Andramo indray afaka kelikely.',
      backToLoginBtn: 'Hiverina hiditra',
      newSignupBtn: 'Hisoratra amin\'ny kaonty hafa',
    },
  }

  const t = content[language]

  const showMessage = (type, text) => {
    setMessage({ type, text })
  }

  const clearMessage = () => {
    setMessage({ type: '', text: '' })
    setDevConfirmationLink('')
  }

  const handleChange = (e) => {
    const { name, value } = e.target

    setFormData((prev) => ({
      ...prev,
      [name]: value,
      // Position options differ between scout / non-scout, so reset it on type change
      ...(name === 'scoutType' ? { position: '' } : {}),
    }))

    clearMessage()
  }

  // If the user switches to "non-scout" while sitting on the (now hidden)
  // location step, bring them back to the last available step.
  useEffect(() => {
    if (isNonScout && currentStep > totalSteps) {
      setCurrentStep(totalSteps)
    }
  }, [isNonScout, currentStep, totalSteps])

  const validateStepOne = () => {
    const requiredFields = [
      formData.nom,
      formData.prenom,
      formData.email,
      formData.motDePasse,
      formData.confirmationMotDePasse,
      formData.telephone,
      formData.dateNaissance,
    ]

    const hasEmptyField = requiredFields.some((field) => !String(field).trim())

    if (hasEmptyField) {
      showMessage('error', t.requiredError)
      return false
    }

    if (formData.motDePasse.length < 8) {
      showMessage('error', t.passwordLengthError)
      return false
    }

    if (formData.motDePasse !== formData.confirmationMotDePasse) {
      showMessage('error', t.passwordMatchError)
      return false
    }

    return true
  }

  const validateStepTwo = () => {
    if (!formData.scoutType || !formData.section || !formData.position) {
      showMessage('error', t.requiredError)
      return false
    }

    return true
  }

  const validateStepThree = () => {
    // Non-scout users skip the location requirement entirely
    if (isNonScout) return true

    if (!formData.faritra.trim() || !formData.fivondronana.trim()) {
      showMessage('error', t.requiredError)
      return false
    }

    return true
  }

  const validateCurrentStep = () => {
    clearMessage()

    if (formRef.current && !formRef.current.reportValidity()) {
      return false
    }

    if (currentStep === 1) return validateStepOne()
    if (currentStep === 2) return validateStepTwo()
    if (currentStep === 3) return validateStepThree()

    return true
  }

  const validateAllSteps = () => {
    if (!validateStepOne()) {
      setCurrentStep(1)
      return false
    }

    if (!validateStepTwo()) {
      setCurrentStep(2)
      return false
    }

    if (!isNonScout && !validateStepThree()) {
      setCurrentStep(3)
      return false
    }

    return true
  }

  const handleNextStep = () => {
    if (!validateCurrentStep()) return
    setCurrentStep((prev) => prev + 1)
  }

  const handlePreviousStep = () => {
    clearMessage()
    setCurrentStep((prev) => prev - 1)
  }

  const resetForm = () => {
    setFormData(initialFormData)
    setCurrentStep(1)
  }

  const extractApiError = (error) => {
    const data = error?.response?.data

    if (!data) {
      return t.networkError
    }

    if (typeof data === 'string') {
      return data
    }

    if (data.message) {
      return data.message
    }

    if (data.detail) {
      return data.detail
    }

    if (data.non_field_errors) {
      return Array.isArray(data.non_field_errors)
        ? data.non_field_errors.join(' ')
        : data.non_field_errors
    }

    const fieldErrors = Object.entries(data)
      .map(([field, value]) => {
        if (Array.isArray(value)) return `${field}: ${value.join(' ')}`
        if (typeof value === 'object') return `${field}: ${JSON.stringify(value)}`
        return `${field}: ${value}`
      })
      .join(' ')

    return fieldErrors || t.networkError
  }

  const buildRegisterPayload = () => {
    return {
      email: formData.email.trim().toLowerCase(),
      first_name: formData.prenom.trim(),
      last_name: formData.nom.trim(),
      phone: formData.telephone.trim(),
      birth_date: formData.dateNaissance,

      password: formData.motDePasse,
      password_confirm: formData.confirmationMotDePasse,

      scout_type: formData.scoutType,
      section: formData.section,
      sampana: isNonScout ? '' : formData.sampana || '',
      position: formData.position,

      // Location is irrelevant for non-scout accounts
      fivondronana: isNonScout ? '' : formData.fivondronana.trim(),
      faritra: isNonScout ? '' : formData.faritra.trim(),
      diosezy: isNonScout ? '' : formData.diosezy.trim(),
    }
  }

  const openDevConfirmationLink = () => {
    if (!devConfirmationLink) return

    try {
      const url = new URL(devConfirmationLink)
      window.history.pushState({}, '', url.pathname)
      window.dispatchEvent(new Event('popstate'))
    } catch (error) {
      window.location.href = devConfirmationLink
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    clearMessage()

    if (!validateAllSteps()) return

    try {
      setIsLoading(true)

      const payload = buildRegisterPayload()
      const response = await api.post('/auth/register/', payload)

      const emailUsed = payload.email

      if (response.data?.dev_confirmation_link) {
        setDevConfirmationLink(response.data.dev_confirmation_link)
      }

      setSuccessEmail(emailUsed)
      setSignupSuccess(true)
      resetForm()
    } catch (error) {
      showMessage('error', extractApiError(error))
    } finally {
      setIsLoading(false)
    }
  }

  const handleResendEmail = async () => {
    if (!successEmail || isResending) return

    setResendMessage({ type: '', text: '' })

    try {
      setIsResending(true)
      await api.post('/auth/resend-confirmation/', { email: successEmail })
      setResendMessage({ type: 'success', text: t.resendSuccess })
    } catch (error) {
      setResendMessage({
        type: 'error',
        text: error?.response?.data?.message || t.resendError,
      })
    } finally {
      setIsResending(false)
    }
  }

  const handleNewSignup = () => {
    setSignupSuccess(false)
    setSuccessEmail('')
    setDevConfirmationLink('')
    setResendMessage({ type: '', text: '' })
    resetForm()
  }

  return (
    <div className="signup-page">
      <motion.button
        className="back-arrow-btn"
        onClick={() => onNavigate('landing')}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        type="button"
        title="Retour"
        disabled={isLoading}
      >
        ←
      </motion.button>

      <motion.div
        className="signup-container"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65, delay: 0.2 }}
      >
        <div className="signup-box">
          <div className="form-header">
            <div
              className="signup-logo"
              onClick={() => !isLoading && onNavigate('landing')}
            >
              <span className="signup-logo-mark">W</span>
              <span>Water Challenge</span>
            </div>

            <div className="signup-language">
              <button
                type="button"
                className={language === 'FR' ? 'active' : ''}
                onClick={() => setLanguage('FR')}
                disabled={isLoading}
              >
                FR
              </button>

              <button
                type="button"
                className={language === 'MLG' ? 'active' : ''}
                onClick={() => setLanguage('MLG')}
                disabled={isLoading}
              >
                MLG
              </button>
            </div>
          </div>

          {signupSuccess ? (
            // ---------- SUCCESS / CHECK YOUR EMAIL VIEW ----------
            <motion.div
              className="signup-success"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <div className="signup-success-icon">✓</div>

              <h1>{t.successTitle}</h1>

              <p className="signup-success-text">
                {t.successText} <strong>{successEmail}</strong>.
              </p>
              <p className="signup-success-subtext">{t.successSubText}</p>

              <AnimatePresence>
                {resendMessage.text && (
                  <motion.div
                    className={`signup-message ${resendMessage.type}`}
                    initial={{ opacity: 0, y: -8, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -8, scale: 0.98 }}
                    transition={{ duration: 0.25 }}
                  >
                    {resendMessage.text}
                  </motion.div>
                )}
              </AnimatePresence>

              {devConfirmationLink && (
                <div className="dev-confirmation-box">
                  <p>{t.devLinkText}</p>
                  <button
                    type="button"
                    className="link-btn"
                    onClick={openDevConfirmationLink}
                  >
                    {t.devLinkBtn}
                  </button>
                </div>
              )}

              <button
                type="button"
                className="btn-primary resend-btn"
                onClick={handleResendEmail}
                disabled={isResending}
              >
                {isResending ? (
                  <span className="btn-loader-content">
                    <span className="signup-loader"></span>
                    {t.resendLoadingBtn}
                  </span>
                ) : (
                  t.resendBtn
                )}
              </button>

              <div className="signup-footer">
                <button
                  type="button"
                  className="link-btn"
                  onClick={() => onNavigate('login')}
                >
                  {t.backToLoginBtn}
                </button>

                <button
                  type="button"
                  className="link-btn"
                  onClick={handleNewSignup}
                >
                  {t.newSignupBtn}
                </button>
              </div>
            </motion.div>
          ) : (
            // ---------- SIGNUP FORM ----------
            <>
              <h1>{t.title}</h1>

              <div className="signup-progress">
                <div className={`progress-step ${currentStep >= 1 ? 'active' : ''}`}>
                  <span>1</span>
                  <p>{t.step1}</p>
                </div>

                <div className={`progress-step ${currentStep >= 2 ? 'active' : ''}`}>
                  <span>2</span>
                  <p>{t.step2}</p>
                </div>

                {!isNonScout && (
                  <div className={`progress-step ${currentStep >= 3 ? 'active' : ''}`}>
                    <span>3</span>
                    <p>{t.step3}</p>
                  </div>
                )}
              </div>

              <AnimatePresence>
                {message.text && (
                  <motion.div
                    className={`signup-message ${message.type}`}
                    initial={{ opacity: 0, y: -8, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -8, scale: 0.98 }}
                    transition={{ duration: 0.25 }}
                  >
                    {message.text}
                  </motion.div>
                )}
              </AnimatePresence>

              <form ref={formRef} onSubmit={handleSubmit} className="signup-form">
                {currentStep === 1 && (
                  <motion.div
                    className="form-step"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4 }}
                  >
                    <div className="form-row">
                      <div className="form-group">
                        <label>{t.nomLabel}</label>
                        <input
                          type="text"
                          name="nom"
                          value={formData.nom}
                          onChange={handleChange}
                          placeholder="Dupont"
                          required
                          disabled={isLoading}
                        />
                      </div>

                      <div className="form-group">
                        <label>{t.prenomLabel}</label>
                        <input
                          type="text"
                          name="prenom"
                          value={formData.prenom}
                          onChange={handleChange}
                          placeholder="Jean"
                          required
                          disabled={isLoading}
                        />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>{t.emailLabel}</label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="email@example.com"
                        required
                        disabled={isLoading}
                      />
                    </div>

                    <div className="form-row">
                      <div className="form-group">
                        <label>{t.passwordLabel}</label>
                        <input
                          type="password"
                          name="motDePasse"
                          value={formData.motDePasse}
                          onChange={handleChange}
                          placeholder={t.passwordPlaceholder}
                          minLength="8"
                          required
                          disabled={isLoading}
                        />
                      </div>

                      <div className="form-group">
                        <label>{t.confirmPasswordLabel}</label>
                        <input
                          type="password"
                          name="confirmationMotDePasse"
                          value={formData.confirmationMotDePasse}
                          onChange={handleChange}
                          placeholder={t.confirmPasswordPlaceholder}
                          minLength="8"
                          required
                          disabled={isLoading}
                        />
                      </div>
                    </div>

                    <div className="form-row">
                      <div className="form-group">
                        <label>{t.telephoneLabel}</label>
                        <input
                          type="tel"
                          name="telephone"
                          value={formData.telephone}
                          onChange={handleChange}
                          placeholder="+261 XX XXX XXXX"
                          required
                          disabled={isLoading}
                        />
                      </div>

                      <div className="form-group">
                        <label>{t.dateNaissanceLabel}</label>
                        <input
                          type="date"
                          name="dateNaissance"
                          value={formData.dateNaissance}
                          onChange={handleChange}
                          required
                          disabled={isLoading}
                        />
                      </div>
                    </div>
                  </motion.div>
                )}

                {currentStep === 2 && (
                  <motion.div
                    className="form-step"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4 }}
                  >
                    <div className="form-group">
                      <label>{t.scoutTypeLabel}</label>
                      <select
                        name="scoutType"
                        value={formData.scoutType}
                        onChange={handleChange}
                        required
                        disabled={isLoading}
                      >
                        <option value="">{t.selectOption}</option>

                        {scoutOptions[language].map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="form-row">
                      <div className="form-group">
                        <label>{t.sectionLabel}</label>
                        <select
                          name="section"
                          value={formData.section}
                          onChange={handleChange}
                          required
                          disabled={isLoading}
                        >
                          <option value="">{t.selectOption}</option>

                          {Object.entries(sections[language]).map(([key, val]) => (
                            <option key={key} value={key}>
                              {val}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="form-group">
                        <label>{t.positionLabel}</label>
                        <select
                          name="position"
                          value={formData.position}
                          onChange={handleChange}
                          required
                          disabled={isLoading}
                        >
                          <option value="">{t.selectOption}</option>

                          {Object.entries(
                            isNonScout ? nonScoutPositions[language] : positions[language]
                          ).map(([key, val]) => (
                            <option key={key} value={key}>
                              {val}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </motion.div>
                )}

                {currentStep === 3 && !isNonScout && (
                  <motion.div
                    className="form-step"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4 }}
                  >
                    <div className="form-group">
                      <label>{t.faritraLabel}</label>
                      <input
                        type="text"
                        name="faritra"
                        value={formData.faritra}
                        onChange={handleChange}
                        placeholder="Ex: Analamanga"
                        required
                        disabled={isLoading}
                      />
                    </div>

                    <div className="form-group">
                      <label>{t.fivondronanaLabel}</label>
                      <input
                        type="text"
                        name="fivondronana"
                        value={formData.fivondronana}
                        onChange={handleChange}
                        placeholder="Ex: Antananarivo"
                        required
                        disabled={isLoading}
                      />
                    </div>

                    <div className="form-group">
                      <label>{t.diosezLabel}</label>
                      <input
                        type="text"
                        name="diosezy"
                        value={formData.diosezy}
                        onChange={handleChange}
                        placeholder="Ex: Antananarivo"
                        disabled={isLoading}
                      />
                    </div>
                  </motion.div>
                )}

                <div className="form-buttons">
                  {currentStep > 1 && (
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={handlePreviousStep}
                      disabled={isLoading}
                    >
                      {t.backBtn}
                    </button>
                  )}

                  {currentStep < totalSteps && (
                    <button
                      type="button"
                      className="btn-primary"
                      onClick={handleNextStep}
                      disabled={isLoading}
                    >
                      {t.nextBtn}
                    </button>
                  )}

                  {currentStep === totalSteps && (
                    <button
                      type="submit"
                      className="btn-primary"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <span className="btn-loader-content">
                          <span className="signup-loader"></span>
                          {t.loadingBtn}
                        </span>
                      ) : (
                        t.signupBtn
                      )}
                    </button>
                  )}
                </div>
              </form>

              <div className="signup-footer">
                <button
                  type="button"
                  className="link-btn"
                  onClick={() => onNavigate('login')}
                  disabled={isLoading}
                >
                  {t.loginLink}
                </button>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  )
}

export default SignupPage