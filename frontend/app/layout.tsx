import type React from "react";
import "./styles.css";

export const metadata = {
  title: "XEIP",
  description: "Xerox Enterprise Intelligence Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
