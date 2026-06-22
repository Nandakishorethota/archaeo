import { useState } from "react";
import { Brain, MessageSquare, Send, Loader2, FileText, ChevronRight } from "lucide-react";
import { useStreamAnswer } from "../hooks/useStreamAnswer";

export function AskAiSection({ repoId }) {
  const [question, setQuestion] = useState("");
  const [conversation, setConversation] = useState([]);
  const { askQuestion, loading, error, data } = useStreamAnswer(repoId);

  const handleAsk = async (q) => {
    const questionText = q || question;
    if (!questionText.trim() || loading) return;

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
  };

  const suggestedQuestions = [
    "What does this application do?",
    "How do I set up and run this project?",
    "What are the main entry points?",
    "How is the codebase organized?",
  ];

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">Ask AI</h3>
        <p className="text-sm text-gray-500">Get AI-powered answers about this repository.</p>
      </div>

      {conversation.length === 0 && (
        <div className="border border-gray-100 rounded-lg p-6 space-y-5">
          <div className="flex items-center gap-2">
            <Brain className="h-4 w-4 text-gray-400" />
            <h2 className="text-sm font-medium text-gray-900">Questions You Should Ask</h2>
          </div>
          <div className="space-y-2">
            {suggestedQuestions.map((q, qIndex) => (
              <button
                key={qIndex}
                onClick={() => handleAsk(q)}
                className="w-full flex items-center gap-3 p-3 bg-gray-50 border border-gray-100 rounded-lg text-left hover:border-gray-300 transition-colors group"
                disabled={loading}
              >
                <MessageSquare className="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 flex-shrink-0" />
                <span className="text-xs text-gray-600 group-hover:text-gray-900 transition-colors flex-1">{q}</span>
                <ChevronRight className="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 transition-colors" />
              </button>
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
                {msg.files && msg.files.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                    <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">Referenced files</p>
                    {msg.files.map((file, i) => (
                      <div key={i} className="flex items-center gap-1.5 text-[11px]">
                        <FileText className="h-3 w-3 text-gray-400" />
                        <span className="text-gray-500 font-mono">{file.path}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="bg-gray-50 border border-gray-100 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="h-3.5 w-3.5 text-gray-400" />
                  <span className="text-[10px] font-medium text-gray-400">AI</span>
                </div>
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
                  <span className="text-sm text-gray-500">Thinking...</span>
                </div>
              </div>
            </div>
          )}
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
            disabled={loading}
          />
          <button
            onClick={() => handleAsk()}
            disabled={!question.trim() || loading}
            className="bg-gray-900 text-white p-2.5 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}
