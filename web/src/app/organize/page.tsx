"use client";

import { Suspense, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { scanApi, organizeApi, Operation, TaskResponse, createTaskSSE } from "@/lib/api";

type Step = "input" | "plan" | "execute" | "result";

function OrganizeContent() {
  const searchParams = useSearchParams();
  const scanIdParam = searchParams.get("scan_id");

  const [step, setStep] = useState<Step>("input");
  const [scanId, setScanId] = useState(scanIdParam || "");
  const [directory, setDirectory] = useState("");
  const [request, setRequest] = useState("");
  const [useAgent, setUseAgent] = useState(true);
  const [dryRun, setDryRun] = useState(false);
  const [loading, setLoading] = useState(false);
  const [operations, setOperations] = useState<Operation[]>([]);
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (scanIdParam) {
      scanApi.getScanResult(scanIdParam).then((result) => {
        setDirectory(result.directory);
      }).catch(() => {});
    }
  }, [scanIdParam]);

  const handleGeneratePlan = async () => {
    if (!request.trim()) {
      setError("请输入整理需求");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (useAgent) {
        const response = await organizeApi.organizeWithAgent({
          directory: directory.trim(),
          request: request.trim(),
          dry_run: dryRun,
          create_backup: true,
        });
        setTask(response);
        setStep("execute");

        const sse = createTaskSSE(response.task_id);
        sse.onMessage((msg) => {
          if (msg.type === "progress" || msg.type === "complete" || msg.type === "error") {
            organizeApi.getTaskStatus(response.task_id).then(setTask);
          }
          if (msg.type === "complete" || msg.type === "error") {
            sse.disconnect();
            setStep("result");
          }
        });
      } else {
        if (!scanId) {
          const scanResult = await scanApi.scan({
            directory: directory.trim(),
            recursive: true,
            include_metadata: true,
          });
          setScanId(scanResult.scan_id);
          
          const ops = await organizeApi.generatePlan({
            scan_id: scanResult.scan_id,
            request: request.trim(),
          });
          setOperations(ops);
        } else {
          const ops = await organizeApi.generatePlan({
            scan_id: scanId,
            request: request.trim(),
          });
          setOperations(ops);
        }
        setStep("plan");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "操作失败");
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await organizeApi.execute({
        operations,
        create_backup: true,
      });
      setTask(response);
      setStep("execute");

      const sse = createTaskSSE(response.task_id);
      sse.onMessage((msg) => {
        if (msg.type === "progress" || msg.type === "complete" || msg.type === "error") {
          organizeApi.getTaskStatus(response.task_id).then(setTask);
        }
        if (msg.type === "complete" || msg.type === "error") {
          sse.disconnect();
          setStep("result");
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "执行失败");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep("input");
    setOperations([]);
    setTask(null);
    setError(null);
  };

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">智能整理</h1>

      <div className="flex items-center gap-4 mb-8">
        {["input", "plan", "execute", "result"].map((s, i) => (
          <div key={s} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === s
                  ? "bg-primary text-primary-foreground"
                  : ["input", "plan", "execute", "result"].indexOf(step) > i
                  ? "bg-primary/20 text-primary"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {i + 1}
            </div>
            {i < 3 && <div className="w-12 h-0.5 bg-muted mx-2" />}
          </div>
        ))}
      </div>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {step === "input" && (
        <Card>
          <CardHeader>
            <CardTitle>输入整理需求</CardTitle>
            <CardDescription>描述您想要如何整理文件</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">目录路径</label>
              <Input
                placeholder="输入要整理的目录路径"
                value={directory}
                onChange={(e) => setDirectory(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">整理需求</label>
              <textarea
                className="w-full min-h-[100px] p-3 border rounded-md bg-background"
                placeholder="例如：按文件类型分类，把PDF文件放到documents文件夹，图片放到images文件夹"
                value={request}
                onChange={(e) => setRequest(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="useAgent"
                  checked={useAgent}
                  onChange={(e) => setUseAgent(e.target.checked)}
                  className="h-4 w-4"
                />
                <label htmlFor="useAgent" className="text-sm">使用 AI Agent 模式（推荐）</label>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="dryRun"
                  checked={dryRun}
                  onChange={(e) => setDryRun(e.target.checked)}
                  className="h-4 w-4"
                />
                <label htmlFor="dryRun" className="text-sm">模拟执行（不实际移动文件）</label>
              </div>
            </div>
            <Button onClick={handleGeneratePlan} disabled={loading}>
              {loading ? "处理中..." : useAgent ? "开始整理" : "生成方案"}
            </Button>
          </CardContent>
        </Card>
      )}

      {step === "plan" && (
        <Card>
          <CardHeader>
            <CardTitle>整理方案预览</CardTitle>
            <CardDescription>共 {operations.length} 个操作</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto mb-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">操作</th>
                    <th className="text-left p-2">源路径</th>
                    <th className="text-left p-2">目标路径</th>
                    <th className="text-left p-2">原因</th>
                  </tr>
                </thead>
                <tbody>
                  {operations.map((op, index) => (
                    <tr key={index} className="border-b hover:bg-muted/50">
                      <td className="p-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          op.type === "move" ? "bg-blue-100 text-blue-800" :
                          op.type === "rename" ? "bg-green-100 text-green-800" :
                          "bg-gray-100 text-gray-800"
                        }`}>
                          {op.type}
                        </span>
                      </td>
                      <td className="p-2 truncate max-w-xs" title={op.source}>
                        {op.source.split("/").pop()}
                      </td>
                      <td className="p-2 truncate max-w-xs" title={op.target}>
                        {op.target}
                      </td>
                      <td className="p-2 text-muted-foreground">{op.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex gap-4">
              <Button onClick={handleExecute} disabled={loading}>
                {loading ? "执行中..." : "确认执行"}
              </Button>
              <Button variant="outline" onClick={handleReset}>重新开始</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === "execute" && task && (
        <Card>
          <CardHeader>
            <CardTitle>执行中</CardTitle>
            <CardDescription>{task.message || "正在处理..."}</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={task.progress} className="mb-4" />
            <p className="text-sm text-muted-foreground">
              进度: {task.progress}%
              {task.current_file && ` - 当前文件: ${task.current_file}`}
            </p>
          </CardContent>
        </Card>
      )}

      {step === "result" && task && (
        <Card>
          <CardHeader>
            <CardTitle>{task.status === "completed" ? "执行完成" : "执行失败"}</CardTitle>
          </CardHeader>
          <CardContent>
            {task.result && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{task.result.total}</div>
                  <div className="text-sm text-muted-foreground">总操作数</div>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{task.result.success_count}</div>
                  <div className="text-sm text-muted-foreground">成功</div>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{task.result.failed_count}</div>
                  <div className="text-sm text-muted-foreground">失败</div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold">{(task.result.success_rate * 100).toFixed(1)}%</div>
                  <div className="text-sm text-muted-foreground">成功率</div>
                </div>
              </div>
            )}
            {task.error && <p className="text-destructive mb-4">{task.error}</p>}
            <div className="flex gap-4">
              <Button onClick={handleReset}>开始新的整理</Button>
              <Button variant="outline" onClick={() => window.location.href = "/history"}>
                查看历史记录
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function OrganizePage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto py-10">
        <div className="text-center text-muted-foreground">加载中...</div>
      </div>
    }>
      <OrganizeContent />
    </Suspense>
  );
}
