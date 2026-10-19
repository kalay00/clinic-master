<template>
  <div class="page-card">
    <div class="page-title">新增供应商</div>
    <el-form :model="form" label-width="90px" class="form-body">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="名称" required>
            <el-input v-model="form.name" placeholder="供应商名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="编码">
            <el-input v-model="form.code" placeholder="选填" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="联系人">
            <el-input v-model="form.contact_name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话">
            <el-input v-model="form.contact_phone" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="邮箱">
        <el-input v-model="form.contact_email" />
      </el-form-item>
      <el-form-item label="地址">
        <el-input v-model="form.address" />
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
import { createSupplier } from '@/api/inventory'

const router = useRouter()
const submitting = ref(false)
const form = reactive({
  name: '', code: '', contact_name: '', contact_phone: '',
  contact_email: '', address: '', status: 'active', remark: '',
})

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入供应商名称')
    return
  }
  submitting.value = true
  try {
    await createSupplier({
      name: form.name, code: form.code || undefined,
      contact_name: form.contact_name || undefined, contact_phone: form.contact_phone || undefined,
      contact_email: form.contact_email || undefined, address: form.address || undefined,
      status: form.status, remark: form.remark || undefined,
    })
    ElMessage.success('新增成功')
    router.push({ name: 'Supplier' })
  } finally {
    submitting.value = false
  }
}

function onBack() {
  router.push({ name: 'Supplier' })
}
</script>

<style scoped lang="scss">
.form-body {
  max-width: 640px;
}
.footer-bar {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}
</style>
