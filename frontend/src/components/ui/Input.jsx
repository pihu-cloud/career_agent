import React, { forwardRef } from 'react';

export const Input = forwardRef(
  (
    {
      label,
      error,
      helperText,
      id,
      name,
      type = 'text',
      className = '',
      required = false,
      ...props
    },
    ref
  ) => {
    const inputId = id || name;

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">
            {label}
            {required && <span className="text-danger ml-1">*</span>}
          </label>
        )}
        <div className="relative rounded-md shadow-sm">
          <input
            ref={ref}
            id={inputId}
            name={name}
            type={type}
            className={`block w-full rounded-md border text-sm px-3 py-2 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0 ${
              error
                ? 'border-danger text-danger focus:border-danger focus:ring-danger/20'
                : 'border-gray-300 text-gray-900 focus:border-primary-600 focus:ring-primary-500/20'
            } ${className}`}
            {...props}
          />
        </div>
        {error && <p className="mt-1 text-xs text-danger">{error}</p>}
        {helperText && !error && <p className="mt-1 text-xs text-gray-500">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
