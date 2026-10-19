# Electron 开发指南

## 9.1 主进程概述

Electron 使用主进程和渲染进程的双进程架构：

- **主进程 (main.js)**：Node.js 环境，访问系统资源
- **渲染进程 (Vue)**：Chromium 环境，渲染 UI
- **预加载脚本 (preload.js)**：桥接主进程和渲染进程

## 9.2 窗口管理

### 9.2.1 创建窗口

```javascript
// electron/main.js
const { BrowserWindow } = require('electron')

let mainWindow = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,           // 窗口宽度
    height: 800,           // 窗口高度
    minWidth: 1024,        // 最小宽度
    minHeight: 700,        // 最小高度
    center: true,          // 启动居中
    resizable: true,       // 允许调整大小
    frame: true,           // 显示原生边框
    show: false,           // 创建后不显示，等待 ready-to-show
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  // 加载页面
  mainWindow.loadURL(url)

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })
}
```

### 9.2.2 窗口操作

```javascript
// 最小化
mainWindow.minimize()

// 最大化/还原
if (mainWindow.isMaximized()) {
  mainWindow.unmaximize()
} else {
  mainWindow.maximize()
}

// 关闭
mainWindow.close()

// 置顶
mainWindow.setAlwaysOnTop(true)

// 获取窗口状态
mainWindow.isMaximized()
mainWindow.isMinimized()
mainWindow.isAlwaysOnTop()
```

## 9.3 IPC 通信

### 9.3.1 预加载脚本暴露 API

```javascript
// electron/preload.js
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // 发送消息（异步）
  sendMsg: (channel, data) => ipcRenderer.send(channel, data),

  // 调用并等待响应（同步）
  invokeMsg: (channel, data) => ipcRenderer.invoke(channel, data),

  // 监听消息
  onMsg: (channel, callback) => ipcRenderer.on(channel, callback),

  // 移除监听
  removeListener: (channel, callback) => ipcRenderer.removeListener(channel, callback)
})
```

### 9.3.2 主进程监听

```javascript
// electron/main.js
const { ipcMain } = require('electron')

// 监听渲染进程消息
ipcMain.on('window-min', () => {
  mainWindow.minimize()
})

// 异步响应
ipcMain.handle('get-app-version', () => {
  return app.getVersion()
})

// 获取应用信息
ipcMain.handle('get-app-info', () => {
  return {
    version: app.getVersion(),
    name: app.getName(),
    platform: process.platform
  }
})
```

### 9.3.3 渲染进程调用

```javascript
// Vue 组件中
const version = await window.electronAPI.invokeMsg('get-app-version')
console.log('版本:', version)

window.electronAPI.sendMsg('window-min')

window.electronAPI.onMsg('update-progress', (percent) => {
  console.log('下载进度:', percent)
})
```

## 9.4 文件操作

### 9.4.1 文件读写

```javascript
// electron/utils/file.js
const fs = require('fs')
const path = require('path')
const { dialog } = require('electron')

// 读取文件
function readFile(filePath) {
  return fs.readFileSync(filePath, 'utf-8')
}

// 写入文件
function writeFile(filePath, content) {
  fs.writeFileSync(filePath, content, 'utf-8')
}

// 保存对话框
async function saveDialog(win, options) {
  const result = await dialog.showSaveDialog(win, {
    title: '保存文件',
    defaultPath: 'untitled.txt',
    filters: [
      { name: '文本文件', extensions: ['txt'] },
      { name: '所有文件', extensions: ['*'] }
    ]
  })
  return result.filePath
}

// 打开对话框
async function openDialog(win) {
  const result = await dialog.showOpenDialog(win, {
    title: '选择文件',
    properties: ['openFile'],
    filters: [
      { name: '图片', extensions: ['jpg', 'png', 'gif'] }
    ]
  })
  return result.filePaths
}
```

### 9.4.2 渲染进程调用文件操作

```javascript
// 保存数据到本地
async function saveData() {
  const filePath = await window.electronAPI.invokeMsg('file-save-dialog', {
    title: '保存数据',
    defaultPath: 'data.json'
  })

  if (filePath) {
    const data = JSON.stringify({ name: 'test' })
    await window.electronAPI.invokeMsg('file-write-text', {
      filePath,
      content: data
    })
  }
}
```

## 9.5 系统能力

### 9.5.1 开机自启

