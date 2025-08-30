import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/AppSidebar"
import { ThemeProvider } from "@/components/ThemeProvider"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Photo Gallery App",
  description: "A beautiful photo gallery application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <SidebarProvider>
            <div className="flex min-h-screen w-full">
              <AppSidebar />
              <div className="flex-1 transition-all duration-200">
                <div className="sticky top-0 z-10 w-full bg-transparent backdrop-blur-sm ">
                  <div className="h-16 flex items-center px-4 w-full">
                    <SidebarTrigger className="mr-2" />
                    <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">RedactedBytes</h1>
                  </div>
                </div>
                <main className="p-4 md:p-6 text-gray-900 dark:text-gray-100">
                  {children}
                </main>
              </div>
            </div>
          </SidebarProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}