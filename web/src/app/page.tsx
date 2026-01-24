import Link from "next/link";

export default function Home() {
  return (
    <div className="container mx-auto py-10">
      <div className="flex flex-col items-center justify-center space-y-8">
        <h1 className="text-4xl font-bold text-center">
          Smart File Tidy
        </h1>
        <p className="text-xl text-muted-foreground text-center max-w-2xl">
          AI 驱动的智能文件整理助手，帮助您自动分类和整理文件
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
          <Link href="/scan" className="group">
            <div className="border rounded-lg p-6 hover:border-primary transition-colors">
              <h2 className="text-xl font-semibold mb-2 group-hover:text-primary">
                扫描目录
              </h2>
              <p className="text-muted-foreground">
                扫描指定目录，获取文件列表和统计信息
              </p>
            </div>
          </Link>
          
          <Link href="/organize" className="group">
            <div className="border rounded-lg p-6 hover:border-primary transition-colors">
              <h2 className="text-xl font-semibold mb-2 group-hover:text-primary">
                智能整理
              </h2>
              <p className="text-muted-foreground">
                使用 AI 分析文件并生成整理方案
              </p>
            </div>
          </Link>
          
          <Link href="/chat" className="group">
            <div className="border rounded-lg p-6 hover:border-primary transition-colors">
              <h2 className="text-xl font-semibold mb-2 group-hover:text-primary">
                AI 对话
              </h2>
              <p className="text-muted-foreground">
                与 AI 助手对话，获取整理建议
              </p>
            </div>
          </Link>
          
          <Link href="/history" className="group">
            <div className="border rounded-lg p-6 hover:border-primary transition-colors">
              <h2 className="text-xl font-semibold mb-2 group-hover:text-primary">
                操作历史
              </h2>
              <p className="text-muted-foreground">
                查看历史操作记录，支持撤销
              </p>
            </div>
          </Link>
          
          <Link href="/config" className="group">
            <div className="border rounded-lg p-6 hover:border-primary transition-colors">
              <h2 className="text-xl font-semibold mb-2 group-hover:text-primary">
                系统配置
              </h2>
              <p className="text-muted-foreground">
                配置 AI 提供商和系统参数
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
