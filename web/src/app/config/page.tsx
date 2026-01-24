"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { configApi, ConfigResponse, AIProviderConfig } from "@/lib/api";

export default function ConfigPage() {
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({
    api_key: "",
    model: "",
    base_url: "",
  });

  const loadConfig = async () => {
    setLoading(true);
    try {
      const data = await configApi.getConfig();
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载配置失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const handleSetDefault = async (provider: string) => {
    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      await configApi.setDefaultProvider(provider);
      setMessage(`已将 ${provider} 设为默认提供商`);
      await loadConfig();
    } catch (err) {
      setError(err instanceof Error ? err.message : "设置失败");
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async (provider: string) => {
    setError(null);
    setMessage(null);

    try {
      const result = await configApi.validateConfig(provider);
      if (result.valid) {
        setMessage(`${provider} 配置有效`);
      } else {
        setError(`配置问题: ${result.issues?.join(", ")}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "验证失败");
    }
  };

  const handleEdit = (provider: AIProviderConfig) => {
    setEditingProvider(provider.provider);
    setEditForm({
      api_key: "",
      model: provider.model,
      base_url: "",
    });
  };

  const handleSave = async () => {
    if (!editingProvider) return;

    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      await configApi.updateAIConfig({
        provider: editingProvider,
        model: editForm.model || undefined,
        api_key: editForm.api_key || undefined,
        base_url: editForm.base_url || undefined,
      });
      setMessage("配置已更新");
      setEditingProvider(null);
      await loadConfig();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const getProviderName = (provider: string) => {
    switch (provider) {
      case "claude":
        return "Claude (Anthropic)";
      case "openai":
        return "OpenAI";
      case "local":
        return "本地模型 (Ollama)";
      case "custom":
        return "自定义 API";
      default:
        return provider;
    }
  };

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">系统配置</h1>

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
      ) : config ? (
        <>
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>AI 提供商配置</CardTitle>
              <CardDescription>
                当前默认: {getProviderName(config.default_provider)}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {config.providers.map((provider) => (
                  <div
                    key={provider.provider}
                    className="p-4 border rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">
                          {getProviderName(provider.provider)}
                        </span>
                        {provider.is_default && (
                          <span className="px-2 py-0.5 bg-primary text-primary-foreground rounded text-xs">
                            默认
                          </span>
                        )}
                        <span
                          className={`px-2 py-0.5 rounded text-xs ${
                            provider.is_configured
                              ? "bg-green-100 text-green-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {provider.is_configured ? "已配置" : "未配置"}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleValidate(provider.provider)}
                        >
                          测试
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(provider)}
                        >
                          编辑
                        </Button>
                        {!provider.is_default && (
                          <Button
                            size="sm"
                            onClick={() => handleSetDefault(provider.provider)}
                            disabled={saving}
                          >
                            设为默认
                          </Button>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      模型: {provider.model || "未设置"}
                    </p>

                    {editingProvider === provider.provider && (
                      <div className="mt-4 p-4 bg-muted rounded-lg space-y-4">
                        <div>
                          <label className="text-sm font-medium mb-1 block">
                            API Key
                          </label>
                          <Input
                            type="password"
                            placeholder="输入 API Key（将通过环境变量存储）"
                            value={editForm.api_key}
                            onChange={(e) =>
                              setEditForm({ ...editForm, api_key: e.target.value })
                            }
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            建议通过环境变量配置，此处设置仅作提示
                          </p>
                        </div>
                        <div>
                          <label className="text-sm font-medium mb-1 block">
                            模型名称
                          </label>
                          <Input
                            placeholder="例如: claude-3-5-sonnet-20241022"
                            value={editForm.model}
                            onChange={(e) =>
                              setEditForm({ ...editForm, model: e.target.value })
                            }
                          />
                        </div>
                        {(provider.provider === "local" ||
                          provider.provider === "custom") && (
                          <div>
                            <label className="text-sm font-medium mb-1 block">
                              API 地址
                            </label>
                            <Input
                              placeholder="例如: http://localhost:11434"
                              value={editForm.base_url}
                              onChange={(e) =>
                                setEditForm({
                                  ...editForm,
                                  base_url: e.target.value,
                                })
                              }
                            />
                          </div>
                        )}
                        <div className="flex gap-2">
                          <Button onClick={handleSave} disabled={saving}>
                            {saving ? "保存中..." : "保存"}
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => setEditingProvider(null)}
                          >
                            取消
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>文件操作配置</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-lg font-medium">
                    {config.file_operations.batch_size as number || 50}
                  </div>
                  <div className="text-sm text-muted-foreground">批量大小</div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-lg font-medium">
                    {config.file_operations.max_file_size_mb as number || 100} MB
                  </div>
                  <div className="text-sm text-muted-foreground">
                    最大文件大小
                  </div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-lg font-medium">
                    {config.file_operations.scan_max_depth as number || 5}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    扫描深度
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}
