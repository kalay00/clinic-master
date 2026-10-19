<template>
  <div class="layout-container" :class="{ 'sidebar-collapsed': appStore.sidebarCollapsed }">
    <TitleBar v-if="isElectron" />
    <div class="layout-wrapper">
      <Sidebar />
      <div class="main-container">
        <Navbar />
        <TagsView v-if="settingsStore.showTagsView" />
        <div class="app-main">
          <router-view v-slot="{ Component, route }">
            <transition name="fade-transform" mode="out-in">
              <keep-alive :include="tagsViewStore.cachedViews">
                <component :is="Component" :key="route.fullPath" />
              </keep-alive>
            </transition>
          </router-view>
        </div>
        <AppFooter v-if="settingsStore.showFooter" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAppStore } from '@/store/modules/app'
import { useSettingsStore } from '@/store/modules/settings'
import { useTagsViewStore } from '@/store/modules/tagsView'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
import TagsView from './components/TagsView.vue'
import TitleBar from './components/TitleBar.vue'
import AppFooter from './components/AppFooter.vue'

const appStore = useAppStore()
const settingsStore = useSettingsStore()
const tagsViewStore = useTagsViewStore()

const isElectron = computed(() => !!window.electronAPI)

onMounted(() => {
  if (isElectron.value) {
    document.body.classList.add('electron-mode')
  }
})
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &.electron-mode {
    .layout-wrapper {
      height: calc(100vh - 32px);
    }
  }
}

.layout-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: $bg-color-page;
}

.app-main {
  flex: 1;
  overflow: auto;
  padding: $spacing-base;
  @include scrollbar;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
