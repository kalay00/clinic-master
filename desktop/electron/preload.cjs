const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  sendMsg: (channel, data) => {
    const validChannels = [
      'window-min',
      'window-max',
      'window-close',
      'window-set-always-on-top',
      'file-save',
      'file-read',
      'log-write'
    ]
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data)
    }
  },

  invokeMsg: (channel, data) => {
    const validChannels = [
      'get-app-version',
      'get-app-info',
      'set-auto-launch',
      'get-auto-launch',
      'file-open-dialog',
      'file-save-dialog',
      'file-read-text',
      'file-write-text',
      'log-export',
      'checkForUpdates',
      'downloadUpdate',
      'installUpdate'
    ]
    if (validChannels.includes(channel)) {
      return ipcRenderer.invoke(channel, data)
    }
    return Promise.reject(new Error(`Invalid channel: ${channel}`))
  },

  onMsg: (channel, callback) => {
    const validChannels = [
      'update-progress',
      'update-available',
      'update-downloaded',
      'updateDownloadProgress',
      'updateAvailable',
      'updateDownloaded',
      'updateError',
      'main-log'
    ]
    if (validChannels.includes(channel)) {
      const subscription = (_event, ...args) => callback(...args)
      ipcRenderer.on(channel, subscription)
      return () => ipcRenderer.removeListener(channel, subscription)
    }
  },

  removeListener: (channel, callback) => {
    ipcRenderer.removeListener(channel, callback)
  },

  removeAllListeners: channel => {
    ipcRenderer.removeAllListeners(channel)
  }
})
