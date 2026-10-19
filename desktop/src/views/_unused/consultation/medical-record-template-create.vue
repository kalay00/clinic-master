<template>
<div class="his-page">
  <div class="his-page-head">
  <div>
    <div class="his-page-title">新开就诊 - Medical Record Template Create</div>
  </div>
  <div class="his-toolbar-right"><button class="his-btn his-btn-primary" @click="onSubmit">保存</button><button class="his-btn his-btn-default" @click="onBack">返回</button></div>
</div>
  <div class="his-card">
    <div class="his-section-title">基本信息</div><div class="his-form-row"><div class="his-form-item">
  <label class="his-form-label required">名称</label>
  <input class="his-input" type="text" placeholder="请输入" v-model="form.name" />
</div><div class="his-form-item">
  <label class="his-form-label">备注</label>
  <input class="his-input" type="text" placeholder="" v-model="form.remark" />
</div></div>
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
