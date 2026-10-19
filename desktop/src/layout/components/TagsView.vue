<template>
  <div class="tags-view-container" :class="{ 'is-dark': appStore.isDark }">
    <el-scrollbar class="tags-scroll">
      <div class="tags-wrapper">
        <span
          v-for="tag in visitedViews"
          :key="tag.path"
          class="tag-item"
          :class="{ active: isActive(tag), affix: tag.meta?.affix }"
          @click="handleClick(tag)"
          @contextmenu.prevent="openContextMenu(tag, $event)"
        >
          <el-icon v-if="tag.meta?.icon" class="tag-icon">
            <component :is="tag.meta.icon" />
          </el-icon>
          <span class="tag-title">{{ tag.title }}</span>
          <el-icon
            v-if="!tag.meta?.affix"
            class="tag-close"
            @click.stop="handleClose(tag)"
          >
            <Close />
          </el-icon>
        </span>
      </div>
    </el-scrollbar>

    <!-- 右键菜单 -->
    <ul
      v-show="contextMenuVisible"
      class="context-menu"
      :style="{ left: contextMenuLeft + 'px', top: contextMenuTop + 'px' }"
    >
      <li @click="refreshSelectedTag(selectedTag)">
        <el-icon><Refresh /></el-icon>
        <span>刷新</span>
      </li>
      <li v-if="!selectedTag?.meta?.affix" @click="closeSelectedTag(selectedTag)">
        <el-icon><Close /></el-icon>
        <span>关闭</span>
      </li>
      <li @click="closeOthersTags">
        <el-icon><FolderRemove /></el-icon>
        <span>关闭其他</span>
      </li>
      <li @click="closeLeftTags">
        <el-icon><Back /></el-icon>
        <span>关闭左侧</span>
      </li>
      <li @click="closeRightTags">
        <el-icon><Right /></el-icon>
        <span>关闭右侧</span>
      </li>
      <li class="divider"></li>
      <li @click="closeAllTags">
        <el-icon><CircleClose /></el-icon>
        <span>关闭全部</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTagsViewStore } from '@/store/modules/tagsView'
import { useAppStore } from '@/store/modules/app'

const route = useRoute()
const router = useRouter()
const tagsViewStore = useTagsViewStore()
const appStore = useAppStore()

// 初始化时确保首页存在且在第一位
tagsViewStore.ensureHomeView()

// 右键菜单状态
const contextMenuVisible = ref(false)
const contextMenuLeft = ref(0)
const contextMenuTop = ref(0)
const selectedTag = ref(null)

const visitedViews = computed(() => tagsViewStore.visitedViews)

// 判断当前激活标签
function isActive(tag) {
  return tag.path === route.path
}

// 监听路由变化，添加标签页
watch(
  () => route.fullPath,
  () => {
    if (route.name && route.meta?.title) {
      tagsViewStore.addView({
        path: route.path,
        name: route.name,
        fullPath: route.fullPath,
        meta: route.meta || {},
        title: route.meta?.title || '未命名'
      })
      tagsViewStore.ensureHomeView()
    }
  },
  { immediate: true }
)

// 点击标签页
function handleClick(tag) {
  router.push(tag.path)
}

// 关闭标签页
function handleClose(tag) {
  if (tag.meta?.affix) return
  closeSelectedTag(tag)
}

// 关闭指定标签
function closeSelectedTag(tag) {
  if (!tag || tag.meta?.affix) return
  tagsViewStore.delView(tag).then(({ visitedViews }) => {
    if (isActive(tag)) {
      toLastView(visitedViews)
    }
  })
}

// 刷新当前标签
function refreshSelectedTag(tag) {
  if (!tag) return
  tagsViewStore.delCachedView({ name: tag.name })
  router.replace({ path: '/redirect' + tag.fullPath })
  closeContextMenu()
}

// 关闭其他标签
function closeOthersTags() {
  if (!selectedTag.value) return
  tagsViewStore.delOthersViews({
    path: selectedTag.value.path,
    name: selectedTag.value.name,
    meta: selectedTag.value.meta
  })
  if (!isActive(selectedTag.value)) {
    router.push(selectedTag.value.path)
  }
  closeContextMenu()
}

// 关闭左侧标签
function closeLeftTags() {
  if (!selectedTag.value) return
  const currentIndex = visitedViews.value.findIndex(v => v.path === selectedTag.value.path)
  if (currentIndex > 0) {
    visitedViews.value.slice(0, currentIndex).forEach(tag => {
      if (!tag.meta?.affix) {
        tagsViewStore.delView(tag)
      }
    })
  }
  if (!isActive(selectedTag.value)) {
    router.push(selectedTag.value.path)
  }
  closeContextMenu()
}

