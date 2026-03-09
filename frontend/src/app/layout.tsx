import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Immigration Roadmap — AI-Powered Immigration Planning",
  description:
    "AI-powered immigration roadmap tool. Aggregate your career data, score evidence against EB-1A, NIW, and O-1 criteria, and get a personalized multi-year plan.",
  metadataBase: new URL("https://immigration-roadmap.com"),
  openGraph: {
    title: "Immigration Roadmap",
    description:
      "AI-powered planning for EB-1A, NIW, and O-1 immigration pathways.",
    siteName: "Immigration Roadmap",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Immigration Roadmap",
    description:
      "AI-powered planning for EB-1A, NIW, and O-1 immigration pathways.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider>
          <Providers>{children}</Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}
