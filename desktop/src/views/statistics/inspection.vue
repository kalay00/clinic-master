<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">检查项目统计</div>
    </div>
    <el-card class="page-card" shadow="never">
      <el-empty description="后端暂未提供检查项目统计报表接口，待后端补充 /report/inspections 后接入。" />
    </el-card>
  </div>
</template>

<script setup>
defineOptions({ name: 'StatInspection' })
</script>

<style lang="scss" scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>
