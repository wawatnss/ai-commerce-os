import React from 'react';
import { cn } from '@ai-commerce/shared';

export interface TextProps extends React.HTMLAttributes<HTMLParagraphElement> {
  variant?: 'body' | 'lead' | 'small' | 'muted';
  as?: 'p' | 'span' | 'div';
}

export const Text = React.forwardRef<HTMLParagraphElement, TextProps>(
  ({ className, variant = 'body', as = 'p', children, ...props }, ref) => {
    const baseStyles = 'text-gray-700';
    
    const variants = {
      body: 'text-base',
      lead: 'text-lg sm:text-xl font-medium',
      small: 'text-sm',
      muted: 'text-gray-500'
    };
    
    const Tag = as as React.ElementType;
    
    return (
      <Tag
        ref={ref}
        className={cn(baseStyles, variants[variant], className)}
        {...props}
      >
        {children}
      </Tag>
    );
  }
);

Text.displayName = 'Text';
