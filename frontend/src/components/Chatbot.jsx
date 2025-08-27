import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { MessageCircle, X } from "lucide-react";
import { PdfContext } from "../context/PdfContext";
import { API_BASE_URL } from "../api";

const Chatbot = ({ activeDocId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: "Welcome to Glean! How can I help?", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const activeCase = activeDocId; // provided by parent

  const baseUrl = API_BASE_URL;

  // Fetch chat history onopen
  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!activeCase) return;
      try {
        const response = await axios.post(`${baseUrl}/chat`, {
          doc_id: activeCase,
        });
        if (response.data.chat && response.data.chat.length > 0) {
          // Flatten chat history into a messages array (user query then bot answer)
          const historyMessages = response.data.chat.reduce((acc, item) => {
            return [
              ...acc,
              { text: item.query, sender: "user" },
              { text: item.answer, sender: "bot" },
            ];
          }, []);
          setMessages((prev) => [...prev, ...historyMessages]);
        }
      } catch (error) {
        console.error("Error fetching chat history:", error);
      }
    };

    if (isOpen) {
      fetchChatHistory();
    }
  }, [isOpen, activeCase, baseUrl]);

  const sendMessage = async () => {
    if (!input.trim() || !activeCase) return;

    const userQuery = input;
    setMessages((prev) => [...prev, { text: userQuery, sender: "user" }]);
    setInput("");

    try {
      const response = await axios.post(`${baseUrl}/ask`, {
        doc_id: activeCase,
        query: userQuery,
      });
      const answer = response.data.answer || "Sorry, I couldn't get a response.";
      setMessages((prev) => [...prev, { text: answer, sender: "bot" }]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Error communicating with the server.", sender: "bot" },
      ]);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 flex flex-col items-end">
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="p-3 bg-[#64FFDA] text-[#1F2430] rounded-full shadow-md hover:bg-[#5be8e4] transition-colors"
      >
        {isOpen ? <X size={20} /> : <MessageCircle size={20} />}
      </button>

      {/* Chatbox */}
      {isOpen && (
        <div className="w-80 h-[630px] bg-[rgba(255,255,255,0.04)] backdrop-blur-sm border border-slate-700 shadow-lg rounded-2xl flex flex-col p-4 mt-2">
          <div className="flex-1 overflow-y-auto space-y-3">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded-2xl max-w-xs break-words ${
                  msg.sender === "user"
                    ? "bg-[#64FFDA] text-[#1F2430] self-end"
                    : "bg-[#2A2F33] text-slate-300 self-start"
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>
          <div className="flex gap-2 mt-3">
            <input
              type="text"
              className="flex-1 p-2 border border-slate-700 rounded-full bg-transparent text-slate-100 placeholder-slate-400 focus:outline-none focus:border-[#64FFDA]"
              placeholder="Ask Glean..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button
              onClick={sendMessage}
              className="bg-[#64FFDA] text-[#1F2430] px-4 py-2 rounded-full hover:bg-[#5be8e4] transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