// 关闭右侧标签
function closeRightTags() {
  if (!selectedTag.value) return
  const currentIndex = visitedViews.value.findIndex(v => v.path === selectedTag.value.path)
  if (currentIndex < visitedViews.value.length - 1) {
    visitedViews.value.slice(currentIndex + 1).forEach(tag => {
      if (!tag.meta?.affix) {
        tagsViewStore.delView(tag)
      }
    })
  }
  if (!isActive(selectedTag.value)) {
    router.push(selectedTag.value.path)
  }
  closeContextMenu()
}

// 关闭全部标签
function closeAllTags() {
  tagsViewStore.delAllViews()
  toLastView(tagsViewStore.visitedViews)
  closeContextMenu()
}

// 跳转到最后一个视图或首页
function toLastView(visitedViews) {
  const lastView = visitedViews[visitedViews.length - 1]
  if (lastView) {
    router.push(lastView.path)
  } else {
    router.push('/')
  }
}

// 打开右键菜单
function openContextMenu(tag, event) {
  selectedTag.value = tag
  const menuMinWidth = 120
  const offsetLeft = document.body.getBoundingClientRect().left
  const offsetWidth = document.body.offsetWidth
  const maxLeft = offsetWidth - menuMinWidth
  const left = event.clientX - offsetLeft + 10

  contextMenuLeft.value = left > maxLeft ? maxLeft : left
  contextMenuTop.value = event.clientY + 10
  contextMenuVisible.value = true
}

// 关闭右键菜单
function closeContextMenu() {
  contextMenuVisible.value = false
}

// 点击其他区域关闭右键菜单
function handleClickOutside() {
  closeContextMenu()
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style lang="scss" scoped>
.tags-view-container {
  height: 40px;
  background: #fff;
  border-bottom: 1px solid $border-color-lighter;
  display: flex;
  align-items: flex-end;
  padding-bottom: 1px;
  transition: background 0.3s, border-color 0.3s;
  position: relative;

  &.is-dark {
    background: $dark-bg-color-white;
    border-bottom-color: $dark-border-color;

    .tag-item {
      color: $dark-text-regular;
      background: $dark-bg-color;
      border-color: $dark-border-color;

      &:hover {
        color: $primary-light-color;
        background: rgba(64, 158, 255, 0.1);
      }

      &.active {
        color: $primary-color;
        background: $dark-bg-color-white;
        border-color: $primary-color;
      }
    }

    .context-menu {
      background: $dark-card-bg;
      border-color: $dark-border-color;

      li {
        color: $dark-text-regular;

        &:hover {
          background: rgba(255, 255, 255, 0.1);
        }
      }
    }
  }
}

.tags-scroll {
  flex: 1;
  height: 100%;

  :deep(.el-scrollbar__view) {
    height: 100%;
  }
}

.tags-wrapper {
  display: flex;
  align-items: flex-end;
  height: 100%;
  padding: 0 12px;
  gap: 6px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 12px;
  font-size: 12px;
  color: $text-regular;
  background: $bg-color;
  border: 1px solid $border-color-lighter;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;

  &:hover {
    color: $primary-color;
    background: rgba(64, 158, 255, 0.08);
    border-color: rgba(64, 158, 255, 0.3);
  }

  &.active {
    color: $primary-color;
    background: #fff;
    border-color: $primary-color $primary-color transparent $primary-color;

    .tag-icon {
      color: $primary-color;
    }
  }

  &.affix {
    padding-left: 14px;
  }

  .tag-icon {
    font-size: 14px;
    color: inherit;
  }

  .tag-title {
    max-width: 140px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .tag-close {
    font-size: 12px;
    margin-left: 4px;
    padding: 2px;
    border-radius: 50%;
    transition: all 0.2s;

    &:hover {
      background-color: rgba(245, 108, 108, 0.15);
      color: $danger-color;
    }
  }
}

// 右键菜单样式
.context-menu {
  position: fixed;
  z-index: 3000;
  list-style: none;
  margin: 0;
  padding: 4px 0;
  background: #fff;
  border: 1px solid $border-color-lighter;
  border-radius: 4px;
  box-shadow: $shadow-md;

  li {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    font-size: 13px;
    color: $text-regular;
    cursor: pointer;
    transition: background 0.3s;

    &:hover {
      background: rgba(64, 158, 255, 0.1);
    }

    .el-icon {
      font-size: 14px;
    }
  }

  .divider {
    height: 1px;
    margin: 4px 0;
    padding: 0;
    background: $border-color-lighter;

    &:hover {
      background: $border-color-lighter;
    }
  }
}
</style>