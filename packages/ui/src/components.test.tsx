import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import {
  Badge,
  Button,
  Card,
  Container,
  Grid,
  Heading,
  Input,
  Section,
  Text,
} from './index';

describe('Button', () => {
  it('renders its children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeTruthy();
  });

  it('applies the requested variant and size classes', () => {
    render(
      <Button variant="outline" size="lg">
        Action
      </Button>
    );
    const button = screen.getByRole('button', { name: 'Action' });
    expect(button.className).toContain('border-blue-600');
    expect(button.className).toContain('h-11');
  });
});

describe('Card', () => {
  it('renders children content', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeTruthy();
  });
});

describe('Container', () => {
  it('renders children', () => {
    render(<Container>Inner content</Container>);
    expect(screen.getByText('Inner content')).toBeTruthy();
  });
});

describe('Section', () => {
  it('renders as a <section> element', () => {
    render(<Section data-testid="section">Section content</Section>);
    expect(screen.getByTestId('section').tagName).toBe('SECTION');
  });
});

describe('Heading', () => {
  it('renders the requested heading level', () => {
    render(<Heading level={3}>Title</Heading>);
    expect(screen.getByRole('heading', { level: 3, name: 'Title' })).toBeTruthy();
  });
});

describe('Text', () => {
  it('renders as a paragraph by default', () => {
    render(<Text data-testid="text">Hello</Text>);
    expect(screen.getByTestId('text').tagName).toBe('P');
  });
});

describe('Input', () => {
  it('renders an input element', () => {
    render(<Input placeholder="Type here" />);
    expect(screen.getByPlaceholderText('Type here')).toBeTruthy();
  });
});

describe('Badge', () => {
  it('renders its label', () => {
    render(<Badge variant="success">Active</Badge>);
    expect(screen.getByText('Active')).toBeTruthy();
  });
});

describe('Grid', () => {
  it('renders children', () => {
    render(
      <Grid cols={2} data-testid="grid">
        <span>Item</span>
      </Grid>
    );
    expect(screen.getByTestId('grid').className).toContain('grid-cols-1');
  });
});
