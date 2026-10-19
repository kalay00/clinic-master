<template>
  <div class="error-page">
    <div class="error-code">403</div>
    <div class="error-title">无权访问该页面</div>
    <button class="his-btn his-btn-primary" @click="$router.push('/')">返回首页</button>
  </div>
</template>

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
  color: #ff6b6b;
  line-height: 1;
}
.error-title {
  font-size: 18px;
  color: #606266;
  margin: 16px 0 24px;
}
</style>
