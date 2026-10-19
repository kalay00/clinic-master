<template>
  <div class="title-bar" :class="{ 'is-dark': appStore.isDark }">
    <div class="title-left">
      <span class="title-text">{{ settingsStore.title }}</span>
    </div>
    <div class="title-right">
      <div class="win-btn min-btn" @click="minimize" title="最小化">
        <el-icon><Minus /></el-icon>
      </div>
      <div class="win-btn max-btn" @click="maximize" :title="isMaximized ? '还原' : '最大化'">
        <el-icon v-if="!isMaximized"><FullScreen /></el-icon>
        <el-icon v-else><CopyDocument /></el-icon>
      </div>
      <div class="win-btn close-btn" @click="close" title="关闭">
        <el-icon><Close /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/store/modules/app'
import { useSettingsStore } from '@/store/modules/settings'

const appStore = useAppStore()
const settingsStore = useSettingsStore()
const isMaximized = ref(false)

function minimize() {
  window.electronAPI?.sendMsg('window-min')
}

function maximize() {
  window.electronAPI?.sendMsg('window-max')
  isMaximized.value = !isMaximized.value
}

function close() {
  window.electronAPI?.sendMsg('window-close')
}

function handleMaximized() {
  isMaximized.value = true
}

function handleUnmaximized() {
  isMaximized.value = false
}

onMounted(() => {
  if (window.electronAPI?.onMsg) {
    // 预留：主进程推送最大化/还原状态
  }
})
</script>

<style lang="scss" scoped>
.title-bar {
  height: 32px;
  background: #f5f5f5;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-xs;
  -webkit-app-region: drag;
  user-select: none;

  &.is-dark {
    background: #1f1f1f;
    border-bottom-color: #333;

    .title-text {
      color: #ccc;
    }

    .win-btn {
      color: #ccc;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      &.close-btn:hover {
        background: #e81123;
        color: #fff;
      }
    }
  }
}

.title-left {
  padding-left: $spacing-sm;
}

.title-text {
  font-size: $font-size-sm;
  color: $text-regular;
  font-weight: 500;
}

.title-right {
  display: flex;
  align-items: center;
  -webkit-app-region: no-drag;
}

.win-btn {
  width: 40px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: $text-regular;
  font-size: 14px;
  transition: background 0.2s;

  &:hover {
    background: rgba(0, 0, 0, 0.06);
  }

  &.close-btn:hover {
    background: #e81123;
    color: #fff;
  }
}
</style>
