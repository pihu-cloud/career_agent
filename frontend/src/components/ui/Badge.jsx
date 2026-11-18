import React from 'react';

const badgeVariants = {
  default: 'bg-gray-100 text-gray-800 border-gray-200',
  primary: 'bg-blue-50 text-primary-900 border-primary-200',
  secondary: 'bg-purple-50 text-secondary-700 border-purple-200',
  success: 'bg-green-50 text-green-700 border-green-200',
  warning: 'bg-amber-50 text-amber-700 border-amber-200',
  danger: 'bg-red-50 text-red-700 border-red-200',
};

const badgeSizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
};

export const Badge = ({
  children,
  variant = 'default',
  size = 'sm',
  className = '',
}) => {
  const variantClass = badgeVariants[variant] || badgeVariants.default;
  const sizeClass = badgeSizes[size] || badgeSizes.sm;

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${variantClass} ${sizeClass} ${className}`}
    >
      {children}
    </span>
  );
};

export default Badge;
