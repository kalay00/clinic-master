const { app, BrowserWindow, ipcMain, Menu, shell, dialog } = require('electron')
const path = require('path')
const fs = require('fs')
const net = require('net')

let mainWindow = null
let logger = null

/**
 * 扫描端口范围，找到 Vite 服务器
 */
async function findVitePort(startPort = 5173, maxPort = 5200) {
  for (let port = startPort; port <= maxPort; port++) {
    const isListening = await new Promise((resolve) => {
      const client = net.createConnection({ port, host: 'localhost' }, () => {
        client.destroy()
        resolve(true)
      })
      client.on('error', () => {
        client.destroy()
        resolve(false)
      })
    })
    if (isListening) return port
  }
  return null
}

const isDev = process.env.NODE_ENV === 'development' || process.env.VITE_DEV_SERVER_URL
let detectedVitePort = null

function createLogger() {
  const userDataPath = app.getPath('userData')
  const logDir = path.join(userDataPath, 'logs')

  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true })
  }

  function getLogFileName() {
    const date = new Date()
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `app-${year}${month}${day}.log`
  }

  function writeLog(level, message, ...args) {
    try {
      const logFile = path.join(logDir, getLogFileName())
      const timestamp = new Date().toISOString()
      const argsStr = args.length ? ' ' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : a).join(' ') : ''
      const logLine = `[${timestamp}] [${level}] ${message}${argsStr}\n`
      fs.appendFileSync(logFile, logLine, 'utf-8')
    } catch (e) {
      console.error('日志写入失败:', e.message)
    }
  }

  ipcMain.on('log-write', (_, { level, message, args }) => {
    writeLog(level, message, ...(args || []))
  })

  ipcMain.handle('log-export', async () => {
    try {
      const logFile = path.join(logDir, getLogFileName())
      if (fs.existsSync(logFile)) {
        return { success: true, path: logFile, content: fs.readFileSync(logFile, 'utf-8') }
      }
      return { success: false, message: '今日日志文件不存在' }
    } catch (error) {
      return { success: false, message: error.message }
    }
  })

  return {
    info: (msg, ...args) => {
      console.log('[INFO]', msg, ...args)
      writeLog('INFO', msg, ...args)
    },
    warn: (msg, ...args) => {
      console.warn('[WARN]', msg, ...args)
      writeLog('WARN', msg, ...args)
    },
    error: (msg, ...args) => {
      console.error('[ERROR]', msg, ...args)
      writeLog('ERROR', msg, ...args)
    }
  }
}

function createFileUtils(win) {
  const userDataPath = app.getPath('userData')
  const localDataPath = path.join(userDataPath, 'localData')

  if (!fs.existsSync(localDataPath)) {
    fs.mkdirSync(localDataPath, { recursive: true })
  }

  ipcMain.handle('file-open-dialog', async (_, options = {}) => {
    const res = await dialog.showOpenDialog(win, {
      title: options.title || '选择文件',
      filters: options.filters || [{ name: '所有文件', extensions: ['*'] }],
      properties: options.properties || ['openFile']
    })
    return res.canceled ? null : res.filePaths
  })

  ipcMain.handle('file-save-dialog', async (_, options = {}) => {
    const res = await dialog.showSaveDialog(win, {
      title: options.title || '保存文件',
      defaultPath: options.defaultPath || 'untitled',
      filters: options.filters || [{ name: '所有文件', extensions: ['*'] }]
    })
    return res.canceled ? null : res.filePath
  })

  ipcMain.handle('file-read-text', async (_, filePath) => {
    try {
      const content = fs.readFileSync(filePath, 'utf-8')
      return { success: true, data: content }
    } catch (error) {
      return { success: false, message: error.message }
    }
  })

  ipcMain.handle('file-write-text', async (_, { filePath, content }) => {
    try {
      const dir = path.dirname(filePath)
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
      }
      fs.writeFileSync(filePath, content, 'utf-8')
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message }
    }
  })

  return { localDataPath }
}