```javascript
const { app } = require('electron')

// 设置开机自启
app.setLoginItemSettings({
  openAtLogin: true,
  openAsHidden: false
})

// 获取当前设置
const settings = app.getLoginItemSettings()
console.log(settings.openAtLogin)
```

### 9.5.2 系统通知

```javascript
// 渲染进程
new window.Notification('标题', {
  body: '通知内容'
})
```

### 9.5.3 应用菜单

```javascript
const { Menu } = require('electron')

function createMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        { label: '退出', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { label: '撤销', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: '重做', accelerator: 'CmdOrCtrl+Y', role: 'redo' },
        { type: 'separator' },
        { label: '剪切', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: '复制', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: '粘贴', accelerator: 'CmdOrCtrl+V', role: 'paste' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { label: '刷新', accelerator: 'F5', role: 'reload' },
        { label: '开发者工具', accelerator: 'F12', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: '全屏', accelerator: 'F11', role: 'togglefullscreen' }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}
```

## 9.6 自动更新

### 9.6.1 更新模块

```javascript
// electron/update.js
const { autoUpdater, dialog } = require('electron')

function initUpdate(win) {
  autoUpdater.setFeedURL({ url: updateServerUrl })

  // 检查更新
  autoUpdater.checkForUpdates()

  // 发现新版本
  autoUpdater.on('update-available', () => {
    dialog.showMessageBox(win, {
      type: 'info',
      title: '版本更新',
      message: '检测到新版本，是否下载？',
      buttons: ['下载', '稍后']
    }).then(res => {
      if (res.response === 0) {
        autoUpdater.downloadUpdate()
      }
    })
  })

  // 下载进度
  autoUpdater.on('download-progress', (progress) => {
    win.webContents.send('update-progress', progress.percent)
  })

  // 下载完成
  autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(win, {
      type: 'info',
      title: '更新完成',
      message: '新版本已下载，是否立即重启？',
      buttons: ['立即重启', '稍后']
    }).then(res => {
      if (res.response === 0) {
        autoUpdater.quitAndInstall()
      }
    })
  })
}
```

### 9.6.2 渲染进程监听更新

```javascript
onMounted(() => {
  if (window.electronAPI) {
    window.electronAPI.onMsg('update-progress', (percent) => {
      console.log('下载进度:', percent)
    })

    window.electronAPI.onMsg('update-downloaded', () => {
      console.log('下载完成')
    })
  }
})
```

## 9.7 日志系统

### 9.7.1 日志工具

```javascript
// electron/utils/logger.js
const fs = require('fs')
const path = require('path')

function createLogger() {
  const logDir = path.join(app.getPath('userData'), 'logs')

  function writeLog(level, message) {
    const timestamp = new Date().toISOString()
    const logLine = `[${timestamp}] [${level}] ${message}\n`
    fs.appendFileSync(
      path.join(logDir, `app-${getDate()}.log`),
      logLine
    )
  }

  return {
    info: (msg) => writeLog('INFO', msg),
    warn: (msg) => writeLog('WARN', msg),
    error: (msg) => writeLog('ERROR', msg)
  }
}
```

### 9.7.2 渲染进程日志

```javascript
// Vue 中使用
import { logInfo, logError, exportLogs } from '@/utils/logger'

logInfo('用户登录成功')
logError('请求失败:', error)

async function exportLogs() {
  const res = await window.electronAPI.invokeMsg('log-export')
  if (res.success) {
    console.log('日志路径:', res.path)
  }
}
```

## 9.8 异常处理

### 9.8.1 主进程异常

```javascript
// electron/main.js
process.on('uncaughtException', (error) => {
  logger.error('未捕获异常:', error.message)
})

process.on('unhandledRejection', (reason) => {
  logger.error('未处理的Promise拒绝:', reason)
})
```

### 9.8.2 渲染进程异常

```javascript
// src/utils/errorHandler.js
window.addEventListener('error', (event) => {
  console.error('脚本错误:', event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Promise错误:', event.reason)
})
```

## 9.9 安全最佳实践

1. **禁用 nodeIntegration**：始终使用 `nodeIntegration: false`
2. **启用上下文隔离**：`contextIsolation: true`
3. **验证 IPC 通道**：在 preload 中白名单化 channel
4. **避免远程内容**：不要加载不受信任的远程内容
5. **禁用 webSecurity**：仅在开发时禁用
