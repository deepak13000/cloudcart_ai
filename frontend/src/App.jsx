import { useEffect, useRef, useState } from 'react'
import './App.css'

const quickActions = [
  'Where is my order? id = CC-12345',
  'Are wireless headphones available?',
  'How much does shipping cost for 2 kg to India?',
  'I want to return an item',
]

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hi, I am your CloudCart assistant. Ask me about orders, shipping, availability, or refunds.',
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState('Ready to help you with CloudCart.')
  const chatWindowRef = useRef(null)

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const appendMessage = (role, text) => {
    setMessages((prev) => [...prev, { role, text }])
  }

  const submitMessage = async (userText) => {
    appendMessage('user', userText)
    setIsLoading(true)
    setStatus('Checking CloudCart records...')

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      const text =
        data.success
          ? data.response
          : `${data.error_code || 'ERROR'}: ${data.message || 'Request failed'}`

      appendMessage('assistant', text)
    } catch (error) {
      appendMessage('assistant', `Unable to reach backend API. ${error.message}`)
    } finally {
      setIsLoading(false)
      setStatus('Ready to help you with CloudCart.')
    }
  }

  const sendMessage = async (event) => {
    event.preventDefault()
    const userText = input.trim()
    if (!userText || isLoading) return

    setInput('')
    await submitMessage(userText)
  }

  const handleQuickAction = async (quickText) => {
    if (isLoading) return
    setInput('')
    await submitMessage(quickText)
  }

  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        text: 'Hi, I am your CloudCart assistant. Ask me about orders, shipping, availability, or refunds.',
      },
    ])
    setStatus('Ready to help you with CloudCart.')
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <span className="brand-pill">CloudCart</span>
          <h1>AI Assistant</h1>
          <p>Your CloudCart assistant is ready to help with orders, shipping, inventory, returns, and refunds.</p>
        </div>
        <div className="header-meta">
          <p className="status-label">Status</p>
          <strong className="status-value">{isLoading ? 'Thinking...' : status}</strong>
        </div>
      </header>

      <section className="action-panel">
        <div className="action-info">
          <h2>Try one of these actions</h2>
          <p>Click a quick action to get an instant CloudCart answer without typing.</p>
        </div>
        <div className="action-buttons">
          {quickActions.map((action) => (
            <button
              type="button"
              key={action}
              className="action-chip"
              onClick={() => handleQuickAction(action)}
              disabled={isLoading}
            >
              {action}
            </button>
          ))}
        </div>
      </section>

      <section ref={chatWindowRef} className="chat-window">
        {messages.map((message, index) => (
          <article key={`${message.role}-${index}`} className={`bubble ${message.role}`}>
            <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
            <p>{message.text}</p>
          </article>
        ))}
        {isLoading && <p className="loading">Assistant is typing...</p>}
      </section>

      <form className="chat-form" onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about your CloudCart order, shipping, or product availability..."
          disabled={isLoading}
        />
        <button type="submit" className="primary" disabled={isLoading}>
          Send
        </button>
        <button type="button" className="secondary" onClick={clearChat} disabled={isLoading}>
          Clear
        </button>
      </form>
    </main>
  )
}

export default App
