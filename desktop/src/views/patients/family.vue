<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑家庭成员' : '添加家庭成员'" width="560px" :close-on-click-modal="false" @close="onCancel">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" class="family-form">
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="家庭关系" prop="relation" required>
            <el-select v-model="form.relation" placeholder="请选择" style="width: 100%">
              <el-option label="父子" value="父子" />
              <el-option label="父女" value="父女" />
              <el-option label="母子" value="母子" />
              <el-option label="母女" value="母女" />
              <el-option label="夫妻" value="夫妻" />
              <el-option label="兄弟" value="兄弟" />
              <el-option label="姐妹" value="姐妹" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="姓名" prop="name" required>
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="年龄" prop="age">
            <el-input v-model.number="form.age" placeholder="请输入数字"><template #append>岁</template></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="出生日期" prop="birthday">
            <el-date-picker v-model="form.birthday" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="性别" prop="gender" required>
            <el-select v-model="form.gender" placeholder="请选择" style="width: 100%">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号码" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号码" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="onCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, computed, ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: Boolean,
  editing: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isEdit = computed(() => Boolean(props.editing?.id))
const formRef = ref(null)
const loading = ref(false)
const defaultForm = () => ({ relation: '', name: '', age: null, birthday: '', gender: '男', phone: '' })
const form = reactive(defaultForm())

const rules = {
  relation: [{ required: true, message: '请选择家庭关系', trigger: 'change' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }]
}

function resetForm() {
  Object.assign(form, defaultForm())
}

function fillForm(row) {
  if (!row) {
    resetForm()
    return
  }
  Object.assign(form, {
    relation: row.relation || '',
    name: row.name || '',
    age: row.age ?? null,
    birthday: row.birthday || '',
    gender: row.gender === 'female' || row.gender === '女' ? '女' : '男',
    phone: row.phone || ''
  })
}

const onCancel = () => { visible.value = false }
const onConfirm = () => {
  formRef.value?.validate((valid) => {
    if (!valid) return
    const payload = { ...form, gender: form.gender === '女' ? 'female' : 'male' }
    if (isEdit.value) payload.id = props.editing.id
    emit('confirm', payload)
    visible.value = false
    resetForm()
  })
}

watch(() => props.modelValue, (v) => {
  if (v) fillForm(props.editing)
})
</script>

<style lang="scss" scoped>
.family-form :deep(.el-form-item__label) { color: #606266; }
</style>
