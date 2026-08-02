import React from 'react';
import { cn } from '@ai-commerce/shared';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, error = false, type = 'text', ...props }, ref) => {
    const baseStyles = 'flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50';
    
    const errorStyles = error ? 'border-red-500 focus-visible:ring-red-500' : '';
    
    return (
      <input
        ref={ref}
        type={type}
        className={cn(baseStyles, errorStyles, className)}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';
