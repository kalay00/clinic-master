<template>
  <div class="page-card">
    <div class="page-title">新增药品分类</div>
    <el-form :model="form" label-width="90px" class="form-body">
      <el-form-item label="分类名称" required>
        <el-input v-model="form.name" placeholder="请输入分类名称" />
      </el-form-item>
      <el-form-item label="排序">
        <el-input-number v-model="form.sort" :min="0" />
      </el-form-item>
      <el-form-item label="状态">
        <el-radio-group v-model="form.status">
          <el-radio value="active">启用</el-radio>
          <el-radio value="inactive">停用</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="2" />
      </el-form-item>
    </el-form>
    <div class="footer-bar">
      <el-button @click="onBack">返回</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createDrugCategory } from '@/api/pharmacy'

const router = useRouter()
const submitting = ref(false)
const form = reactive({ name: '', sort: 0, status: 'active', remark: '' })

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  submitting.value = true
  try {
    await createDrugCategory({
      name: form.name, sort: form.sort, status: form.status, remark: form.remark || undefined,
    })
    ElMessage.success('新增成功')
    router.push({ name: 'DrugCategory' })
  } finally {
    submitting.value = false
  }
}

function onBack() {
  router.push({ name: 'DrugCategory' })
}
</script>

<style scoped lang="scss">
.form-body {
  max-width: 480px;
}
.footer-bar {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}
</style>
