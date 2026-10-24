<template>
  <div class="settings-form-page">
    <el-card class="page-card" shadow="never">
    <el-form :model="form" label-width="100px" style="max-width: 560px" v-loading="loading">
      <el-form-item label="用户名">
        <el-input v-model="form.username" disabled />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="form.real_name" placeholder="请输入姓名" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="20" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="所属角色">
        <div class="role-tags">
          <el-tag v-for="r in roles" :key="r.id || r.code || r" size="small" type="info">
            {{ r.name || r.code || r }}
          </el-tag>
          <span v-if="!roles.length" class="text-muted">-</span>
        </div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
        <el-button @click="fetchProfile">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMe, updateMe } from '@/api/auth'
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const roles = ref([])
const form = reactive({ username: '', real_name: '', phone: '', email: '' })

async function fetchProfile() {
  loading.value = true
  try {
    const info = await getMe()
    form.username = info.username || ''
    form.real_name = info.real_name || info.name || ''
    form.phone = info.phone || ''
    form.email = info.email || ''
    roles.value = info.roles || []
  } finally {
    loading.value = false
  }
}

async function submit() {
  if (!form.real_name) {
    ElMessage.warning('请输入姓名')
    return
  }
  submitting.value = true
  try {
    await updateMe({
      real_name: form.real_name,
      phone: form.phone || undefined,
      email: form.email || undefined,
    })
    ElMessage.success('保存成功')
    // 同步本地用户信息展示
    if (userStore.userInfo) {
      userStore.setUserInfo({ ...userStore.userInfo, real_name: form.real_name, name: form.real_name })
    }
    fetchProfile()
  } finally {
    submitting.value = false
  }
}

onMounted(fetchProfile)
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动 */
.settings-form-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
.page-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  :deep(.el-card__body) { flex: 1; overflow: auto; min-height: 0; padding: 16px 20px; }
}
</style>
