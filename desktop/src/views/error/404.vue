<template>
  <div class="error-page">
    <div class="error-code">404</div>
    <div class="error-title">页面不存在</div>
    <button class="his-btn his-btn-primary" @click="$router.push('/')">返回首页</button>
  </div>
</template>

<script setup>
</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.error-code {
  font-size: 120px;
  font-weight: 700;
  color: #5b7cff;
  line-height: 1;
}
.error-title {
  font-size: 18px;
  color: #606266;
  margin: 16px 0 24px;
}
</style>
