import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bataille Navale 3D",
  description: "Jeu de bataille navale 3D — Université des Antilles",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="min-h-screen text-slate-100 antialiased">
        <div className="mx-auto max-w-6xl px-4 py-6">{children}</div>
      </body>
    </html>
  );
}
