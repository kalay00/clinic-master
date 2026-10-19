<template>
<div class="his-page">
  <div class="his-page-head">
  <div>
    <div class="his-page-title">系统设置 - Employee List</div>
  </div>
  
</div>
  
  <div class="his-card">
    <div class="his-toolbar"></div>
    <div class="his-table-wrap">
  <table class="his-table">
    <thead><tr><th>序号</th><th>名称</th><th>创建时间</th><th>操作</th></tr></thead>
    <tbody><tr><td>1</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>2</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>3</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>4</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>5</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>6</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>7</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>8</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>9</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr><tr><td>10</td><td>-</td><td>-</td><td><span class="his-link">编辑</span> <span class="his-link danger">删除</span></td></tr></tbody>
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
