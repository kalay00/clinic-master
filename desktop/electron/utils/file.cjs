const { dialog } = require('electron')
const fs = require('fs')
const path = require('path')

let logger = null

function createFileUtils(win) {
  const { ipcMain } = require('electron')
  const userDataPath = require('electron').app.getPath('userData')
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

  ipcMain.on('file-save', (_, { fileName, data }) => {
    try {
      const fullPath = path.join(localDataPath, fileName)
      fs.writeFileSync(fullPath, JSON.stringify(data, null, 2), 'utf-8')
      win.webContents.send('file-save-result', { success: true, path: fullPath })
    } catch (error) {
      win.webContents.send('file-save-result', { success: false, message: error.message })
    }
  })

  ipcMain.on('file-read', (_, fileName) => {
    try {
      const fullPath = path.join(localDataPath, fileName)
      if (fs.existsSync(fullPath)) {
        const content = fs.readFileSync(fullPath, 'utf-8')
        win.webContents.send('file-read-result', { success: true, data: JSON.parse(content) })
      } else {
        win.webContents.send('file-read-result', { success: true, data: null })
      }
    } catch (error) {
      win.webContents.send('file-read-result', { success: false, message: error.message })
    }
  })

  return {
    localDataPath,
    readLocalFile: fullPath => {
      if (fs.existsSync(fullPath)) {
        return fs.readFileSync(fullPath, 'utf-8')
      }
      return null
    },
    writeLocalFile: (fullPath, data) => {
      try {
        const dir = path.dirname(fullPath)
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true })
        }
        fs.writeFileSync(fullPath, data, 'utf-8')
        return true
      } catch (error) {
        return false
      }
    }
  }
}

module.exports = { createFileUtils }
