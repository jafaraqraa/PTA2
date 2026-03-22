import React from 'react';

const SignalControls = ({ config, setConfig, onPresent, onStore, onStoreNR, responseState }) => {
  const frequencies = [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 w-full max-w-sm">
      <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
        <span className="text-gray-400">📊</span> Signal Controls
      </h2>

      <div className="mb-6">
        <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">Ear Selection</label>
        <div className="flex gap-2">
          <button
            onClick={() => setConfig({...config, side: 'RIGHT'})}
            className={`flex-1 py-2 px-4 rounded-lg border-2 font-bold transition-all ${config.side === 'RIGHT' ? 'border-red-500 text-red-500 bg-red-50' : 'border-gray-100 text-gray-400'}`}
          >
            Right (O)
          </button>
          <button
            onClick={() => setConfig({...config, side: 'LEFT'})}
            className={`flex-1 py-2 px-4 rounded-lg border-2 font-bold transition-all ${config.side === 'LEFT' ? 'border-blue-500 text-blue-500 bg-blue-50' : 'border-gray-100 text-gray-400'}`}
          >
            Left (X)
          </button>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <label className="text-xs font-semibold text-gray-500 uppercase">Frequency (Hz)</label>
          <span className="font-bold text-lg">{config.frequency} Hz</span>
        </div>
        <input
          type="range" min="0" max={frequencies.length - 1} step="1"
          value={frequencies.indexOf(config.frequency)}
          onChange={(e) => setConfig({...config, frequency: frequencies[parseInt(e.target.value)]})}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-slate-800"
        />
        <div className="flex justify-between text-[10px] text-gray-400 mt-1">
          {frequencies.map(f => <span key={f}>{f >= 1000 ? f/1000 + 'k' : f}</span>)}
        </div>
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <label className="text-xs font-semibold text-gray-500 uppercase">Intensity (dB HL)</label>
          <span className="font-bold text-lg">{config.intensity} dB</span>
        </div>
        <input
          type="range" min="-10" max="120" step="5"
          value={config.intensity}
          onChange={(e) => setConfig({...config, intensity: parseInt(e.target.value)})}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-slate-800"
        />
        <div className="flex justify-between text-[10px] text-gray-400 mt-1">
          <span>-10</span><span>20</span><span>40</span><span>60</span><span>80</span><span>100</span><span>120</span>
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <div className="flex-1">
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">Transducer</label>
          <select
            value={config.test_type}
            onChange={(e) => setConfig({...config, test_type: e.target.value})}
            className="w-full p-2 bg-gray-50 border border-gray-200 rounded-md text-sm"
          >
            <option value="AC">Air Conduction</option>
            <option value="BC">Bone Conduction</option>
            <option value="AC_MASKED">AC Masked</option>
            <option value="BC_MASKED">BC Masked</option>
          </select>
        </div>
        <div className="w-1/3">
          <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">Masking</label>
          <div className="flex border border-gray-200 rounded-md overflow-hidden text-xs">
            <button className="bg-gray-100 p-2 border-r border-gray-200 font-bold">OFF</button>
            <input
              type="number" value={config.masking_level}
              onChange={(e) => setConfig({...config, masking_level: parseInt(e.target.value)})}
              className="w-full p-2 outline-none"
            />
          </div>
        </div>
      </div>

      <button
        onClick={onPresent}
        className="w-full py-4 bg-slate-900 text-white rounded-lg font-bold text-lg mb-4 hover:bg-slate-800 transition-colors uppercase tracking-wider"
      >
        Present Tone
      </button>

      <div className="flex gap-4 mb-6">
        <button onClick={onStore} className="flex-1 py-3 bg-emerald-600 text-white rounded-lg font-bold hover:bg-emerald-700 transition-colors">Store</button>
        <button onClick={onStoreNR} className="flex-1 py-3 bg-orange-600 text-white rounded-lg font-bold hover:bg-orange-700 transition-colors">Store NR</button>
      </div>

      <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg p-3 text-center">
        <div className="flex items-center justify-center gap-2">
          <div className={`w-3 h-3 rounded-full ${responseState === 'RESPONDED' ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}></div>
          <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">
            {responseState === 'WAITING' ? 'Waiting...' : responseState === 'RESPONDED' ? 'Responded' : 'No Response'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SignalControls;
