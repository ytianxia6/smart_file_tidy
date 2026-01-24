# Node.js 安装与运行指南

本指南面向从未安装过 Node.js 的新手用户，将一步步引导您完成 Web 界面的环境配置和启动。

## 目录

- [1. 安装 Node.js](#1-安装-nodejs)
- [2. 验证安装](#2-验证安装)
- [3. 安装项目依赖](#3-安装项目依赖)
- [4. 启动开发服务器](#4-启动开发服务器)
- [5. 常见问题排查](#5-常见问题排查)

---

## 1. 安装 Node.js

### 推荐版本

本项目需要 **Node.js 20.x 或更高版本**（推荐使用 LTS 长期支持版本）。

### Windows 系统

1. 访问 Node.js 官方网站：https://nodejs.org/
2. 点击下载 **LTS（长期支持版）** 安装包（.msi 文件）
3. 双击下载的安装包，按照安装向导进行安装：
   - 点击 "Next" 继续
   - 接受许可协议
   - 选择安装路径（建议保持默认）
   - 保持默认选项，点击 "Next"
   - 点击 "Install" 开始安装
   - 安装完成后点击 "Finish"
4. **重启终端**（命令提示符或 PowerShell）使环境变量生效

### macOS 系统

**方法一：官方安装包（推荐新手使用）**

1. 访问 Node.js 官方网站：https://nodejs.org/
2. 点击下载 **LTS（长期支持版）** 安装包（.pkg 文件）
3. 双击下载的安装包，按照提示完成安装
4. 重启终端使环境变量生效

**方法二：使用 Homebrew（推荐有开发经验的用户）**

```bash
# 如果未安装 Homebrew，先安装它
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Node.js LTS 版本
brew install node@20

# 添加到 PATH（根据终端提示操作）
echo 'export PATH="/opt/homebrew/opt/node@20/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Linux 系统（Ubuntu/Debian）

```bash
# 更新软件包列表
sudo apt update

# 安装 Node.js 官方仓库
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# 安装 Node.js
sudo apt install -y nodejs

# 验证安装
node --version
npm --version
```

---

## 2. 验证安装

安装完成后，打开新的终端窗口，运行以下命令验证安装是否成功：

```bash
# 查看 Node.js 版本
node --version
# 应该显示类似：v20.x.x 或 v22.x.x

# 查看 npm 版本
npm --version
# 应该显示类似：10.x.x
```

如果两个命令都能正确显示版本号，说明安装成功！

---

## 3. 安装项目依赖

### 进入 web 目录

首先，确保您已经进入项目的 `web` 目录：

```bash
# 从项目根目录进入 web 目录
cd web

# 或者使用完整路径（根据您的实际路径调整）
cd /path/to/smart_file_tidy/web
```

### 安装依赖

在 `web` 目录下运行以下命令安装所有依赖：

```bash
npm install
```

这个命令会：
- 读取 `package.json` 文件中的依赖列表
- 从 npm 仓库下载所有需要的包
- 将依赖安装到 `node_modules` 目录

安装过程可能需要几分钟，取决于您的网络速度。

**安装成功的标志：**
- 终端显示类似 "added XXX packages" 的信息
- `web` 目录下出现 `node_modules` 文件夹
- 没有红色的 ERROR 信息

---

## 4. 启动开发服务器

依赖安装完成后，运行以下命令启动开发服务器：

```bash
npm run dev
```

启动成功后，您会看到类似以下的输出：

```
   ▲ Next.js 15.1.0 (Turbopack)
   - Local:        http://localhost:3000

 ✓ Starting...
 ✓ Ready in XXXms
```

现在，打开浏览器访问 **http://localhost:3000** 即可看到 Web 界面！

### 其他常用命令

```bash
# 构建生产版本
npm run build

# 启动生产服务器（需先执行 build）
npm run start

# 代码检查
npm run lint
```

### 停止服务器

在终端中按 `Ctrl + C` 即可停止开发服务器。

---

## 5. 常见问题排查

### 问题 1：'node' 不是内部或外部命令

**症状：** 运行 `node --version` 时提示命令未找到

**解决方法：**
1. 确认 Node.js 安装完成
2. **重启终端**（关闭后重新打开）
3. Windows 用户：可能需要重启电脑
4. 如果仍有问题，检查环境变量是否配置正确

### 问题 2：npm install 速度很慢

**症状：** 依赖下载缓慢或超时

**解决方法：** 使用国内镜像源加速下载

```bash
# 临时使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# 或永久设置镜像源
npm config set registry https://registry.npmmirror.com

# 恢复官方源
npm config set registry https://registry.npmjs.org
```

### 问题 3：权限错误（EACCES）

**症状：** 安装时提示权限不足

**解决方法（macOS/Linux）：**

```bash
# 方法一：使用 sudo（不推荐长期使用）
sudo npm install

# 方法二：修改 npm 目录权限（推荐）
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 问题 4：node_modules 安装不完整

**症状：** 运行时提示模块未找到

**解决方法：**

```bash
# 删除现有的 node_modules 和锁文件
rm -rf node_modules
rm -f package-lock.json

# 重新安装
npm install
```

### 问题 5：端口 3000 被占用

**症状：** 启动时提示端口已被使用

**解决方法：**

```bash
# 方法一：使用其他端口启动
npm run dev -- -p 3001

# 方法二：查找并结束占用端口的进程
# macOS/Linux
lsof -i :3000
kill -9 <PID>

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### 问题 6：TypeScript 或依赖版本错误

**症状：** 编译错误或类型错误

**解决方法：**

```bash
# 确保 Node.js 版本正确（需要 20.x 或更高）
node --version

# 清理缓存并重新安装
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## 完整启动流程总结

```bash
# 1. 确保在项目根目录
cd smart_file_tidy

# 2. 启动后端 API 服务（在终端 1）
uvicorn src.api.main:app --reload --port 8000

# 3. 启动前端开发服务器（在终端 2）
cd web
npm install    # 首次运行需要
npm run dev

# 4. 访问 http://localhost:3000
```

---

## 需要帮助？

如果您在安装过程中遇到其他问题：

1. 查看 Node.js 官方文档：https://nodejs.org/docs/
2. 查看 npm 文档：https://docs.npmjs.com/
3. 在项目 Issues 中提问：https://github.com/yourusername/smart-file-tidy/issues
