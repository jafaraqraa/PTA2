import React from 'react';

const AudiogramChart = ({ storedPoints }) => {
  const frequencies = [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000];
  const intensities = [-10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120];

  const margin = { top: 40, right: 30, bottom: 40, left: 50 };
  const width = 600;
  const height = 500;
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const getX = (freq) => {
    const index = frequencies.indexOf(freq);
    return margin.left + (index / (frequencies.length - 1)) * chartWidth;
  };

  const getY = (db) => {
    return margin.top + ((db + 10) / 130) * chartHeight;
  };

  const getSymbol = (side, type, isNR) => {
    if (isNR) return 'NR';
    if (type === 'AC') return side === 'RIGHT' ? 'O' : 'X';
    if (type === 'BC') return side === 'RIGHT' ? '<' : '>';
    if (type === 'AC_MASKED') return side === 'RIGHT' ? '△' : '□';
    if (type === 'BC_MASKED') return side === 'RIGHT' ? '[' : ']';
    return '?';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex-1">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold uppercase tracking-wide">Audiogram Chart</h2>
        <div className="flex gap-4 text-xs font-bold">
           <span className="flex items-center gap-1 text-red-500"><span className="w-3 h-3 rounded-full bg-red-500"></span> Right Ear</span>
           <span className="flex items-center gap-1 text-blue-500"><span className="w-3 h-3 rounded-full bg-blue-500"></span> Left Ear</span>
        </div>
      </div>

      <svg width="100%" viewBox={`0 0 ${width} ${height}`} className="border-2 border-slate-900 rounded">
        {/* Grid Lines */}
        {frequencies.map((f, i) => (
          <React.Fragment key={f}>
            <line
              x1={getX(f)} y1={margin.top} x2={getX(f)} y2={height - margin.bottom}
              stroke="#eee" strokeWidth="1"
            />
            <text x={getX(f)} y={margin.top - 10} textAnchor="middle" fontSize="10" className="fill-gray-400 font-bold">
              {f >= 1000 ? f/1000 + 'k' : f}
            </text>
          </React.Fragment>
        ))}
        {intensities.map((db, i) => (
          <React.Fragment key={db}>
            <line
              x1={margin.left} y1={getY(db)} x2={width - margin.right} y2={getY(db)}
              stroke="#eee" strokeWidth="1"
            />
            <text x={margin.left - 10} y={getY(db) + 4} textAnchor="end" fontSize="10" className="fill-gray-400 font-bold">
              {db}
            </text>
          </React.Fragment>
        ))}

        {/* Labels */}
        <text x={width/2} y={height - 5} textAnchor="middle" fontSize="12" className="fill-slate-900 font-bold uppercase tracking-widest">Frequency (Hz)</text>
        <text x={15} y={height/2} textAnchor="middle" fontSize="12" className="fill-slate-900 font-bold uppercase tracking-widest" transform={`rotate(-90 15,${height/2})`}>Intensity (dB HL)</text>

        {/* Symbols */}
        {storedPoints.map((pt, i) => {
          const x = getX(pt.frequency);
          const y = getY(pt.threshold_db);
          const color = pt.side === 'RIGHT' ? '#ef4444' : '#3b82f6';
          const symbol = getSymbol(pt.side, pt.test_type, pt.is_nr);

          return (
            <g key={i}>
              <text x={x} y={y + 5} textAnchor="middle" fontSize="16" fontWeight="bold" fill={color}>
                {symbol}
              </text>
            </g>
          );
        })}
      </svg>
      <p className="text-[10px] text-gray-400 mt-4 text-center italic">Click on the grid to manually place or adjust symbols for advanced simulation.</p>
    </div>
  );
};

export default AudiogramChart;
