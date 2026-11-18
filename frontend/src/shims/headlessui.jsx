import React from 'react';

export const Dialog = ({ as = 'div', open = true, onClose = () => {}, className = '', children, ...props }) => {
  if (!open) return null;
  const Component = as === React.Fragment ? 'div' : as;
  return (
    <Component className={className} role="dialog" aria-modal="true" {...props}>
      {children}
    </Component>
  );
};

Dialog.Panel = ({ as = 'div', className = '', children, ...props }) => {
  const Component = as === React.Fragment ? 'div' : as;
  return (
    <Component className={className} onClick={(e) => e.stopPropagation()} {...props}>
      {children}
    </Component>
  );
};

Dialog.Title = ({ as = 'h3', className = '', children, ...props }) => {
  const Component = as === React.Fragment ? 'h3' : as;
  return (
    <Component className={className} {...props}>
      {children}
    </Component>
  );
};

Dialog.Description = ({ as = 'p', className = '', children, ...props }) => {
  const Component = as === React.Fragment ? 'p' : as;
  return (
    <Component className={className} {...props}>
      {children}
    </Component>
  );
};

export const Transition = ({ show = true, as = React.Fragment, children }) => {
  if (!show) return null;
  if (as === React.Fragment) return <>{children}</>;
  const Component = as;
  return <Component>{children}</Component>;
};

Transition.Child = ({ as = React.Fragment, children }) => {
  if (as === React.Fragment) return <>{children}</>;
  const Component = as;
  return <Component>{children}</Component>;
};

Transition.Root = Transition;

export default {
  Dialog,
  Transition,
};
