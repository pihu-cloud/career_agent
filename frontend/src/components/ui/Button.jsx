import React from 'react';

const variants = {
  primary: 'bg-primary-900 hover:bg-primary-800 text-white shadow-sm focus:ring-primary-500',
  secondary: 'bg-secondary-600 hover:bg-secondary-700 text-white shadow-sm focus:ring-secondary-500',
  danger: 'bg-danger hover:bg-danger-700 text-white shadow-sm focus:ring-danger-500',
  outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-primary-500',
  ghost: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus:ring-gray-400',
};

const sizes = {
  sm: 'px-2.5 py-1.5 text-xs font-medium rounded',
  md: 'px-4 py-2 text-sm font-medium rounded-md',
  lg: 'px-5 py-2.5 text-base font-medium rounded-lg',
};

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  type = 'button',
  icon: Icon,
  ...props
}) => {
  const baseClasses =
    'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  const variantClasses = variants[variant] || variants.primary;
  const sizeClasses = sizes[size] || sizes.md;

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}
      {...props}
    >
      {isLoading ? (
        <>
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          Loading...
        </>
      ) : (
        <>
          {Icon && <Icon className="-ml-0.5 mr-2 h-4 w-4" />}
          {children}
        </>
      )}
    </button>
  );
};

export default Button;
