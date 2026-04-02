import type { Metadata } from 'next'
import { Inter, Noto_Sans_Devanagari } from 'next/font/google'
import './globals.css'
import Navbar from '@/components/Navbar'
import { LanguageProvider } from '@/context/LanguageContext'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const notoSansDevanagari = Noto_Sans_Devanagari({
  weight: ['400', '500', '600', '700'],
  subsets: ['devanagari'],
  variable: '--font-noto-sans-devanagari',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Samarth | Jharkhand Government Scheme Assistant',
  description: 'AI-powered assistant to help you find and apply for the right government schemes in Jharkhand.',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${notoSansDevanagari.variable}`}>
      <body className="flex flex-col min-h-screen relative text-slate-200" suppressHydrationWarning>
        <LanguageProvider>
          <Navbar />
          <main className="flex-1 w-full relative z-10 flex flex-col">
            {children}
          </main>
        </LanguageProvider>
      </body>
    </html>
  )
}
