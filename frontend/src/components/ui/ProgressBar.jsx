import React from 'react';

export const ProgressBar = ({
  progress = 0,
  label,
  showPercentage = true,
  color = 'primary',
  size = 'md',
  className = '',
}) => {
  const clampedProgress = Math.min(100, Math.max(0, Math.round(progress)));

  const colorVariants = {
    primary: 'bg-primary-900',
    secondary: 'bg-secondary-600',
    success: 'bg-success',
    warning: 'bg-warning',
    gradient: 'bg-gradient-to-r from-primary-900 via-secondary-600 to-primary-600',
  };

  const sizeVariants = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  };

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-1.5 text-xs font-semibold text-gray-700">
          <span>{label}</span>
          {showPercentage && <span>{clampedProgress}%</span>}
        </div>
      )}
      <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeVariants[size] || sizeVariants.md}`}>
        <div
          className={`${sizeVariants[size] || sizeVariants.md} rounded-full transition-all duration-500 ease-out ${
            colorVariants[color] || colorVariants.primary
          }`}
          style={{ width: `${clampedProgress}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
