import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Bataille Navale 3D',
  description: 'Jeu de Bataille Navale 3D — Université des Antilles L2',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
