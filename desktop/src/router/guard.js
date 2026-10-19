import { useUserStore } from '@/store/modules/user'
import { usePermissionStore } from '@/store/modules/permission'
import { canAccessMenu } from '@/utils/permission'
import config from '@/config'
import { resetRouter } from './index'

const whiteList = config.whiteList

export function setupGuard(router) {
  router.beforeEach(async (to, from, next) => {
    document.title = to.meta?.title ? `${to.meta.title} - ${config.title}` : config.title

    const userStore = useUserStore()
    const permissionStore = usePermissionStore()
    const hasToken = userStore.token

    if (hasToken) {
      if (to.path === '/login') {
        next({ path: '/' })
      } else if (to.path === '/tenant-select') {
        // 选租户阶段（temp_token 态）直接放行，不拉取正式用户信息
        next()
      } else {
        // 初始化权限路由（用于菜单显示）
        // 当 roles 为空或 sidebarRouters 为空时都需要重新生成路由
        if (userStore.roles.length === 0 || permissionStore.sidebarRouters.length === 0) {
          try {
            await userStore.getUserInfo()
            await permissionStore.generateRoutes(userStore.roles)
          } catch (error) {
            userStore.resetState()
            permissionStore.resetState()
            resetRouter()
            next(`/login?redirect=${to.path}`)
            return
          }
        }

        // 检查路由权限（基于菜单权限映射，admin/平台管理员在 canAccessMenu 内已放行）
        if (!canAccessMenu(to.name)) {
          next({ path: '/403' })
        } else {
          next()
        }
      }
    } else {
      if (whiteList.includes(to.path)) {
        next()
      } else {
        next(`/login?redirect=${to.path}`)
      }
    }
  })

  router.afterEach((to, from) => {
    // 路由跳转后可添加埋点、标签页添加等逻辑
  })

  router.onError(error => {
    console.error('路由错误:', error)
  })
}
