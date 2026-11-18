import React, { useState, useEffect } from 'react';

const listeners = new Set();
let toasts = [];

const notify = () => {
  listeners.forEach((l) => l([...toasts]));
};

export const toast = (message, opts = {}) => {
  const id = String(Date.now() + Math.random());
  const item = { id, message, type: 'default', ...opts };
  toasts.push(item);
  notify();

  setTimeout(() => {
    toast.dismiss(id);
  }, opts.duration || 4000);

  return id;
};

toast.success = (message, opts = {}) => {
  return toast(message, { ...opts, type: 'success' });
};

toast.error = (message, opts = {}) => {
  return toast(message, { ...opts, type: 'error' });
};

toast.loading = (message, opts = {}) => {
  return toast(message, { ...opts, type: 'loading' });
};

toast.dismiss = (id) => {
  if (id) {
    toasts = toasts.filter((t) => t.id !== id);
  } else {
    toasts = [];
  }
  notify();
};

export const Toaster = ({ position = 'top-right' }) => {
  const [list, setList] = useState(toasts);

  useEffect(() => {
    listeners.add(setList);
    return () => listeners.delete(setList);
  }, []);

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col space-y-2 pointer-events-none max-w-sm w-full">
      {list.map((t) => (
        <div
          key={t.id}
          className={`pointer-events-auto flex items-center p-3 rounded-lg shadow-lg border text-sm transition-all transform ease-out duration-300 ${
            t.type === 'success'
              ? 'bg-white border-green-200 text-gray-800'
              : t.type === 'error'
              ? 'bg-white border-red-200 text-gray-800'
              : 'bg-white border-gray-200 text-gray-800'
          }`}
        >
          <span
            className={`mr-2.5 flex-shrink-0 h-2.5 w-2.5 rounded-full ${
              t.type === 'success'
                ? 'bg-green-600'
                : t.type === 'error'
                ? 'bg-red-600'
                : 'bg-blue-600'
            }`}
          />
          <span className="flex-1 font-medium">{t.message}</span>
        </div>
      ))}
    </div>
  );
};

export default toast;
