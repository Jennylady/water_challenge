import {
  useMemo,
  useState,
} from 'react'

import './HelpSection.css'

function HelpSection({
  language = 'FR',
}) {
  const [
    openQuestion,
    setOpenQuestion,
  ] = useState(0)

  const content = useMemo(() => {
    if (language === 'MLG') {
      return {
        kicker: 'Fanohanana',

        title: 'Fanampiana',

        subtitle:
          'Mitadiava valiny sy fanampiana momba ny fampiasana ny Water Challenge.',

        contactTitle:
          'Mila fanampiana fanampiny ve ianao?',

        contactText:
          'Mifandraisa amin’ny ekipan’ny Water Challenge raha mbola misy olana.',

        contactButton:
          'Hifandray amin’ny ekipa',

        questions: [
          {
            title:
              'Ahoana no hanombohana module iray?',

            answer:
              'Mankanesa ao amin’ny Learning, mifidiana module iray, ary tsindrio Commencer.',
          },
          {
            title:
              'Ahoana no handefasana challenge?',

            answer:
              'Mankanesa ao amin’ny Challenges, fidio ny challenge ary alefaso ny porofo takiana.',
          },
          {
            title:
              'Aiza no ahitana ny asa nalefa?',

            answer:
              'Ny asa nalefanao rehetra dia hita ao amin’ny My Activities.',
          },
        ],
      }
    }

    return {
      kicker: 'Assistance',

      title: 'Centre d’aide',

      subtitle:
        'Trouvez rapidement des réponses et découvrez comment utiliser Water Challenge.',

      contactTitle:
        'Besoin d’aide supplémentaire ?',

      contactText:
        'Contactez l’équipe Water Challenge lorsque vous ne trouvez pas la réponse à votre question.',

      contactButton:
        'Contacter l’équipe',

      questions: [
        {
          title:
            'Comment commencer un module ?',

          answer:
            'Ouvrez la section Learning, choisissez un module puis cliquez sur Commencer. Le parcours commence par la lecture.',
        },
        {
          title:
            'Comment réaliser un challenge ?',

          answer:
            'Ouvrez Challenges, sélectionnez un défi accessible, réalisez l’activité puis envoyez les preuves demandées.',
        },
        {
          title:
            'Où retrouver mes soumissions ?',

          answer:
            'Toutes vos activités envoyées et leurs statuts sont disponibles dans la section My Activities.',
        },
      ],
    }
  }, [language])

  return (
    <section className="dash-section help-page">
      <header className="help-page__header">
        <p>{content.kicker}</p>

        <h1>{content.title}</h1>

        <span>
          {content.subtitle}
        </span>
      </header>

      <div className="help-page__grid">
        <div className="help-page__questions">
          {content.questions.map(
            (question, index) => {
              const isOpen =
                openQuestion === index

              return (
                <article
                  className={
                    isOpen
                      ? 'is-open'
                      : ''
                  }
                  key={question.title}
                >
                  <button
                    type="button"
                    onClick={() =>
                      setOpenQuestion(
                        isOpen
                          ? null
                          : index
                      )
                    }
                  >
                    <span>
                      {question.title}
                    </span>

                    <strong>
                      {isOpen
                        ? '−'
                        : '+'}
                    </strong>
                  </button>

                  {isOpen && (
                    <p>
                      {question.answer}
                    </p>
                  )}
                </article>
              )
            }
          )}
        </div>

        <aside className="help-page__contact">
          <span aria-hidden="true">
            💬
          </span>

          <h2>
            {content.contactTitle}
          </h2>

          <p>
            {content.contactText}
          </p>

          <a
            href="mailto:support@waterchallenge.mg"
          >
            {content.contactButton}
          </a>
        </aside>
      </div>
    </section>
  )
}

export default HelpSection