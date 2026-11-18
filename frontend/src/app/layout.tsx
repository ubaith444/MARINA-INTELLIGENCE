import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MARINA INTELLIGENCE | Chennaiyin FC & ISL 2026–27",
  description:
    "Professional football performance analytics platform for Chennaiyin FC and the Indian Super League.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
