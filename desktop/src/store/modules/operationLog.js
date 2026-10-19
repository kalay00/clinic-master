import { defineStore } from 'pinia'

export const useOperationLogStore = defineStore('operationLog', {
  state: () => ({
    logs: []
  }),
  
  actions: {
    addLog(log) {
      const newLog = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...log
      }
      this.logs.unshift(newLog)
      if (this.logs.length > 100) {
        this.logs = this.logs.slice(0, 100)
      }
    },
    
    clearLogs() {
      this.logs = []
    },
    
    removeLog(id) {
      this.logs = this.logs.filter(log => log.id !== id)
    }
  }
})
