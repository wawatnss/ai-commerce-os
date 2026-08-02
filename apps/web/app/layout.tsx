import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Commerce OS',
  description: 'AI-powered e-commerce platform for maximizing organic sales through automation',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
