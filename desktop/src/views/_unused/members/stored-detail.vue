<template>
<div class="his-page">
  <div class="his-page-head">
  <div>
    <div class="his-page-title">会员管理 - Stored Detail</div>
  </div>
  <div class="his-toolbar-right"><button class="his-btn his-btn-default">返回</button></div>
</div>
  <div class="his-card">
    <div class="his-section-title">基本信息</div><div class="his-info-row"><div class="his-info-item"><span class="his-info-label">名称：</span><span class="his-info-value">-</span></div></div>
  </div>
</div>
</template>

<script setup>
import { reactive } from 'vue'
const form = reactive({})
const onSubmit = () => {}
const onBack = () => {}

</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
</style>
