<template>
<div class="his-page">
  <div class="his-page-head">
  <div>
    <div class="his-page-title">医生业绩统计</div>
  </div>
  <div class="his-toolbar-right"><button class="his-btn his-btn-default">导出</button></div>
</div>
  
  <div class="his-card">
    <div class="his-toolbar"><div class="his-form-item-inline">
  <span class="his-form-label">订单时间</span>
  <input class="his-input" value="2019-10-17 - 2019-10-17" style="width:180px" />
</div><div class="his-form-item-inline">
  <select class="his-select" style="width:120px"><option>医生</option></select>
</div></div>
    <div class="his-table-wrap">
  <table class="his-table">
    <thead><tr><th>序号</th><th>医生</th><th>应收金额（元）</th><th>优惠金额（元）</th><th>实收金额（元）</th><th>接诊人次</th><th>初诊人次</th><th>复诊人次</th><th>西/成药费（元）</th><th>中药费（元）</th><th>检查项目（元）</th><th>挂号费（元）</th><th>诊疗费（元）</th></tr></thead>
    <tbody><tr><td>1</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>2</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>3</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>4</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr></tbody>
  </table>
</div>
    <div class="his-pagination">
  <button class="his-page-btn" disabled>&lt;</button>
  <button class="his-page-btn active">1</button>
  <button class="his-page-btn">2</button>
  <button class="his-page-btn">3</button>
  <button class="his-page-btn">4</button>
  <button class="his-page-btn">5</button>
  <span>...</span>
  <button class="his-page-btn">60</button>
  <button class="his-page-btn">&gt;</button>
  <span>每页10条，共30条</span>
  <span>前往第</span>
  <input class="his-page-input" value="1" />
  <span>页</span>
</div>
  </div>
</div>
</template>

<script setup>
import { reactive } from 'vue'
const query = reactive({ page:1, pageSize:10, keyword:'' })
const onSearch = () => {}
const onReset = () => {}
const onExport = () => {}

</script>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
</style>
