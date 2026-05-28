import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";
import chatbotIcon from "../img/assistant.png"
import userIcon from "../img/user_icon.png"


function ChatWindow() {
  const sampleQuestions = [
    {
      label: "How can I fix my noisy refrigerator?",
      query: "How can I fix my noisy refrigerator?"
    },
    {
      label: "The ice maker on my Whirlpool fridge is not working. How can I fix it?",
      query: "The ice maker on my Whirlpool fridge is not working. How can I fix it?"
    },
    {
      label: "How can I fix my leaky dishwasher?",
      query: "How can I fix my leaky dishwasher?"
    }
  ];

  const defaultMessage = [{
    role: "assistant",
    content: `Hi, I am your chat agent for ParkSelect who can assist you with information about Refrigerator and Dishwasher parts from our catalog. I can answer questions about:

    1. Popular model discovery and product compatibility
    2. Installation of right parts
    3. Descriptions and Prices of Parts 
    4. Common products issues and solutions.
  
    How can I be of service?`
  }];

  const [messages, setMessages] = useState(defaultMessage)
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (input) => {
    if (input.trim() !== "") {
      // Set user message
      setMessages(prevMessages => [...prevMessages, { role: "user", content: input }]);
      setInput("");
      setLoading(true)

      // Call API & set assistant message
      const newMessage = await getAIMessage(input, messages);
      setLoading(false)
      setMessages(prevMessages => [...prevMessages, newMessage]);
    }
  };


  return (
    <div className="messages-container">
      {messages.map((message, index) => (
        <React.Fragment key={index}>
          <div className={`${message.role}-message-container`}>
            <div className={`${message.role}-message-group`}>
              <div className="user-circle">
                {message.role === "user" ? <img src={userIcon} alt="chatbot icon"></img>
                :  <img src={chatbotIcon} alt="chatbot icon"></img>}
              </div>
              {message.content && (
                <div className={`message ${message.role}-message`}>
                  <div dangerouslySetInnerHTML={{ __html: marked(message.content).replace(/<p>|<\/p>/g, "") }}></div>
                </div>
              )}
            </div>
          </div>
          {index === 0 && (
            <div className="example-questions">
              <p><strong>Sample questions:</strong></p>
              <div className="example-question-list">
                {sampleQuestions.map((question) => (
                  <div
                    key={question.label}
                    className="example-rectangle"
                    onClick={() => {
                      handleSend(question.query);
                    }}
                  >
                    {question.label}
                  </div>
                ))}
              </div>
            </div>
          )}
        </React.Fragment>
      ))}
      <div ref={messagesEndRef} />
      {loading && (
        <div className="assistant-message-container">
          <div className="assistant-message-group">
            <div className="user-circle">
              <img src={chatbotIcon} alt="chatbot icon"></img>
            </div>
            <div
              className="message assistant-message loading-message"
              aria-label="Assistant is typing"
              data-testid="loader"
            >
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
            </div>
          </div>
        </div>
      )}
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend(input);
              e.preventDefault();
            }
          }}
          rows="3"
        />
        <button className="send-button" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
