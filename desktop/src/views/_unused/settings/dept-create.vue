<template>
  <div class="page-card">
    <div class="page-title">新增科室</div>
    <el-form :model="form" label-width="90px" class="form-body">
      <el-form-item label="科室名称" required>
        <el-input v-model="form.name" placeholder="请输入科室名称" />
      </el-form-item>
      <el-form-item label="科室编码">
        <el-input v-model="form.code" placeholder="选填" />
      </el-form-item>
      <el-form-item label="科室描述">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="状态">
        <el-radio-group v-model="form.status">
          <el-radio value="enabled">启用</el-radio>
          <el-radio value="disabled">停用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <div class="footer-bar">
      <el-button @click="onBack">返回</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createDepartment } from '@/api/department'

const router = useRouter()
const submitting = ref(false)
const form = reactive({ name: '', code: '', description: '', status: 'enabled' })

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入科室名称')
    return
  }
  submitting.value = true
  try {
    await createDepartment({
      name: form.name,
      code: form.code || undefined,
      description: form.description || undefined,
      status: form.status,
    })
    ElMessage.success('新增成功')
    router.push({ name: 'Dept' })
  } finally {
    submitting.value = false
  }
}

function onBack() {
  router.push({ name: 'Dept' })
}
</script>

<style scoped lang="scss">
.form-body {
  max-width: 520px;
}
.footer-bar {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}
</style>
