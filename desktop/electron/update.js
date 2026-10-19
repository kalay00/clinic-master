const { autoUpdater, dialog } = require('electron')

function initUpdate(win) {
  if (process.env.NODE_ENV === 'development') {
    return
  }

  const updateUrl = process.env.VITE_UPDATE_URL
  if (!updateUrl) {
    return
  }

  autoUpdater.setFeedURL({ url: updateUrl })
  autoUpdater.autoDownload = false
  autoUpdater.autoInstallOnAppQuit = true

  autoUpdater.checkForUpdates()

  autoUpdater.on('checking-for-update', () => {
    win.webContents.send('update-checking')
  })

  autoUpdater.on('update-available', info => {
    win.webContents.send('update-available', info)
    dialog
      .showMessageBox(win, {
        type: 'info',
        title: '版本更新',
        message: `检测到新版本 v${info.version}，是否立即下载更新？`,
        detail: info.releaseNotes ? `更新说明：\n${info.releaseNotes}` : '',
        buttons: ['立即下载', '稍后提醒'],
        cancelId: 1
      })
      .then(res => {
        if (res.response === 0) {
          autoUpdater.downloadUpdate()
        }
      })
  })

  autoUpdater.on('update-not-available', () => {
    win.webContents.send('update-not-available')
  })

  autoUpdater.on('download-progress', progressObj => {
    win.webContents.send('update-progress', {
      percent: progressObj.percent,
      speed: progressObj.bytesPerSecond,
      transferred: progressObj.transferred,
      total: progressObj.total
    })
  })

  autoUpdater.on('update-downloaded', info => {
    win.webContents.send('update-downloaded', info)
    dialog
      .showMessageBox(win, {
        type: 'info',
        title: '更新完成',
        message: '新版本已下载完成，是否立即重启应用？',
        buttons: ['立即重启', '稍后重启'],
        cancelId: 1
      })
      .then(res => {
        if (res.response === 0) {
          autoUpdater.quitAndInstall()
        }
      })
  })

  autoUpdater.on('error', error => {
    win.webContents.send('update-error', error.message)
  })
}

module.exports = { initUpdate }
