<template>
  <div class="page-card">
    <div class="page-title">新增角色</div>
    <el-form :model="form" label-width="90px" class="form-body">
      <el-form-item label="角色名称" required>
        <el-input v-model="form.name" placeholder="角色名称" />
      </el-form-item>
      <el-form-item label="角色编码" required>
        <el-input v-model="form.code" placeholder="如 doctor_admin" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="2" />
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
import { createRole } from '@/api/role'

const router = useRouter()
const submitting = ref(false)
const form = reactive({ name: '', code: '', description: '' })

async function submit() {
  if (!form.name || !form.code) {
    ElMessage.warning('请填写角色名称和编码')
    return
  }
  submitting.value = true
  try {
    await createRole({ name: form.name, code: form.code, description: form.description || undefined })
    ElMessage.success('新增成功')
    router.push({ name: 'Role' })
  } finally {
    submitting.value = false
  }
}

function onBack() {
  router.push({ name: 'Role' })
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
