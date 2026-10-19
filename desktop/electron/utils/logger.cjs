const fs = require('fs')
const path = require('path')

let mainWindow = null

const LOG_LEVELS = {
  info: 'INFO',
  warn: 'WARN',
  error: 'ERROR'
}

function createLogger() {
  const { app, ipcMain } = require('electron')
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

  function formatLog(level, message, ...args) {
    const timestamp = new Date().toISOString()
    const argsStr = args.length ? ' ' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : a).join(' ') : ''
    return `[${timestamp}] [${level}] ${message}${argsStr}\n`
  }

  function writeLog(level, message, ...args) {
    try {
      const logFile = path.join(logDir, getLogFileName())
      const logLine = formatLog(LOG_LEVELS[level] || level, message, ...args)
      fs.appendFileSync(logFile, logLine, 'utf-8')

      if (mainWindow) {
        mainWindow.webContents.send('main-log', { level, message, args, timestamp: Date.now() })
      }
    } catch (e) {
      console.error('日志写入失败:', e.message)
    }
  }

  function cleanOldLogs(days = 30) {
    try {
      const files = fs.readdirSync(logDir)
      const now = Date.now()
      const expireMs = days * 24 * 60 * 60 * 1000

      files.forEach(file => {
        if (file.startsWith('app-') && file.endsWith('.log')) {
          const filePath = path.join(logDir, file)
          const stat = fs.statSync(filePath)
          if (now - stat.mtimeMs > expireMs) {
            fs.unlinkSync(filePath)
          }
        }
      })
    } catch (e) {
      console.error('清理旧日志失败:', e.message)
    }
  }

  cleanOldLogs()

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

  const logger = {
    info: (msg, ...args) => writeLog('info', msg, ...args),
    warn: (msg, ...args) => writeLog('warn', msg, ...args),
    error: (msg, ...args) => writeLog('error', msg, ...args),
    setWindow: win => {
      mainWindow = win
    }
  }

  return logger
}

module.exports = { createLogger }
