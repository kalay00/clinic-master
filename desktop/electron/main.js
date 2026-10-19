const { app, BrowserWindow, ipcMain, Menu, shell } = require('electron')
const path = require('path')
const { initUpdate } = require('./update')
const { createFileUtils } = require('./utils/file')
const { createLogger } = require('./utils/logger')

let mainWindow = null
let logger = null

const isDev = process.env.NODE_ENV === 'development' || process.env.VITE_DEV_SERVER_URL

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
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
      webSecurity: true
    }
  })

  if (isDev) {
    const devUrl = process.env.VITE_DEV_SERVER_URL || 'http://localhost:5173'
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
    try {
      initUpdate(mainWindow)
    } catch (e) {
      logger && logger.error('更新模块初始化失败:', e.message)
    }
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
            const { dialog } = require('electron')
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

app.whenReady().then(() => {
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

process.on('uncaughtException', error => {
  logger && logger.error('主进程未捕获异常:', error.message)
})

process.on('unhandledRejection', reason => {
  logger && logger.error('主进程未处理的Promise拒绝:', reason)
})
