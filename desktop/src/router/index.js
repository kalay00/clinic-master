import { createRouter, createWebHashHistory } from 'vue-router'
import { constantRoutes, asyncRoutes } from './routes'
import { setupGuard } from './guard'

// 将所有路由合并初始化（路由守卫中仍会动态处理权限）
const allRoutes = [...constantRoutes, ...asyncRoutes]

const router = createRouter({
  history: createWebHashHistory(),
  routes: allRoutes,
  scrollBehavior: () => ({ top: 0 })
})

setupGuard(router)

export function resetRouter() {
  const newRouter = createRouter({
    history: createWebHashHistory(),
    routes: allRoutes
  })
  router.matcher = newRouter.matcher
}

export default router
