import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SignalControls from './components/SignalControls';
import AudiogramChart from './components/AudiogramChart';
import TestHistoryLog from './components/TestHistoryLog';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [session, setSession] = useState(null);
  const [config, setConfig] = useState({
    side: 'RIGHT',
    frequency: 1000,
    intensity: 30,
    test_type: 'AC',
    masking_level: 0
  });
  const [attempts, setAttempts] = useState([]);
  const [storedPoints, setStoredPoints] = useState([]);
  const [responseState, setResponseState] = useState('WAITING');
  const [evaluation, setEvaluation] = useState(null);

  const startSession = async () => {
    try {
      const res = await axios.post(`${API_BASE_URL}/sessions/start`);
      setSession(res.data);
      setAttempts([]);
      setStoredPoints([]);
      setEvaluation(null);
      setResponseState('WAITING');
    } catch (err) {
      console.error("Error starting session:", err);
    }
  };

  const onPresent = async () => {
    if (!session) return;
    setResponseState('PRESENTING');
    try {
      const res = await axios.post(`${API_BASE_URL}/sessions/${session.session_id}/present`, config);
      const responded = res.data.responded;
      setResponseState(responded ? 'RESPONDED' : 'NO_RESPONSE');

      setAttempts([
        { ...config, responded, timestamp: new Date() },
        ...attempts
      ]);
    } catch (err) {
      console.error("Error presenting tone:", err);
      setResponseState('WAITING');
    }
  };

  const onStore = (isNR = false) => {
    // Add point to audiogram
    const newPoint = { ...config, threshold_db: config.intensity, is_nr: isNR };
    // Remove existing point for same side/freq/type if exists
    const filtered = storedPoints.filter(p => !(p.side === config.side && p.frequency === config.frequency && p.test_type === config.test_type));
    setStoredPoints([...filtered, newPoint]);
  };

  const onEvaluate = async () => {
    if (!session) return;
    try {
      const res = await axios.post(`${API_BASE_URL}/sessions/${session.session_id}/evaluate`, storedPoints);
      setEvaluation(res.data);
    } catch (err) {
      console.error("Error evaluating session:", err);
    }
  };

  if (!session) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center font-sans">
        <div className="bg-white p-12 rounded-2xl shadow-xl border border-gray-100 text-center max-w-lg">
           <h1 className="text-4xl font-black text-slate-900 mb-4 tracking-tight">PTA Simulator</h1>
           <p className="text-gray-500 mb-8 leading-relaxed">Experience a high-fidelity audiology simulation. Start a session to generate a virtual patient and begin testing.</p>
           <button
             onClick={startSession}
             className="px-10 py-4 bg-slate-900 text-white rounded-xl font-bold text-lg hover:bg-slate-800 transition-all hover:scale-105"
           >
             Start New Session
           </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-10 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight uppercase">PTA Simulator</h1>
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Session # {session.session_id} • Patient # {session.patient_id}</p>
          </div>
          <div className="flex gap-4">
             <button onClick={onEvaluate} className="px-6 py-2 bg-slate-900 text-white rounded-lg font-bold text-sm hover:bg-slate-800 transition-colors uppercase tracking-widest">End & Evaluate</button>
             <button onClick={startSession} className="px-6 py-2 bg-white text-slate-900 border-2 border-slate-900 rounded-lg font-bold text-sm hover:bg-slate-50 transition-colors uppercase tracking-widest">New Session</button>
          </div>
        </header>

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="lg:w-1/3 flex flex-col gap-6">
            <SignalControls
              config={config} setConfig={setConfig}
              onPresent={onPresent}
              onStore={() => onStore(false)}
              onStoreNR={() => onStore(true)}
              responseState={responseState}
            />
          </div>
          <div className="lg:w-2/3">
            <AudiogramChart storedPoints={storedPoints} />
            <TestHistoryLog attempts={attempts} onClear={() => setAttempts([])} />
          </div>
        </div>

        {evaluation && (
          <div className="fixed inset-0 bg-slate-900/90 backdrop-blur-sm flex items-center justify-center p-8 z-50">
            <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-10 relative">
               <button onClick={() => setEvaluation(null)} className="absolute top-6 right-6 text-2xl font-bold text-gray-300 hover:text-slate-900 transition-colors">✕</button>
               <h2 className="text-3xl font-black text-slate-900 mb-8 tracking-tight uppercase">Evaluation Result</h2>

               <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                  <div className="bg-slate-900 p-6 rounded-xl text-center">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Final Score</p>
                    <p className="text-white text-5xl font-black tracking-tight">{evaluation.final_score}%</p>
                  </div>
                  <div className="bg-gray-50 p-6 rounded-xl text-center border border-gray-100">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Accuracy</p>
                    <p className="text-slate-900 text-5xl font-black tracking-tight">{evaluation.threshold_accuracy_score}%</p>
                  </div>
                  <div className="bg-gray-50 p-6 rounded-xl text-center border border-gray-100">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Protocol</p>
                    <p className="text-slate-900 text-5xl font-black tracking-tight">{evaluation.protocol_adherence_score}%</p>
                  </div>
               </div>

               <div className="mb-10">
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Instructor Feedback</h3>
                  <div className="space-y-3">
                    {evaluation.feedback.length > 0 ? (
                      evaluation.feedback.map((f, i) => (
                        <div key={i} className="p-4 bg-orange-50 border-l-4 border-orange-400 text-orange-800 font-medium rounded-r-lg">
                          • {f}
                        </div>
                      ))
                    ) : (
                      <div className="p-4 bg-green-50 border-l-4 border-green-400 text-green-800 font-medium rounded-r-lg">
                        Excellent! You followed the clinical protocol perfectly.
                      </div>
                    )}
                  </div>
               </div>

               <div className="mb-4">
                  <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Detailed Threshold Match</h3>
                  <div className="overflow-x-auto rounded-lg border border-gray-100">
                    <table className="w-full text-left text-sm">
                       <thead className="bg-gray-50 text-gray-500 uppercase text-[10px] tracking-widest">
                         <tr>
                            <th className="px-4 py-3">Frequency</th>
                            <th className="px-4 py-3">Ear</th>
                            <th className="px-4 py-3">Detected</th>
                            <th className="px-4 py-3">True</th>
                            <th className="px-4 py-3">Error</th>
                         </tr>
                       </thead>
                       <tbody className="divide-y divide-gray-100">
                         {evaluation.details.map((d, i) => (
                           <tr key={i}>
                             <td className="px-4 py-3 font-bold text-slate-800">{d.frequency} Hz</td>
                             <td className="px-4 py-3"><span className={`font-bold ${d.side === 'RIGHT' ? 'text-red-500' : 'text-blue-500'}`}>{d.side}</span></td>
                             <td className="px-4 py-3 font-bold">{d.detected} dB</td>
                             <td className="px-4 py-3 font-medium text-gray-400">{d.true} dB</td>
                             <td className="px-4 py-3">
                                <span className={`font-bold ${d.is_correct ? 'text-green-500' : 'text-red-500'}`}>
                                   {d.error} dB {d.is_correct ? '✓' : '✗'}
                                </span>
                             </td>
                           </tr>
                         ))}
                       </tbody>
                    </table>
                  </div>
               </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
