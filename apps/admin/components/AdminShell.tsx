import Link from 'next/link';

export function AdminShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-50 border-b border-gray-200 bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="/" className="text-xl font-bold tracking-tight text-gray-900">
            AI Commerce OS
          </Link>
          <nav className="flex items-center gap-4">
            <Link href="/" className="text-sm font-medium text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/quality" className="text-sm font-medium text-gray-600 hover:text-gray-900">
              Qualité IA
            </Link>
            <Link href="/system" className="text-sm font-medium text-gray-600 hover:text-gray-900">
              Système
            </Link>
            <Link href="/faq" className="text-sm font-medium text-gray-600 hover:text-gray-900">
              FAQ
            </Link>
            <Link
              href="/brands/new"
              className="inline-flex items-center justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Créer une marque
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
