import React from 'react';

export const ResponsiveContainer = ({ width = '100%', height = '100%', children }) => {
  return (
    <div style={{ width, height, position: 'relative' }} className="recharts-responsive-container">
      {children}
    </div>
  );
};

export const PolarGrid = ({ stroke = '#e5e7eb' }) => {
  const rings = [0.25, 0.5, 0.75, 1];
  return (
    <g className="recharts-polar-grid">
      {rings.map((r, i) => (
        <circle
          key={i}
          cx="150"
          cy="120"
          r={90 * r}
          fill="none"
          stroke={stroke}
          strokeDasharray="3 3"
        />
      ))}
    </g>
  );
};

export const PolarAngleAxis = ({ dataKey = 'trait', tick = {} }) => null;
export const PolarRadiusAxis = () => null;

export const Radar = ({ name, dataKey = 'score', stroke = '#1e3a8a', fill = '#3b82f6', fillOpacity = 0.45 }) => null;

export const RadarChart = ({ cx = '50%', cy = '50%', outerRadius = 80, data = [], children }) => {
  const center = { x: 150, y: 120 };
  const radius = 80;
  const count = data.length || 5;

  const points = data.map((d, i) => {
    const angle = (Math.PI * 2 * i) / count - Math.PI / 2;
    const val = (d.score || 5) / (d.fullMark || 10);
    const x = center.x + radius * val * Math.cos(angle);
    const y = center.y + radius * val * Math.sin(angle);
    return `${x},${y}`;
  });

  const polygonPoints = points.join(' ');

  return (
    <svg viewBox="0 0 300 240" className="w-full h-full overflow-visible">
      <PolarGrid />
      {/* Outer axis spokes and labels */}
      {data.map((d, i) => {
        const angle = (Math.PI * 2 * i) / count - Math.PI / 2;
        const x1 = center.x + radius * Math.cos(angle);
        const y1 = center.y + radius * Math.sin(angle);
        const xLabel = center.x + (radius + 24) * Math.cos(angle);
        const yLabel = center.y + (radius + 16) * Math.sin(angle);
        return (
          <g key={i}>
            <line x1={center.x} y1={center.y} x2={x1} y2={y1} stroke="#e5e7eb" />
            <text
              x={xLabel}
              y={yLabel}
              textAnchor="middle"
              dominantBaseline="middle"
              className="text-[11px] fill-gray-600 font-medium select-none"
            >
              {d.trait}
            </text>
          </g>
        );
      })}
      {/* Radar polygon */}
      {points.length > 0 && (
        <polygon
          points={polygonPoints}
          fill="#3b82f6"
          fillOpacity={0.4}
          stroke="#1e3a8a"
          strokeWidth="2"
        />
      )}
    </svg>
  );
};

export const CartesianGrid = () => null;
export const XAxis = () => null;
export const YAxis = () => null;
export const Tooltip = () => null;
export const Bar = () => null;

export const BarChart = ({ data = [], children }) => {
  const maxScore = 100;
  return (
    <div className="w-full h-full flex flex-col justify-end">
      <div className="flex-1 flex items-end gap-4 px-4 pb-2 border-b border-gray-200">
        {data.map((d, i) => {
          const heightPercent = Math.min(100, Math.max(10, (d.score / maxScore) * 100));
          return (
            <div key={i} className="flex-1 flex flex-col items-center h-full justify-end group">
              <div className="text-[11px] font-bold text-primary-900 mb-1 opacity-80 group-hover:opacity-100">
                {d.score}%
              </div>
              <div
                style={{ height: `${heightPercent}%` }}
                className="w-full bg-primary-900 hover:bg-secondary-600 rounded-t-md transition-all duration-300"
              />
              <div className="text-[10px] text-gray-500 mt-2 truncate w-full text-center" title={d.name}>
                {d.name}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
};
