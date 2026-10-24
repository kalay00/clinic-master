<template>
  <div class="stat-inspection-page">
    <el-card class="page-card" shadow="never">
      <div class="page-body">
      <el-empty description="后端暂未提供检查项目统计报表接口，待后端补充 /report/inspections 后接入。" />
    
      </div>
        </el-card>
  </div>
</template>

<script setup>
defineOptions({ name: 'StatInspection' })
</script>

<style lang="scss" scoped>
/* 固定高度布局 */
.stat-inspection-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
.page-card {
  height: 100%;
  :deep(.el-card__body) { height: 100%; display: flex; flex-direction: column; padding: 16px 20px; }
}
.page-body { flex: 1; display: flex; flex-direction: column; justify-content: center; min-height: 0; }
</style>
