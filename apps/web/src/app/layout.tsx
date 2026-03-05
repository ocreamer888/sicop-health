import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Raleway, Montserrat } from "next/font/google";
import "./globals.css";
import { Nav } from "@/components/nav";

const plusJakarta = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const raleway = Raleway({
  variable: "--font-raleway",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "SICOP Health Intelligence",
  description: "Plataforma de inteligencia de licitaciones de salud",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${plusJakarta.variable} ${raleway.variable} ${montserrat.variable} antialiased bg-[#141310] text-[#f2f5f9]`}
      >
        <Nav />
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
