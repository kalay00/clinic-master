import { defineStore } from 'pinia'

export const useTagsViewStore = defineStore('tagsView', {
  state: () => ({
    visitedViews: [],
    cachedViews: []
  }),

  persist: {
    key: 'tags-view',
    storage: localStorage,
    paths: ['visitedViews', 'cachedViews']
  },

  actions: {
    addView(view) {
      this.addVisitedView(view)
      this.addCachedView(view)
    },

    addVisitedView(view) {
      if (!view.name) return
      // hidden 路由（如「新建病历」）不生成顶部标签页，避免切回标签导致内容被重置
      if (view.meta?.hidden) return

      const uniqueKey = view.meta?.tabUniqueKey || view.name
      const existIndex = this.visitedViews.findIndex(v => {
        const vUniqueKey = v.meta?.tabUniqueKey || v.name
        return vUniqueKey === uniqueKey
      })

      if (existIndex >= 0) {
        this.visitedViews[existIndex] = {
          path: view.path,
          name: view.name,
          title: view.meta?.title || 'no-name',
          fullPath: view.fullPath,
          meta: view.meta || {}
        }
        return
      }

      const newView = {
        path: view.path,
        name: view.name,
        title: view.meta?.title || 'no-name',
        fullPath: view.fullPath,
        meta: view.meta || {}
      }

      if (view.meta?.affix) {
        this.visitedViews.unshift(newView)
      } else {
        this.visitedViews.push(newView)
      }
    },

    addCachedView(view) {
      if (this.cachedViews.includes(view.name)) return
      if (view.meta?.hidden) return
      if (!view.meta?.noCache) {
        this.cachedViews.push(view.name)
      }
    },

    delView(view) {
      return new Promise(resolve => {
        this.delVisitedView(view)
        this.delCachedView(view)
        resolve({
          visitedViews: [...this.visitedViews],
          cachedViews: [...this.cachedViews]
        })
      })
    },

    delVisitedView(view) {
      return new Promise(resolve => {
        if (!view.name) {
          this.visitedViews = this.visitedViews.filter(v => v.path !== view.path)
        } else {
          const uniqueKey = view.meta?.tabUniqueKey || view.name
          this.visitedViews = this.visitedViews.filter(v => {
            const vUniqueKey = v.meta?.tabUniqueKey || v.name
            return vUniqueKey !== uniqueKey
          })
        }
        resolve([...this.visitedViews])
      })
    },

    delCachedView(view) {
      return new Promise(resolve => {
        const index = this.cachedViews.indexOf(view.name)
        index > -1 && this.cachedViews.splice(index, 1)
        resolve([...this.cachedViews])
      })
    },

    delOthersViews(view) {
      return new Promise(resolve => {
        let filterFn
        if (!view.name) {
          filterFn = v => v.meta?.affix || v.path === view.path
        } else {
          const uniqueKey = view.meta?.tabUniqueKey || view.name
          filterFn = v => {
            if (v.meta?.affix) return true
            const vUniqueKey = v.meta?.tabUniqueKey || v.name
            return vUniqueKey === uniqueKey
          }
        }
        this.visitedViews = this.visitedViews.filter(filterFn)
        this.cachedViews = this.cachedViews.filter(name => {
          const v = this.visitedViews.find(item => item.name === name)
          return v ? !v.meta?.noCache : false
        })
        resolve({
          visitedViews: [...this.visitedViews],
          cachedViews: [...this.cachedViews]
        })
      })
    },

    delAllViews() {
      return new Promise(resolve => {
        this.visitedViews = this.visitedViews.filter(v => v.meta?.affix)
        this.cachedViews = []
        resolve({
          visitedViews: [...this.visitedViews],
          cachedViews: [...this.cachedViews]
        })
      })
    },

    updateVisitedView(view) {
      for (let v of this.visitedViews) {
        if (v.path === view.path) {
          v.title = view.meta?.title || v.title
          v.fullPath = view.fullPath
          v.meta = view.meta || v.meta
          break
        }
      }
    },

    ensureHomeView() {
      const homeExist = this.visitedViews.some(v => v.path === '/' || v.path === '/dashboard')
      if (!homeExist) {
        this.addVisitedView({
          path: '/',
          name: 'Dashboard',
          title: '首页',
          fullPath: '/',
          meta: { title: '首页', icon: 'HomeFilled', affix: true }
        })
      } else {
        const homeIndex = this.visitedViews.findIndex(v => v.path === '/' || v.path === '/dashboard')
        if (homeIndex !== 0) {
          const homeView = this.visitedViews.splice(homeIndex, 1)[0]
          this.visitedViews.unshift(homeView)
        }
      }
    },

    resetState() {
      this.visitedViews = []
      this.cachedViews = []
    }
  }
})
