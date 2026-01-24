import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart File Tidy",
  description: "AI 驱动的智能文件整理助手",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-background font-sans antialiased">
        <div className="relative flex min-h-screen flex-col">
          <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 items-center">
              <div className="mr-4 flex">
                <a className="mr-6 flex items-center space-x-2" href="/">
                  <span className="font-bold text-xl">Smart File Tidy</span>
                </a>
                <nav className="flex items-center space-x-6 text-sm font-medium">
                  <a href="/scan" className="transition-colors hover:text-foreground/80 text-foreground/60">
                    扫描
                  </a>
                  <a href="/organize" className="transition-colors hover:text-foreground/80 text-foreground/60">
                    整理
                  </a>
                  <a href="/history" className="transition-colors hover:text-foreground/80 text-foreground/60">
                    历史
                  </a>
                  <a href="/chat" className="transition-colors hover:text-foreground/80 text-foreground/60">
                    AI 对话
                  </a>
                  <a href="/config" className="transition-colors hover:text-foreground/80 text-foreground/60">
                    配置
                  </a>
                </nav>
              </div>
            </div>
          </header>
          <main className="flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
