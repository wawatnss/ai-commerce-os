import React from 'react';
import { cn } from '@ai-commerce/shared';

export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  variant?: 'default' | 'muted' | 'accent';
}

export const Section = React.forwardRef<HTMLElement, SectionProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    const baseStyles = 'py-16 px-4';
    
    const variants = {
      default: 'bg-white',
      muted: 'bg-gray-50',
      accent: 'bg-blue-50'
    };
    
    return (
      <section
        ref={ref}
        className={cn(baseStyles, variants[variant], className)}
        {...props}
      >
        {children}
      </section>
    );
  }
);

Section.displayName = 'Section';
