import React from 'react';

export const Card = ({
  children,
  title,
  subtitle,
  actions,
  footer,
  className = '',
  bodyClassName = '',
}) => {
  return (
    <div className={`bg-white rounded-xl border border-gray-200/80 shadow-sm overflow-hidden ${className}`}>
      {(title || subtitle || actions) && (
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between flex-wrap gap-2">
          <div>
            {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className={`p-6 ${bodyClassName}`}>{children}</div>
      {footer && <div className="px-6 py-3 bg-gray-50/70 border-t border-gray-100">{footer}</div>}
    </div>
  );
};

export default Card;
