import { defineStore } from 'pinia'
import { asyncRoutes, constantRoutes } from '@/router/routes'
import { canAccessMenu } from '@/utils/permission'

// 按菜单权限映射（MENU_PERMISSIONS）判断路由是否可见
function hasPermission(route) {
  const name = route.name || route.path
  return canAccessMenu(name)
}

function filterAsyncRoutes(routes) {
  const res = []
  routes.forEach(route => {
    const tmp = { ...route }
    if (hasPermission(tmp)) {
      if (tmp.children) {
        tmp.children = filterAsyncRoutes(tmp.children)
      }
      res.push(tmp)
    }
  })
  return res
}

export const usePermissionStore = defineStore('permission', {
  state: () => ({
    routes: [],
    addRoutes: [],
    sidebarRouters: []
  }),

  getters: {
    menuRoutes: state => state.routes.filter(route => !route.meta?.hidden)
  },

  actions: {
    generateRoutes(roles) {
      return new Promise(resolve => {
        // 菜单可见性由 canAccessMenu（MENU_PERMISSIONS）控制；
        // admin / 平台管理员在 canAccessMenu 内已返回 true，故此处统一按权限过滤
        const accessedRoutes = filterAsyncRoutes(asyncRoutes)
        this.addRoutes = accessedRoutes
        // 合并 constantRoutes 和动态路由
        this.routes = [...constantRoutes, ...accessedRoutes]
        // 设置侧边栏路由（用于菜单显示）
        // 包括：有 component 的路由，或者有 children 的父路由
        this.sidebarRouters = this.routes.filter(route => {
          // homeGroup 路由虽然 hidden，但其 children 需要由 Sidebar 扁平化到菜单中
          if (route.meta?.hidden && !route.meta?.homeGroup) return false
          // 有 component 直接显示，或者有 children 的父路由也显示
          return route.component || (route.children && route.children.length > 0)
        })
        resolve(accessedRoutes)
      })
    },

    resetState() {
      this.routes = []
      this.addRoutes = []
      this.sidebarRouters = []
    }
  }
})
