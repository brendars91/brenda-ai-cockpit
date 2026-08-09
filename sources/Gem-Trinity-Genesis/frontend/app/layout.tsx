import './globals.css'
import type { Metadata } from 'next'
import { Inter, Outfit } from 'next/font/google'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' })
const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit', display: 'swap' })

export const metadata: Metadata = {
    title: 'ORQUESTADOR DE AGENTES | GENESIS',
    description: 'Plataforma Neural de IA para Empresas',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={`${inter.variable} ${outfit.variable} font-sans bg-background text-foreground antialiased`}>
                {/* Neural Void Background */}
                <div className="fixed inset-0 pointer-events-none z-[-1] neural-bg opacity-100"></div>

                {/* Content */}
                <div className="relative z-10 min-h-screen flex flex-col">
                    {children}
                </div>
            </body>
        </html>
    )
}
