import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [repository, setRepository] = useState(null);

  const [isIndexing, setIsIndexing] = useState(false);
  const [isLoadingRepository, setIsLoadingRepository] = useState(true);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isAsking, setIsAsking] = useState(false);

  const [error, setError] = useState("");

  const messagesEndRef = useRef(null);


  // --------------------------------------------------
  // LOAD ACTIVE REPOSITORY
  // --------------------------------------------------

  useEffect(() => {
    const loadRepository = async () => {
      try {
        const response = await fetch(`${API_URL}/repository`);

        if (response.status === 404) {
          setRepository(null);
          return;
        }

        if (!response.ok) {
          throw new Error("Failed to load active repository.");
        }

        const data = await response.json();

        setRepository(data);
        setRepoUrl(data.url || "");

      } catch (err) {
        console.error("Failed to load repository:", err);

      } finally {
        setIsLoadingRepository(false);
      }
    };

    loadRepository();
  }, []);


  // --------------------------------------------------
  // AUTO SCROLL CHAT
  // --------------------------------------------------

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isAsking]);


  // --------------------------------------------------
  // INGEST REPOSITORY
  // --------------------------------------------------

  const handleIngest = async () => {
    const trimmedUrl = repoUrl.trim();

    if (!trimmedUrl) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    setIsIndexing(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/ingest`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          repo_url: trimmedUrl,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to index repository."
        );
      }

      setRepository(data);

      // New repo = new conversation
      setMessages([]);
      setQuestion("");

    } catch (err) {
      setError(
        err.message || "Something went wrong while indexing."
      );

    } finally {
      setIsIndexing(false);
    }
  };


  // --------------------------------------------------
  // ASK QUESTION
  // --------------------------------------------------

  const handleAsk = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isAsking) {
      return;
    }

    if (!repository) {
      setError("Index a repository before asking questions.");
      return;
    }

    setError("");
    setQuestion("");
    setIsAsking(true);

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: trimmedQuestion,
      },
    ]);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to generate answer."
        );
      }

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);

    } catch (err) {
      setError(
        err.message || "Failed to generate answer."
      );

    } finally {
      setIsAsking(false);
    }
  };


  // --------------------------------------------------
  // CLEAN SOURCE PATH
  // --------------------------------------------------

  const cleanSourcePath = (path) => {
    if (!path) {
      return "";
    }

    const normalised = path.replaceAll("\\", "/");

    const parts = normalised.split("/");

    // repositories/repo-name/app/...
    if (parts[0] === "repositories" && parts.length > 2) {
      return parts.slice(2).join("/");
    }

    return normalised;
  };


  // --------------------------------------------------
  // KEYBOARD HANDLING
  // --------------------------------------------------

  const handleQuestionKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      handleAsk();
    }
  };


  // --------------------------------------------------
  // CLEAR CHAT
  // --------------------------------------------------

  const clearChat = () => {
    setMessages([]);
    setQuestion("");
    setError("");
  };


  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">

        <div className="header-inner">

          <div className="brand">

            <div className="brand-icon">
              &lt;/&gt;
            </div>

            <div>
              <h1>Codebase RAG</h1>
              <p>Chat with your GitHub repository</p>
            </div>

          </div>

          <div className="header-badge">
            Local AI
          </div>

        </div>

      </header>


      <main className="container">

        {/* ------------------------------------------
            REPOSITORY SECTION
        ------------------------------------------ */}

        <section className="repo-section">

          <div className="section-heading">

            <div>
              <h2>Repository</h2>

              <p>
                Enter a public GitHub repository to
                analyse its codebase.
              </p>
            </div>

          </div>


          <div className="repo-input">

            <input
              type="text"
              placeholder="https://github.com/user/repository"
              value={repoUrl}
              onChange={(event) =>
                setRepoUrl(event.target.value)
              }
              disabled={isIndexing}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !isIndexing
                ) {
                  handleIngest();
                }
              }}
            />


            <button
              className="primary-button"
              onClick={handleIngest}
              disabled={
                isIndexing ||
                isLoadingRepository
              }
            >

              {isIndexing && (
                <span className="spinner" />
              )}

              {isIndexing
                ? "Indexing"
                : repository
                  ? "Re-index"
                  : "Index Repository"}

            </button>

          </div>


          {/* INDEXING */}

          {isIndexing && (

            <div className="indexing-status">

              <span className="spinner" />

              <div>
                <strong>
                  Analysing repository
                </strong>

                <p>
                  Updating the repository, parsing code
                  and rebuilding retrieval indexes.
                </p>
              </div>

            </div>

          )}


          {/* INITIAL LOADING */}

          {isLoadingRepository && (

            <div className="loading-repository">

              <span className="spinner" />

              Checking for an active repository...

            </div>

          )}


          {/* ACTIVE REPOSITORY */}

          {repository &&
            !isIndexing &&
            !isLoadingRepository && (

              <div className="repo-status">

                <div className="repo-status-main">

                  <div className="repo-icon">
                    &lt;/&gt;
                  </div>


                  <div className="repo-details">

                    <div className="repo-name-row">

                      <strong>
                        {repository.repository}
                      </strong>

                      <span className="ready-badge">
                        <span className="status-dot" />
                        Ready
                      </span>

                    </div>


                    {repository.url && (

                      <div className="repo-url">
                        {repository.url}
                      </div>

                    )}

                  </div>

                </div>


                <div className="chunk-count">

                  <strong>
                    {repository.chunks_indexed}
                  </strong>

                  <span>
                    chunks indexed
                  </span>

                </div>

              </div>

            )}

        </section>


        {/* ERROR */}

        {error && (

          <div className="error-message">

            <span>
              {error}
            </span>

            <button
              onClick={() => setError("")}
              aria-label="Dismiss error"
            >
              ×
            </button>

          </div>

        )}


        {/* ------------------------------------------
            CHAT
        ------------------------------------------ */}

        <section className="chat-section">

          {/* CHAT HEADER */}

          <div className="chat-header">

            <div>

              <h2>
                {repository
                  ? `Chat with ${repository.repository}`
                  : "Codebase Chat"}
              </h2>

              <p>
                Answers are grounded in retrieved
                repository code.
              </p>

            </div>


            {messages.length > 0 && (

              <button
                className="clear-button"
                onClick={clearChat}
                disabled={isAsking}
              >
                Clear chat
              </button>

            )}

          </div>


          {/* CHAT BODY */}

          <div className="chat-content">

            {messages.length === 0 ? (

              <div className="empty-state">

                <div className="empty-icon">
                  &lt;/&gt;
                </div>


                <h2>

                  {isLoadingRepository
                    ? "Loading repository..."
                    : repository
                      ? "Ask about the codebase"
                      : "Connect a repository"}

                </h2>


                <p>

                  {isLoadingRepository
                    ? "Checking for an active repository."
                    : repository
                      ? "Ask about functions, classes, architecture or implementation details."
                      : "Index a GitHub repository above to start exploring its code."}

                </p>


                {repository && (

                  <div className="example-questions">

                    <span>
                      Try asking
                    </span>

                    <button
                      onClick={() =>
                        setQuestion(
                          "How does hybrid retrieval work?"
                        )
                      }
                    >
                      How does hybrid retrieval work?
                    </button>

                    <button
                      onClick={() =>
                        setQuestion(
                          "How does the query router work?"
                        )
                      }
                    >
                      How does the query router work?
                    </button>

                  </div>

                )}

              </div>

            ) : (

              <div className="messages">

                {messages.map(
                  (message, index) => (

                    <div
                      className={`message ${message.role}`}
                      key={index}
                    >

                      <div className="message-role">

                        {message.role === "user"
                          ? "You"
                          : "Codebase RAG"}

                      </div>


                      <div className="message-content">
                        {message.content}
                      </div>


                      {/* SOURCES */}

                      {message.role === "assistant" &&
                        message.sources?.length > 0 && (

                          <div className="sources">

                            <div className="sources-title">

                              <span>
                                Sources
                              </span>

                              <span className="source-count">
                                {message.sources.length}
                              </span>

                            </div>


                            <div className="source-list">

                              {message.sources.map(
                                (source) => (

                                  <div
                                    className="source-card"
                                    key={`${index}-${source.id}`}
                                  >

                                    <div className="source-top">

                                      <span className="source-id">
                                        {source.id}
                                      </span>

                                      <span className="source-name">
                                        {source.name}
                                      </span>

                                    </div>


                                    <div className="source-file">
                                      {cleanSourcePath(
                                        source.file
                                      )}
                                    </div>


                                    <div className="source-meta">

                                      <span>
                                        {source.type}
                                      </span>

                                      <span>
                                        Lines{" "}
                                        {source.start_line}
                                        –
                                        {source.end_line}
                                      </span>

                                    </div>

                                  </div>

                                )
                              )}

                            </div>

                          </div>

                        )}

                    </div>

                  )
                )}


                {/* THINKING */}

                {isAsking && (

                  <div className="message assistant">

                    <div className="message-role">
                      Codebase RAG
                    </div>


                    <div className="thinking">

                      <span className="thinking-dot" />
                      <span className="thinking-dot" />
                      <span className="thinking-dot" />

                      <span>
                        Searching repository...
                      </span>

                    </div>

                  </div>

                )}


                <div ref={messagesEndRef} />

              </div>

            )}

          </div>


          {/* ------------------------------------------
              QUESTION BOX
          ------------------------------------------ */}

          <div className="question-area">

            <div className="question-box">

              <textarea
                rows="1"
                placeholder={
                  isLoadingRepository
                    ? "Loading repository..."
                    : repository
                      ? "Ask something about this repository..."
                      : "Index a repository to start chatting..."
                }
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={handleQuestionKeyDown}
                disabled={
                  !repository ||
                  isAsking ||
                  isLoadingRepository
                }
              />


              <button
                className="send-button"
                onClick={handleAsk}
                disabled={
                  !repository ||
                  isAsking ||
                  isLoadingRepository ||
                  !question.trim()
                }
              >

                {isAsking
                  ? "Thinking..."
                  : "Send"}

              </button>

            </div>


            {repository && (

              <div className="input-hint">
                Enter to send · Shift + Enter for new line
              </div>

            )}

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;