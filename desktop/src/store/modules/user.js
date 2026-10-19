import { defineStore } from 'pinia'
import { storage } from '@/utils/storage'
import config from '@/config'
import authApi from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: storage.get('token') || '',
    userInfo: null,
    roles: [],
    permissions: [],
    isPlatformAdmin: false,
    // 多租户登录等待选租户阶段的临时态
    tempToken: '',
    tempTenants: [],
    tempUserId: ''
  }),

  getters: {
    isLoggedIn: state => !!state.token,
    userName: state => state.userInfo?.name || state.userInfo?.username || '',
    userAvatar: state => state.userInfo?.avatar || '',
    isAdmin: state => state.roles.includes('admin')
  },

  actions: {
    setToken(token) {
      this.token = token
      storage.set('token', token)
    },

    setUserInfo(info) {
      this.userInfo = info
    },

    setRoles(roles) {
      this.roles = roles
    },

    setPermissions(permissions) {
      this.permissions = permissions
    },

    async login(loginForm) {
      const data = await authApi.login({
        username: loginForm.username,
        password: loginForm.password
      })
      // 多租户账号：后端要求先选择租户，下发短期 temp_token + 租户列表（无 access_token）
      if (data && data.requires_tenant_selection) {
        this.tempToken = data.temp_token || ''
        this.tempTenants = data.tenants || []
        this.tempUserId = data.user_id || ''
        return { requiresTenantSelection: true }
      }
      // data: { access_token, refresh_token, token_type, user, tenant_id }
      if (!data || !data.access_token) {
        throw new Error('登录返回数据异常')
      }
      this.setToken(data.access_token)
      // 拉取完整用户信息（含角色、权限、租户）
      await this.getUserInfo()
      return { requiresTenantSelection: false }
    },

    // 选择租户：用 temp_token 鉴权调用切换租户接口，拿到正式 access_token
    async selectTenant(tenantId) {
      if (!this.tempToken) {
        throw new Error('登录状态已失效，请重新登录')
      }
      // 临时用 temp_token 作为 Bearer，供请求拦截器自动带上
      this.setToken(this.tempToken)
      try {
        const data = await authApi.switchTenant({ tenant_id: tenantId })
        if (!data || !data.access_token) {
          throw new Error('切换租户返回数据异常')
        }
        // 用正式 token 覆盖临时 token
        this.setToken(data.access_token)
        await this.getUserInfo()
        // 清理临时态
        this.tempToken = ''
        this.tempTenants = []
        this.tempUserId = ''
        return data
      } catch (e) {
        // 保留 temp 态以便重试，但把 token 复位为空避免脏状态
        this.token = ''
        storage.remove('token')
        throw e
      }
    },

    async getUserInfo() {
      const info = await authApi.getMe()
      this.setUserInfo(info)
      const roleCodes = (info.roles || []).map(r => (typeof r === 'string' ? r : r.code)).filter(Boolean)
      // 平台管理员无租户角色，但可访问全部菜单
      if (info.is_platform_admin && !roleCodes.includes('admin')) {
        roleCodes.push('admin')
      }
      this.isPlatformAdmin = !!info.is_platform_admin
      this.setRoles(roleCodes)
      this.setPermissions(info.permissions || [])
      return info
    },

    async logout() {
      try {
        await authApi.logout()
      } catch (e) {
        // 忽略登出接口错误，仍执行本地清理
      }
      this.resetState()
    },

    resetState() {
      this.token = ''
      this.userInfo = null
      this.roles = []
      this.permissions = []
      this.isPlatformAdmin = false
      storage.remove('token')
    }
  },

  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['token', 'userInfo', 'roles', 'permissions', 'isPlatformAdmin', 'tempToken', 'tempTenants', 'tempUserId']
  }
})
