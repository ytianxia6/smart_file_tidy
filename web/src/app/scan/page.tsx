"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { scanApi, ScanResponse, FileInfo } from "@/lib/api";

export default function ScanPage() {
  const [directory, setDirectory] = useState("");
  const [recursive, setRecursive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    if (!directory.trim()) {
      setError("请输入目录路径");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await scanApi.scan({
        directory: directory.trim(),
        recursive,
        include_metadata: true,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "扫描失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">扫描目录</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>扫描配置</CardTitle>
          <CardDescription>输入要扫描的目录路径</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Input
              placeholder="输入目录路径，例如: /Users/xxx/Documents"
              value={directory}
              onChange={(e) => setDirectory(e.target.value)}
              className="flex-1"
            />
            <Button onClick={handleScan} disabled={loading}>
              {loading ? "扫描中..." : "开始扫描"}
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="recursive"
              checked={recursive}
              onChange={(e) => setRecursive(e.target.checked)}
              className="h-4 w-4"
            />
            <label htmlFor="recursive" className="text-sm">
              递归扫描子目录
            </label>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {result && (
        <>
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>扫描结果</CardTitle>
              <CardDescription>
                扫描 ID: {result.scan_id}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{result.total_files}</div>
                  <div className="text-sm text-muted-foreground">文件总数</div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{result.stats.total_size_human}</div>
                  <div className="text-sm text-muted-foreground">总大小</div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">
                    {Object.keys(result.stats.by_extension).length}
                  </div>
                  <div className="text-sm text-muted-foreground">文件类型</div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">
                    {Object.keys(result.stats.by_category).length}
                  </div>
                  <div className="text-sm text-muted-foreground">分类数</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="mb-6">
            <CardHeader>
              <CardTitle>按类型统计</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {Object.entries(result.stats.by_extension).map(([ext, count]) => (
                  <span
                    key={ext}
                    className="px-3 py-1 bg-secondary rounded-full text-sm"
                  >
                    {ext}: {count}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>文件列表</CardTitle>
              <CardDescription>共 {result.files.length} 个文件</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">文件名</th>
                      <th className="text-left p-2">类型</th>
                      <th className="text-left p-2">大小</th>
                      <th className="text-left p-2">修改时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.files.slice(0, 100).map((file: FileInfo, index: number) => (
                      <tr key={index} className="border-b hover:bg-muted/50">
                        <td className="p-2 truncate max-w-xs" title={file.path}>
                          {file.name}
                        </td>
                        <td className="p-2">{file.extension || "-"}</td>
                        <td className="p-2">{file.size_human}</td>
                        <td className="p-2">
                          {new Date(file.modified_time).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {result.files.length > 100 && (
                  <p className="text-center text-muted-foreground mt-4">
                    显示前 100 条，共 {result.files.length} 条
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="mt-6 flex gap-4">
            <Button
              onClick={() => {
                window.location.href = `/organize?scan_id=${result.scan_id}`;
              }}
            >
              开始整理
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
