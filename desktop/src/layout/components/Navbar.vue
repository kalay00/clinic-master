<template>
  <div class="navbar" :class="{ 'is-dark': appStore.isDark }">
    <div class="navbar-left">
      <el-icon class="collapse-btn" @click="toggleSidebar">
        <Fold v-if="!appStore.sidebarCollapsed" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb v-if="settingsStore.showBreadcrumb" separator="/">
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.index">
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="navbar-right">
      <!-- 全局搜索 -->
      <el-tooltip :content="t('navbar.search') + ' (Ctrl+K)'">
        <el-icon class="nav-icon" @click="openSearch"><Search /></el-icon>
      </el-tooltip>
      
      <!-- 全屏 -->
      <el-tooltip :content="isFullscreen ? t('navbar.exitFullscreen') : t('navbar.fullscreen')">
        <el-icon class="nav-icon" @click="toggleFullscreen"><FullScreen /></el-icon>
      </el-tooltip>
      
      <!-- 主题切换 -->
      <el-tooltip :content="appStore.isDark ? t('navbar.light') : t('navbar.dark')">
        <el-icon class="nav-icon" @click="toggleDark">
          <Moon v-if="!appStore.isDark" />
          <Sunny v-else />
        </el-icon>
      </el-tooltip>

      <!-- 语言切换 -->
      <el-tooltip :content="t('navbar.language')">
        <el-dropdown @command="changeLanguage">
          <el-icon class="nav-icon"><Operation /></el-icon>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="zh-CN" :class="{ 'is-active': currentLocale === 'zh-CN' }">简体中文</el-dropdown-item>
              <el-dropdown-item command="en-US" :class="{ 'is-active': currentLocale === 'en-US' }">English</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-tooltip>
      
      <!-- 设置 -->
      <el-tooltip :content="t('navbar.settings')">
        <el-icon class="nav-icon" @click="goSettings"><Setting /></el-icon>
      </el-tooltip>
      
      <!-- 用户下拉菜单 -->
      <el-dropdown @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" class="user-avatar">
            <el-icon><UserFilled /></el-icon>
          </el-avatar>
          <span class="username">{{ userName }}</span>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              <span>{{ t('navbar.profile') }}</span>
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              <span>{{ t('navbar.settings') }}</span>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              <span>{{ t('navbar.logout') }}</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    
    <!-- 全局搜索对话框 -->
    <el-dialog
      v-model="searchVisible"
      :title="t('navbar.search')"
      width="500px"
      :append-to-body="true"
      class="search-dialog"
    >
      <el-input
        v-model="searchKeyword"
        :placeholder="t('navbar.search') + '...'"
        size="large"
        clearable
        @keyup.enter="handleSearch"
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="search-results" v-if="searchResults.length">
        <div class="search-result-item" v-for="item in searchResults" :key="item.path" @click="goToSearchResult(item)">
          <el-icon class="result-icon"><component :is="getIconComponent(item.icon)" /></el-icon>
          <span class="result-title">{{ item.title }}</span>
          <span class="result-path">{{ item.path }}</span>
        </div>
      </div>
      <div class="search-empty" v-else-if="searchKeyword">
        <el-empty :description="t('common.noData')" :image-size="60" />
      </div>
      <div class="search-tip" v-else>
        <p>Ctrl + K</p>
        <p>{{ t('common.search') }}: {{ t('navbar.search') }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, markRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import * as Icons from '@element-plus/icons-vue'
import { useAppStore } from '@/store/modules/app'
import { useSettingsStore } from '@/store/modules/settings'
import { useUserStore } from '@/store/modules/user'
import { usePermissionStore } from '@/store/modules/permission'
import { resetAllStore } from '@/store'
import { setLocale } from '@/locales'

// 将图标名称转换为实际组件
function getIconComponent(iconName) {
  if (!iconName) return markRaw(Icons.Document)
  const Icon = Icons[iconName]
  return Icon ? markRaw(Icon) : markRaw(Icons.Document)
}

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const appStore = useAppStore()
const settingsStore = useSettingsStore()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

const currentLocale = computed(() => locale.value)

// 搜索相关
const searchVisible = ref(false)
const searchKeyword = ref('')
const searchResults = ref([])
const isFullscreen = ref(false)

// 用户名显示
const userName = computed(() => {
  return userStore.userInfo?.nickname || userStore.userInfo?.username || '用户'
})

// 面包屑数据
const breadcrumbs = computed(() => {
  return route.matched
    .filter(item => item.meta && item.meta.title)
    .map((item, index) => ({
      path: item.path,
      name: item.name,
      title: item.meta.title,
      index: index
    }))
})

// 获取所有可搜索的菜单
const allMenus = computed(() => {
  const menus = []
  function extractMenus(routes, basePath = '') {
    routes.forEach(r => {
      if (r.meta && r.meta.title && !r.meta.hidden) {
        // 计算当前路由的完整路径
        const fullPath = r.path.startsWith('/') 
          ? r.path 
          : (basePath ? basePath + '/' + r.path : r.path)
        
        menus.push({
          path: fullPath,
          title: r.meta.title,
          icon: r.meta.icon
        })
      }
      
      // 即使当前路由没有title，只要有子路由也继续递归
      // 这样可以处理首页这类父路由无title但子路由有title的情况
      if (r.children && r.children.length > 0) {
        const currentBasePath = r.path.startsWith('/') 
          ? r.path 
          : (basePath ? basePath + '/' + r.path : r.path)
        extractMenus(r.children, currentBasePath)
      }
    })
  }
  extractMenus(permissionStore.routes)
  return menus
})

// 搜索处理
function handleSearch() {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }
  const keyword = searchKeyword.value.toLowerCase()
  searchResults.value = allMenus.value.filter(item => 
    item.title.toLowerCase().includes(keyword) ||
    item.path.toLowerCase().includes(keyword)
  ).slice(0, 10)
}

