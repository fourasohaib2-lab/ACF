import type { Metadata, Viewport } from "next"
import { Inter, JetBrains_Mono } from "next/font/google"
import "./globals.css"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

const jbMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jbmono",
  display: "swap",
})

export const metadata: Metadata = {
  title: "AWCI — Aviation Weather Complexity Index",
  description:
    "Operational dashboard for the Aviation Weather Complexity Index: convective and thermodynamic complexity, flight-level heatmaps and route risk analysis.",
}

export const viewport: Viewport = {
  themeColor: "#06090f",
  colorScheme: "dark",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jbMono.variable} bg-background`}>
      <body className="font-sans antialiased bg-background text-foreground">
        {children}
      </body>
    </html>
  )
}
