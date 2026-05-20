import type { Metadata } from "next";
import { Inter, Fira_Code } from "next/font/google";
import { Providers } from "./providers";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-fira-code",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Foresight — See Trends Before They Break Out",
  description:
    "AI-powered trend intelligence platform. Detect emerging trends from 50+ platforms using multi-agent simulation. Get ahead of the curve.",
  keywords: [
    "trend intelligence",
    "AI",
    "signal detection",
    "trend forecasting",
    "cultural analytics",
    "MiroFish",
  ],
  authors: [{ name: "Foresight" }],
  openGraph: {
    title: "Foresight — See Trends Before They Break Out",
    description:
      "AI-powered trend intelligence platform with multi-agent simulation.",
    type: "website",
    locale: "en_US",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${firaCode.variable}`}>
      <body className="min-h-screen bg-background text-on-background antialiased selection:bg-primary-container selection:text-on-primary-container">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

