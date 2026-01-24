"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { historyApi, HistoryResponse, HistoryItem } from "@/lib/api";

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [undoing, setUndoing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await historyApi.getHistory(50, 1);
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleUndo = async () => {
    if (!history?.can_undo) return;

    setUndoing(true);
    setError(null);
    setMessage(null);

    try {
      // 先获取确认
      const confirm = await historyApi.undo(false);
      if (confirm.confirm_required) {
        // 执行撤销
        const result = await historyApi.undo(true);
        setMessage(result.message);
        await loadHistory();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "撤销失败");
    } finally {
      setUndoing(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-100 text-green-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "move":
        return "移动";
      case "rename":
        return "重命名";
      case "create_folder":
        return "创建文件夹";
      case "delete":
        return "删除";
      case "undo":
        return "撤销";
      default:
        return type;
    }
  };

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">操作历史</h1>
        <div className="flex gap-4">
          <Button
            variant="outline"
            onClick={loadHistory}
            disabled={loading}
          >
            刷新
          </Button>
          <Button
            onClick={handleUndo}
            disabled={undoing || !history?.can_undo}
          >
            {undoing ? "撤销中..." : "撤销最后操作"}
          </Button>
        </div>
      </div>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {message && (
        <Card className="mb-6 border-green-500">
          <CardContent className="pt-6">
            <p className="text-green-600">{message}</p>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">加载中...</p>
          </CardContent>
        </Card>
      ) : history ? (
        <Card>
          <CardHeader>
            <CardTitle>历史记录</CardTitle>
            <CardDescription>
              共 {history.total} 条记录
              {history.can_undo && " - 可以撤销"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {history.operations.length === 0 ? (
              <p className="text-muted-foreground">暂无历史记录</p>
            ) : (
              <div className="space-y-4">
                {history.operations.map((item: HistoryItem, index: number) => (
                  <div
                    key={index}
                    className="flex items-start gap-4 p-4 border rounded-lg hover:bg-muted/50"
                  >
                    <div className="flex-shrink-0">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                          item.status
                        )}`}
                      >
                        {item.status}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium">
                          {getTypeLabel(item.type)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {new Date(item.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm truncate" title={item.source}>
                        源: {item.source}
                      </p>
                      {item.target && (
                        <p className="text-sm truncate" title={item.target}>
                          目标: {item.target}
                        </p>
                      )}
                      {item.reason && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {item.reason}
                        </p>
                      )}
                      {item.error && (
                        <p className="text-sm text-destructive mt-1">
                          错误: {item.error}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
