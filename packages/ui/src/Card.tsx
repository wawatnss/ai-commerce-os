import React from 'react';
import { cn } from '@ai-commerce/shared';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    const baseStyles = 'rounded-lg border bg-white p-6 shadow-sm';
    
    const variants = {
      default: 'border-gray-200',
      elevated: 'border-gray-200 shadow-md',
      outlined: 'border-2 border-gray-300 shadow-none'
    };
    
    return (
      <div
        ref={ref}
        className={cn(baseStyles, variants[variant], className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';
