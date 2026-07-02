import { useState } from 'react'

function CommunitySection({ t }) {
  const [posts, setPosts] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('waterChallengeCommunityPosts')) || [
        {
          id: 1,
          author: 'Water Ambassador',
          date: 'Aujourd’hui',
          text: 'J’ai sensibilisé ma famille sur trois gestes simples pour économiser l’eau : fermer le robinet, réutiliser l’eau de lavage et signaler les fuites.',
        },
        {
          id: 2,
          author: 'Community Team',
          date: 'Cette semaine',
          text: 'Nouveau défi : créer une affiche avec un message clair sur la protection des sources d’eau.',
        },
      ]
    } catch (error) {
      return []
    }
  })

  const [text, setText] = useState('')

  const savePosts = (nextPosts) => {
    setPosts(nextPosts)
    localStorage.setItem('waterChallengeCommunityPosts', JSON.stringify(nextPosts))
  }

  const handleSubmit = (event) => {
    event.preventDefault()

    if (!text.trim()) return

    const nextPost = {
      id: Date.now(),
      author: 'Moi',
      date: new Date().toLocaleDateString(),
      text: text.trim(),
    }

    savePosts([nextPost, ...posts])
    setText('')
  }

  return (
    <section className="dash-section">
      <div className="dash-section-heading">
        <div>
          <p className="dash-kicker">{t.community.kicker}</p>
          <h1>{t.community.title}</h1>
          <p>{t.community.subtitle}</p>
        </div>
      </div>

      <div className="dash-form-card">
        <form className="dash-form" onSubmit={handleSubmit}>
          <div className="dash-form-group">
            <label>{t.community.publish}</label>
            <textarea
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder={t.community.placeholder}
            />
          </div>

          <button type="submit" className="dash-primary-btn">
            {t.community.publish}
          </button>
        </form>
      </div>

      <div className="activity-list">
        {posts.map((post) => (
          <article className="community-post" key={post.id}>
            <div className="community-post-head">
              <div className="community-avatar">
                {post.author.charAt(0)}
              </div>
              <div>
                <strong>{post.author}</strong>
                <small>{post.date}</small>
              </div>
            </div>

            <p>{post.text}</p>

            <div className="challenge-meta">
              <span className="dash-pill">💬 Commenter</span>
              <span className="dash-pill gold">👏 Encourager</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

export default CommunitySection
