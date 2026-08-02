import { describe, expect, it } from 'vitest';
import {
  classNames,
  cn,
  formatCurrency,
  formatDate,
  formatNumber,
  generateId,
  isEmpty,
  slugify,
  truncate,
} from './index';

describe('classNames / cn', () => {
  it('joins truthy class names together', () => {
    expect(classNames('a', 'b', 'c')).toBe('a b c');
  });

  it('filters out falsy values', () => {
    expect(classNames('a', undefined, null, false, '', 'b')).toBe('a b');
  });

  it('cn is an alias of classNames', () => {
    expect(cn).toBe(classNames);
  });
});

describe('formatDate', () => {
  it('formats a Date instance into a readable string', () => {
    const result = formatDate(new Date('2024-01-15T00:00:00Z'), 'en-US');
    expect(result).toContain('2024');
    expect(result).toContain('January');
  });

  it('accepts an ISO date string', () => {
    const result = formatDate('2024-01-15T00:00:00Z', 'en-US');
    expect(result).toContain('2024');
  });
});

describe('formatCurrency', () => {
  it('formats a number as USD by default', () => {
    expect(formatCurrency(19.99)).toBe('$19.99');
  });

  it('supports other currencies', () => {
    expect(formatCurrency(10, 'EUR', 'en-US')).toContain('10');
  });
});

describe('formatNumber', () => {
  it('adds thousand separators', () => {
    expect(formatNumber(1234567)).toBe('1,234,567');
  });
});

describe('slugify', () => {
  it('converts text to a URL-friendly slug', () => {
    expect(slugify('Hello World!')).toBe('hello-world');
  });

  it('collapses whitespace and trims dashes', () => {
    expect(slugify('  Multiple   Spaces  ')).toBe('multiple-spaces');
  });
});

describe('truncate', () => {
  it('leaves short text untouched', () => {
    expect(truncate('short', 10)).toBe('short');
  });

  it('truncates long text and appends an ellipsis', () => {
    expect(truncate('this is a long string', 10)).toBe('this is...');
  });
});

describe('isEmpty', () => {
  it('detects empty values', () => {
    expect(isEmpty(null)).toBe(true);
    expect(isEmpty(undefined)).toBe(true);
    expect(isEmpty('')).toBe(true);
    expect(isEmpty('   ')).toBe(true);
    expect(isEmpty([])).toBe(true);
    expect(isEmpty({})).toBe(true);
  });

  it('detects non-empty values', () => {
    expect(isEmpty('text')).toBe(false);
    expect(isEmpty([1])).toBe(false);
    expect(isEmpty({ a: 1 })).toBe(false);
    expect(isEmpty(0)).toBe(false);
  });
});

describe('generateId', () => {
  it('generates unique ids', () => {
    const a = generateId();
    const b = generateId();
    expect(a).not.toBe(b);
  });
});