function goToSearchResult(item) {
  router.push(item.path)
  searchVisible.value = false
  searchKeyword.value = ''
}

function openSearch() {
  searchVisible.value = true
  searchKeyword.value = ''
  searchResults.value = []
}

function toggleSidebar() {
  appStore.toggleSidebar()
}

function toggleDark() {
  appStore.toggleDark()
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

function goSettings() {
  router.push('/settings/basic')
}

function changeLanguage(lang) {
  setLocale(lang)
  ElMessage.success(lang === 'zh-CN' ? '语言切换成功' : 'Language switched')
}

async function handleCommand(command) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings/basic')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(t('common.tip'), t('navbar.logout'), {
          confirmButtonText: t('common.confirm'),
          cancelButtonText: t('common.cancel'),
          type: 'warning'
        })
        resetAllStore()
        ElMessage.success(t('navbar.logout') + '!')
        router.push('/login')
      } catch (e) {}
      break
  }
}

// 监听搜索快捷键
function handleKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    openSearch()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style lang="scss" scoped>
.navbar {
  height: $header-height;
  background: $header-bg;
  border-bottom: 1px solid $border-color-lighter;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-base;
  box-shadow: $shadow-sm;
  transition: background 0.3s, border-color 0.3s;

  &.is-dark {
    background: $dark-header-bg;
    border-bottom-color: $dark-border-color;

    .collapse-btn,
    .nav-icon,
    .username,
    .dropdown-icon {
      color: $dark-text-primary;
    }

    .user-info:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    :deep(.el-breadcrumb__inner) {
      color: $dark-text-primary;
    }

    :deep(.el-breadcrumb__separator) {
      color: $dark-text-secondary;
    }
  }
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: $spacing-base;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: $text-regular;
  transition: color 0.3s;

  &:hover {
    color: $primary-color;
  }
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.nav-icon {
  font-size: 18px;
  cursor: pointer;
  color: $text-regular;
  transition: color 0.3s;
  padding: $spacing-xs;
  border-radius: $border-radius-base;

  &:hover {
    color: $primary-color;
    background: rgba(64, 158, 255, 0.1);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  cursor: pointer;
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-base;
  transition: background 0.3s;

  &:hover {
    background: $bg-color;
  }
}

.username {
  font-size: $font-size-base;
  color: $text-regular;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 12px;
  color: $text-secondary;
}

.user-avatar {
  background: $primary-color;
}

// 搜索对话框样式
.search-dialog {
  :deep(.el-dialog__header) {
    padding-bottom: 0;
  }

  :deep(.el-dialog__body) {
    padding-top: $spacing-sm;
  }
}

.search-results {
  margin-top: $spacing-base;
  max-height: 300px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-base;
  cursor: pointer;
  border-radius: $border-radius-base;
  transition: background 0.3s;

  &:hover {
    background: $bg-color;
  }

  .result-icon {
    font-size: 16px;
    color: $primary-color;
  }

  .result-title {
    font-size: $font-size-base;
    color: $text-primary;
  }

  .result-path {
    font-size: $font-size-xs;
    color: $text-secondary;
    margin-left: auto;
  }
}

.search-empty {
  padding: $spacing-lg 0;
}

.search-tip {
  padding: $spacing-lg 0;
  text-align: center;
  color: $text-secondary;

  p {
    margin: $spacing-xs 0;
    font-size: $font-size-sm;
  }
}
</style>