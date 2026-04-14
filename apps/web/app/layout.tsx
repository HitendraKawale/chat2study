import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Chat2Study",
  description: "Turn long AI chats into searchable knowledge, notes, and visual study maps.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
