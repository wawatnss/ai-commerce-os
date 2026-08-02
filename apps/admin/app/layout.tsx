import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Commerce OS - Admin',
  description: 'Administrative dashboard for the AI Commerce OS platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
