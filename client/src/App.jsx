import { useState } from 'react';
import axios from 'axios';
import { Activity, AlertTriangle, BookOpen, Stethoscope, Send, ClipboardList } from 'lucide-react';

function App() {
  const [symptoms, setSymptoms] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleTriage = async () => {
    if (!symptoms.trim()) return;
    
    setLoading(true);
    setError("");
    setResult(null);

    try {
      // 1. Connect to your Local Python Server
      const response = await axios.post('http://127.0.0.1:8000/analyze', {
        symptoms: symptoms
      });
      
      console.log("AI Response:", response.data); // For debugging
      setResult(response.data);
      
    } catch (err) {
      setError("⚠️ Error: Is the Python Server running? (Check terminal)");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 pb-12">
      
      {/* 🏥 HEADER */}
      <nav className="bg-blue-700 text-white p-4 shadow-lg sticky top-0 z-50">
        <div className="max-w-md mx-auto flex items-center gap-2">
          <Stethoscope className="h-6 w-6" />
          <h1 className="text-xl font-bold tracking-wide">Triage-Mate <span className="text-xs opacity-75 font-normal">Offline Edition</span></h1>
        </div>
      </nav>

      <main className="max-w-md mx-auto p-4 space-y-6 mt-4">
        
        {/* 📝 INPUT CARD */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
          <label className="flex items-center gap-2 text-sm font-bold text-slate-700 mb-3">
            <ClipboardList className="h-4 w-4 text-blue-600"/> Patient Symptoms
          </label>
          
          <textarea
            className="w-full h-32 p-4 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none text-slate-700 bg-slate-50"
            placeholder="e.g. 5yo boy, fever 102F, rash on arms, stiff neck..."
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
          />
          
          <button
            onClick={handleTriage}
            disabled={loading}
            className={`w-full mt-4 py-3.5 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 ${
              loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {loading ? <Activity className="animate-spin h-5 w-5" /> : <Send className="h-5 w-5" />}
            {loading ? "Analyzing Guidelines..." : "Run Triage Analysis"}
          </button>
          
          {error && <p className="text-red-500 text-sm mt-3 text-center bg-red-50 p-2 rounded-lg">{error}</p>}
        </div>

        {/* 📊 RESULTS CARD */}
        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-4">
            
            {/* Risk Banner */}
            <div className={`p-5 rounded-xl border-l-4 flex items-start gap-4 shadow-sm ${
              result.risk_level?.includes("High") 
                ? 'bg-red-50 border-red-500 text-red-900' 
                : result.risk_level?.includes("Medium")
                  ? 'bg-amber-50 border-amber-500 text-amber-900'
                  : 'bg-green-50 border-green-500 text-green-900'
            }`}>
              <AlertTriangle className={`h-6 w-6 shrink-0 ${
                 result.risk_level?.includes("High") ? 'text-red-600' : 'text-amber-600'
              }`} />
              <div>
                <p className="text-xs font-bold uppercase tracking-wider opacity-70">Triage Assessment</p>
                <h2 className="text-xl font-bold">{result.risk_level || "Unknown Risk"} Risk</h2>
                <p className="text-sm font-medium mt-1">{result.suspected_condition}</p>
              </div>
            </div>

            {/* AI Reasoning */}
            <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
              <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
                <BookOpen className="h-4 w-4 text-blue-500" /> Clinical Reasoning
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                {result.reasoning}
              </p>
            </div>

            {/* Follow Up Questions */}
            {result.follow_up_questions && (
              <div className="bg-blue-50 p-5 rounded-2xl border border-blue-100">
                <h3 className="font-bold text-blue-900 mb-3 text-sm">Suggested Questions</h3>
                <ul className="space-y-2">
                  {result.follow_up_questions.map((q, i) => (
                    <li key={i} className="flex gap-3 text-sm text-blue-800">
                      <span className="font-bold bg-blue-200 text-blue-800 rounded-full w-5 h-5 flex items-center justify-center text-xs shrink-0">
                        {i+1}
                      </span>
                      {q}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;