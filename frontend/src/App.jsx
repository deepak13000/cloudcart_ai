import { useState } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hi, I am your CloudCart assistant. Ask me about orders, returns, shipping, or refunds.',
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async (event) => {
    event.preventDefault()
    const userText = input.trim()
    if (!userText || isLoading) return

    setMessages((prev) => [...prev, { role: 'user', text: userText }])
    setInput('')
    setIsLoading(true)

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

      setMessages((prev) => [...prev, { role: 'assistant', text }])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: `Unable to reach backend API. ${error.message}`,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <h1>CloudCart AI Assistant</h1>
        <p>Your CloudCart AI assistant is ready to help you with your orders, returns, shipping, and refunds.</p>
      </header>

      <section className="chat-window">
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
          placeholder="Ask about returns, orders, shipping..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </main>
  )
}

export default App
