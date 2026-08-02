import React from 'react';
import { cn } from '@ai-commerce/shared';

export interface HeadingProps extends React.HTMLAttributes<HTMLHeadingElement> {
  level?: 1 | 2 | 3 | 4 | 5 | 6;
}

export const Heading = React.forwardRef<HTMLHeadingElement, HeadingProps>(
  ({ className, level = 2, children, ...props }, ref) => {
    const baseStyles = 'font-bold tracking-tight';
    
    const sizes = {
      1: 'text-4xl sm:text-5xl lg:text-6xl',
      2: 'text-3xl sm:text-4xl lg:text-5xl',
      3: 'text-2xl sm:text-3xl lg:text-4xl',
      4: 'text-xl sm:text-2xl lg:text-3xl',
      5: 'text-lg sm:text-xl lg:text-2xl',
      6: 'text-base sm:text-lg lg:text-xl'
    };
    
    const Tag = `h${level}` as React.ElementType;
    
    return (
      <Tag
        ref={ref}
        className={cn(baseStyles, sizes[level], className)}
        {...props}
      >
        {children}
      </Tag>
    );
  }
);

Heading.displayName = 'Heading';
