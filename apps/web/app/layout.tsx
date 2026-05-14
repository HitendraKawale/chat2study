import "@xyflow/react/dist/style.css";
import "./globals.css";

import type { Metadata } from "next";

import { Nav } from "@/components/nav";
import { getMe } from "@/lib/api";

export const metadata: Metadata = {
  title: "Chat2Study",
  description:
    "Turn long AI chats into searchable knowledge, notes, and visual study maps.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const user = await getMe();

  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Nav user={user} />
        {children}
      </body>
    </html>
  );
}
