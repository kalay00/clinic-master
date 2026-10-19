<template>
  <div class="app-footer">
    <span class="footer-text">© {{ year }} 华宣诊所管理系统 · v{{ version }}</span>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const year = new Date().getFullYear()
const version = __APP_VERSION__
</script>

<style lang="scss" scoped>
.app-footer {
  height: $footer-height;
  background: $header-bg;
  border-top: 1px solid $border-color-lighter;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 $spacing-base;
}

.footer-text {
  font-size: $font-size-xs;
  color: $text-secondary;
}
</style>
