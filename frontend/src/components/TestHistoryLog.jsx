import React from 'react';

const TestHistoryLog = ({ attempts, onClear }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 mt-6 overflow-hidden">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold uppercase tracking-wide">Test History Log</h2>
        <button onClick={onClear} className="text-xs font-bold text-gray-400 hover:text-slate-900 transition-colors uppercase tracking-widest border-b border-gray-200">Clear All</button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-gray-500 uppercase text-[10px] tracking-widest">
            <tr>
              <th className="px-4 py-3">Ear</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Freq (Hz)</th>
              <th className="px-4 py-3">Level (dB)</th>
              <th className="px-4 py-3">Result</th>
              <th className="px-4 py-3">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {attempts.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-4 py-12 text-center text-gray-400 font-medium italic">No attempts logged yet.</td>
              </tr>
            ) : (
              attempts.map((att, i) => (
                <tr key={i} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <span className={`font-bold ${att.side === 'RIGHT' ? 'text-red-500' : 'text-blue-500'}`}>
                      {att.side}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 font-medium">{att.test_type}</td>
                  <td className="px-4 py-3 font-bold text-slate-800">{att.frequency} Hz</td>
                  <td className="px-4 py-3 font-bold text-slate-800">{att.intensity} dB</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${att.responded ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {att.responded ? 'Responded' : 'No Response'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">
                    {new Date(att.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TestHistoryLog;
