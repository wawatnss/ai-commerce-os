import React, { useState } from 'react'
import Link from 'next/link'

interface NavItem {
  label: string
  link: string
}

interface HeaderProps {
  navigation: {
    main_menu?: NavItem[]
    mobile_menu?: { hamburger?: boolean }
  }
  storeName: string
}

export function Header({ navigation, storeName }: HeaderProps) {
  const [open, setOpen] = useState(false)
  const mainMenu = navigation.main_menu || []
  const hasHamburger = navigation.mobile_menu?.hamburger !== false

  return (
    <header className="site-header">
      <div className="container site-header__bar">
        <Link href="/" className="site-header__brand" aria-label={`${storeName} home`}>
          {storeName}
        </Link>

        <nav className="site-header__nav" aria-label="Main navigation">
          <ul>
            {mainMenu.map((item, index) => (
              <li key={index}>
                <a href={item.link}>{item.label}</a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="site-header__actions">
          {hasHamburger && (
            <button
              type="button"
              className="site-header__menu-btn"
              aria-expanded={open}
              aria-controls="mobile-nav"
              aria-label={open ? 'Close menu' : 'Open menu'}
              onClick={() => setOpen((prev) => !prev)}
            >
              {open ? (
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                  <path d="M4 4L16 16M16 4L4 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                  <path d="M2 5H18M2 10H18M2 15H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              )}
            </button>
          )}
        </div>
      </div>

      {hasHamburger && open && (
        <nav id="mobile-nav" className="site-header__mobile-nav" aria-label="Mobile navigation">
          <ul>
            {mainMenu.map((item, index) => (
              <li key={index}>
                <a href={item.link} onClick={() => setOpen(false)}>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </header>
  )
}