function initUpdate(win) {
  try {
    const { autoUpdater } = require('electron-updater')

    if (isDev) {
      ipcMain.handle('checkForUpdates', async () => {
        return { success: true, message: '开发环境，跳过更新检查', devMode: true }
      })
      ipcMain.handle('downloadUpdate', async () => {
        return { success: false, message: '开发环境，不支持下载更新' }
      })
      ipcMain.handle('installUpdate', async () => {
        return { success: false, message: '开发环境，不支持安装更新' }
      })
      return
    }

    const updateUrl = process.env.VITE_UPDATE_URL
    if (!updateUrl) {
      ipcMain.handle('checkForUpdates', async () => {
        return { success: false, message: '未配置更新服务器地址' }
      })
      ipcMain.handle('downloadUpdate', async () => {
        return { success: false, message: '未配置更新服务器地址' }
      })
      ipcMain.handle('installUpdate', async () => {
        return { success: false, message: '未配置更新服务器地址' }
      })
      return
    }

    autoUpdater.setFeedURL({ url: updateUrl })
    autoUpdater.autoDownload = false
    autoUpdater.autoInstallOnAppQuit = true

    ipcMain.handle('checkForUpdates', async () => {
      try {
        const result = await autoUpdater.checkForUpdates()
        if (result.updateInfo) {
          return { 
            success: true, 
            hasUpdate: true,
            version: result.updateInfo.version,
            releaseNotes: result.updateInfo.releaseNotes,
            releaseDate: result.updateInfo.releaseDate,
            files: result.updateInfo.files
          }
        }
        return { success: true, hasUpdate: false, message: '当前已是最新版本' }
      } catch (error) {
        return { success: false, message: error.message }
      }
    })

    ipcMain.handle('downloadUpdate', async () => {
      try {
        autoUpdater.downloadUpdate()
        return { success: true, message: '开始下载更新' }
      } catch (error) {
        return { success: false, message: error.message }
      }
    })

    ipcMain.handle('installUpdate', async () => {
      try {
        autoUpdater.quitAndInstall()
        return { success: true, message: '正在安装更新并重启' }
      } catch (error) {
        return { success: false, message: error.message }
      }
    })

    autoUpdater.checkForUpdates()

    autoUpdater.on('update-available', info => {
      win.webContents.send('updateAvailable', info)
    })

    autoUpdater.on('download-progress', progressObj => {
      win.webContents.send('updateDownloadProgress', {
        percent: progressObj.percent,
        speed: progressObj.bytesPerSecond,
        transferred: progressObj.transferred,
        total: progressObj.total
      })
    })

    autoUpdater.on('update-downloaded', info => {
      win.webContents.send('updateDownloaded', info)
    })

    autoUpdater.on('error', error => {
      win.webContents.send('updateError', error.message)
    })
  } catch (e) {
    logger && logger.error('更新模块初始化失败:', e.message)
  }
}

function initIpcMain() {
  ipcMain.on('window-min', () => {
    if (mainWindow) mainWindow.minimize()
  })

  ipcMain.on('window-max', () => {
    if (mainWindow) {
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize()
      } else {
        mainWindow.maximize()
      }
    }
  })

  ipcMain.on('window-close', () => {
    if (mainWindow) mainWindow.close()
  })

  ipcMain.on('window-set-always-on-top', (_, flag) => {
    if (mainWindow) mainWindow.setAlwaysOnTop(flag)
  })

  ipcMain.handle('get-app-version', () => {
    return app.getVersion()
  })

  ipcMain.handle('get-app-info', () => {
    return {
      version: app.getVersion(),
      name: app.getName(),
      platform: process.platform,
      appPath: app.getAppPath(),
      userDataPath: app.getPath('userData')
    }
  })

  ipcMain.handle('set-auto-launch', (_, isOpen) => {
    app.setLoginItemSettings({
      openAtLogin: isOpen,
      openAsHidden: false
    })
    return true
  })

  ipcMain.handle('get-auto-launch', () => {
    return app.getLoginItemSettings().openAtLogin
  })
}

function createWindow() {
  mainWindow = new BrowserWindow({
    title: '华宣诊所管理系统',
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 700,
    center: true,
    resizable: true,
    frame: true,
    show: false,
    backgroundColor: '#ffffff',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
      webSecurity: false
    }
  })

  if (isDev) {
    // 优先使用启动脚本传入的 Vite 地址
    let devUrl = process.env.VITE_DEV_SERVER_URL
    // 如果没有环境变量，使用预扫描的端口或回退
    if (!devUrl) {
      if (detectedVitePort) {
        devUrl = `http://localhost:${detectedVitePort}`
      } else {
        devUrl = 'http://localhost:5173'
      }
    }
    mainWindow.loadURL(devUrl)
    mainWindow.webContents.openDevTools({ mode: 'detach' })
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  createFileUtils(mainWindow)
  initIpcMain()

  if (!isDev) {
    initUpdate(mainWindow)
  }
}

function createAppMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '退出',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit()
        }
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
        { label: '粘贴', accelerator: 'CmdOrCtrl+V', role: 'paste' },
        { label: '全选', accelerator: 'CmdOrCtrl+A', role: 'selectAll' }
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
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '关于',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '关于',
              message: '华宣诊所管理系统',
              detail: `版本: ${app.getVersion()}\n平台: ${process.platform}`
            })
          }
        }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

process.on('uncaughtException', error => {
  console.error('主进程未捕获异常:', error)
  logger && logger.error('主进程未捕获异常:', error.message)
})

process.on('unhandledRejection', reason => {
  console.error('主进程未处理的Promise拒绝:', reason)
  logger && logger.error('主进程未处理的Promise拒绝:', reason)
})

app.whenReady().then(async () => {
  if (isDev) {
    detectedVitePort = await findVitePort()
    if (detectedVitePort) {
      console.log(`[Dev] 检测到 Vite 运行在端口 ${detectedVitePort}`)
    } else {
      console.warn('[Dev] 未检测到 Vite，回退到 5173')
    }
  }
  logger = createLogger()
  logger.info('应用启动')
  createWindow()
  createAppMenu()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
