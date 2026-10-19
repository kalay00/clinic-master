import { defineStore } from 'pinia'

export const useLoadingStore = defineStore('loading', {
  state: () => ({
    visible: false,
    text: '加载中...',
    count: 0
  }),
  
  actions: {
    show(text = '加载中...') {
      this.count++
      this.visible = true
      this.text = text
    },
    
    hide() {
      this.count--
      if (this.count <= 0) {
        this.count = 0
        this.visible = false
      }
    },
    
    reset() {
      this.count = 0
      this.visible = false
    }
  }
})
