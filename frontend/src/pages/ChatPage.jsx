import { useState, useEffect } from "react";
import { useParams, useLocation } from "react-router-dom";
import { Brain, MessageSquare, Lightbulb, Send, Loader2, FileText, ChevronRight } from "lucide-react";
import { useRepository } from "../hooks/useRepository";
import { useChat } from "../hooks/useChat";

const defaultSuggestedQuestions = [
  {
    category: "Getting Started",
    questions: [
      "What does this application do?",
      "How do I set up and run this project?",
      "What are the main entry points?",
    ],
  },
  {
    category: "Architecture",
    questions: [
      "How is the codebase organized?",
      "What are the main modules and how do they connect?",
      "Where is the core business logic?",
    ],
  },
  {
    category: "Deep Dive",
    questions: [
      "How does authentication work?",
      "What databases or external services does this use?",
      "Where are the API routes defined?",
    ],
  },
];

export function ChatPage() {
  const { id } = useParams();
  const location = useLocation();
  const [question, setQuestion] = useState("");
  const [conversation, setConversation] = useState([]);

  const initialQuestion = location.state?.initialQuestion;

  useEffect(() => {
    if (initialQuestion && conversation.length === 0) {
      handleAsk(initialQuestion);
    }
  }, [initialQuestion]);

  const { data: repo, isLoading: repoLoading } = useRepository(id);
  const { askQuestion, loading: chatLoading } = useChat(id);

  async function handleAsk(q) {
    const questionText = q || question;
    if (!questionText.trim() || chatLoading) return;

    const userMessage = { role: "user", content: questionText };
    setConversation((prev) => [...prev, userMessage]);
    setQuestion("");

    try {
      const response = await askQuestion(questionText);
      const aiMessage = {
        role: "assistant",
        content: response.answer || "No answer provided.",
        files: response.files || [],
      };
      setConversation((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        role: "assistant",
        content: "Sorry, I couldn't process that question. Please try again.",
        error: true,
        files: [],
      };
      setConversation((prev) => [...prev, errorMessage]);
    }
  }

  if (repoLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-6 w-48 bg-gray-100 rounded" />
        <div className="h-4 w-full bg-gray-100 rounded" />
        <div className="h-12 w-full bg-gray-100 rounded" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-2xl font-serif text-gray-900">Ask the Repository</h1>
        <p className="text-sm text-gray-500">Get AI-powered answers about {repo?.name || "this repository"}.</p>
      </div>

      {conversation.length === 0 && (
        <div className="border border-gray-100 rounded-lg p-6 space-y-5">
          <div className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-gray-400" />
            <h2 className="text-sm font-medium text-gray-900">Questions You Should Ask</h2>
          </div>
          <div className="space-y-5">
            {defaultSuggestedQuestions.map((category, catIndex) => (
              <div key={catIndex}>
                <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mb-2.5">{category.category}</p>
                <div className="space-y-2">
                  {category.questions.map((q, qIndex) => (
                    <button
                      key={qIndex}
                      onClick={() => handleAsk(q)}
                      className="w-full flex items-center gap-3 p-3 bg-gray-50 border border-gray-100 rounded-lg text-left hover:border-gray-300 transition-colors group"
                    >
                      <MessageSquare className="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 flex-shrink-0" />
                      <span className="text-xs text-gray-600 group-hover:text-gray-900 transition-colors flex-1">{q}</span>
                      <ChevronRight className="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 transition-colors" />
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {conversation.length > 0 && (
        <div className="space-y-4">
          {conversation.map((msg, msgIndex) => (
            <div key={msgIndex} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-gray-900 text-white"
                  : "bg-gray-50 border border-gray-100"
              }`}>
                {msg.role === "assistant" && (
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="h-3.5 w-3.5 text-gray-400" />
                    <span className="text-[10px] font-medium text-gray-400">AI</span>
                  </div>
                )}
                <p className={`text-sm leading-relaxed ${msg.role === "user" ? "text-white" : "text-gray-700"}`}>
                {msg.content}
              </p>
              {msg.files && msg.files.filter(f => f && (typeof f === 'string' ? f.trim() : f.path && f.path.trim())).length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200 space-y-1">
                  <p className="text-[10px] text-gray-400 font-medium">Referenced files</p>
                  {msg.files.filter(f => f && (typeof f === 'string' ? f.trim() : f.path && f.path.trim())).map((file, i) => {
                    const filePath = typeof file === 'string' ? file : file.path;
                    return (
                      <div key={i} className="flex items-center gap-1.5 text-[11px]">
                        <FileText className="h-3 w-3 text-gray-400" />
                        <span className="text-gray-500 font-mono">{filePath}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      )}

      <div className="border border-gray-200 rounded-xl p-1.5 focus-within:border-gray-400 transition-colors">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="Ask about the repository..."
            className="flex-1 bg-transparent px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none"
            disabled={chatLoading}
          />
          <button
            onClick={() => handleAsk()}
            disabled={!question.trim() || chatLoading}
            className="bg-gray-900 text-white p-2.5 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {chatLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {conversation.length > 0 && (
        <div className="border border-gray-100 rounded-lg p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-gray-400" />
            <h2 className="text-sm font-medium text-gray-900">More Questions</h2>
          </div>
          <div className="space-y-2">
            {defaultSuggestedQuestions.flatMap((c) => c.questions).slice(0, 4).map((q, qIndex) => {
              const asked = conversation.some((m) => m.role === "user" && m.content === q);
              return (
                <button
                  key={qIndex}
                  onClick={() => handleAsk(q)}
                  disabled={asked}
                  className={`w-full flex items-center gap-3 p-3 border rounded-lg text-left transition-colors ${
                    asked ? "bg-gray-50 border-gray-100 opacity-40 cursor-not-allowed" : "bg-gray-50 border-gray-100 hover:border-gray-300 group"
                  }`}
                >
                  <MessageSquare className={`h-3.5 w-3.5 flex-shrink-0 ${asked ? "text-gray-300" : "text-gray-300 group-hover:text-gray-500"}`} />
                  <span className={`text-xs ${asked ? "text-gray-400" : "text-gray-600 group-hover:text-gray-900"} transition-colors flex-1`}>{q}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
