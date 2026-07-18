import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Nexus d20",
  description: "Ficha inteligente e segundo cérebro para campanhas de RPG.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
