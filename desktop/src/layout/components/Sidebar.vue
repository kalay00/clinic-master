<template>
  <div class="his-sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <svg viewBox="0 0 24 24" class="logo-icon">
          <path d="M12 21s-6.5-4.5-6.5-9.5S7.5 3 12 3s6.5 2.5 6.5 8.5S12 21 12 21z" fill="currentColor" />
          <path d="M11 8h2v3h3v2h-3v3h-2v-3H8v-2h3V8z" fill="#fff" />
        </svg>
      </div>
      <span v-if="!appStore.sidebarCollapsed" class="sidebar-title">诊所管理系统</span>
    </div>

    <div class="sidebar-menu">
      <div v-for="route in visibleRoutes" :key="route.path">
        <!-- 单个子路由或无子路由，折叠为一级菜单 -->
        <router-link
          v-if="isSingleItem(route)"
          :to="resolvePath(route.path, getFirstVisibleChild(route)?.path)"
          class="menu-item"
          :class="{ active: isActive(route) }"
        >
          <span class="menu-icon">
            <component :is="getIcon(route.meta?.icon)" v-if="route.meta?.icon" />
            <svg v-else viewBox="0 0 24 24" class="default-icon"><circle cx="12" cy="12" r="4" fill="currentColor"/></svg>
          </span>
          <span v-if="!appStore.sidebarCollapsed" class="menu-title">{{ route.meta?.title }}</span>
        </router-link>

        <!-- 有多个可见子路由，可展开 -->
        <div v-else class="menu-group">
          <div
            class="menu-item menu-group-title"
            :class="{ active: isActive(route), expanded: expandedKeys.includes(route.path) }"
            @click="toggleGroup(route.path)"
          >
            <span class="menu-icon">
              <component :is="getIcon(route.meta?.icon)" v-if="route.meta?.icon" />
              <svg v-else viewBox="0 0 24 24" class="default-icon"><circle cx="12" cy="12" r="4" fill="currentColor"/></svg>
            </span>
            <span v-if="!appStore.sidebarCollapsed" class="menu-title">{{ route.meta?.title }}</span>
            <svg v-if="!appStore.sidebarCollapsed" viewBox="0 0 24 24" class="arrow-icon">
              <path d="M7 10l5 5 5-5z" fill="currentColor" />
            </svg>
          </div>
          <div v-show="!appStore.sidebarCollapsed && expandedKeys.includes(route.path)" class="submenu">
            <router-link
              v-for="child in getVisibleChildren(route)"
              :key="child.path"
              :to="resolvePath(route.path, child.path)"
              class="submenu-item"
              :class="{ active: isActiveChild(route, child) }"
            >
              {{ child.meta?.title }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePermissionStore } from '@/store/modules/permission'
import { useAppStore } from '@/store/modules/app'
import * as Icons from '@element-plus/icons-vue'

const route = useRoute()
const permissionStore = usePermissionStore()
const appStore = useAppStore()

const expandedKeys = ref([])

const visibleRoutes = computed(() => {
  const routes = permissionStore.sidebarRouters || []
  const result = []
  routes.forEach(route => {
    // 首页分组路由：扁平化其 children 为一级菜单项
    if (route.meta?.homeGroup && route.children) {
      route.children.forEach(child => {
        if (!child.meta?.hidden) {
          result.push({
            ...child,
            path: child.path.startsWith('/') ? child.path : `/${child.path}`,
            meta: { ...child.meta, parentPath: '/' }
          })
        }
      })
    } else if (!route.meta?.hidden && route.path !== '/') {
      result.push(route)
    }
  })
  return result
})

function getVisibleChildren(parentRoute) {
  return (parentRoute.children || []).filter(c => !c.meta?.hidden)
}

function getFirstVisibleChild(parentRoute) {
  return getVisibleChildren(parentRoute)[0]
}

function isSingleItem(parentRoute) {
  const children = getVisibleChildren(parentRoute)
  return children.length <= 1
}

function resolvePath(parentPath, childPath) {
  if (!childPath) return parentPath
  const base = parentPath.replace(/\/$/, '')
  const child = childPath.replace(/^\//, '')
  return `${base}/${child}`
}

function getIcon(name) {
  return Icons[name] || null
}

function isActive(parentRoute) {
  if (route.path === parentRoute.path) return true
  if (route.path.startsWith(parentRoute.path + '/')) return true
  return (parentRoute.children || []).some(c => route.path.startsWith(resolvePath(parentRoute.path, c.path)))
}

function isActiveChild(parentRoute, childRoute) {
  return route.path.startsWith(resolvePath(parentRoute.path, childRoute.path))
}

function toggleGroup(path) {
  const idx = expandedKeys.value.indexOf(path)
  if (idx > -1) {
    expandedKeys.value.splice(idx, 1)
  } else {
    expandedKeys.value.push(path)
  }
}
</script>

<style lang="scss" scoped>
.his-sidebar {
  width: v-bind('appStore.sidebarWidth');
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  transition: width 0.28s;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
  z-index: 100;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.sidebar-logo {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #5b7cff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.logo-icon {
  width: 20px;
  height: 20px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 44px;
  padding: 0 16px;
  margin: 4px 12px;
  border-radius: 8px;
  color: #4b5563;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.menu-item:hover {
  background: #f5f7ff;
  color: #5b7cff;
}

.menu-item.active {
  background: #eef1ff;
  color: #5b7cff;
}

.menu-item.active::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 8px;
  bottom: 8px;
  width: 4px;
  border-radius: 0 4px 4px 0;
  background: #5b7cff;
}

.collapsed .menu-item {
  justify-content: center;
  padding: 0;
}

.collapsed .menu-item.active::before {
  left: 0;
}

.menu-icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon svg,
.menu-icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.default-icon {
  width: 18px;
  height: 18px;
  color: #9ca3af;
}

.menu-title {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  flex: 1;
}

.arrow-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.menu-group-title.expanded .arrow-icon {
  transform: rotate(180deg);
}

.submenu {
  padding-left: 46px;
  padding-bottom: 4px;
}

.submenu-item {
  display: block;
  height: 36px;
  line-height: 36px;
  padding: 0 16px;
  color: #6b7280;
  font-size: 13px;
  text-decoration: none;
  border-radius: 6px;
  margin-right: 12px;
}

.submenu-item:hover {
  color: #5b7cff;
  background: #f5f7ff;
}

.submenu-item.active {
  color: #5b7cff;
  background: #eef1ff;
}

/* 滚动条 */
.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}
.sidebar-menu::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}
</style>
