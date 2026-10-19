<template>
  <el-dialog
    v-model="visible"
    title="新增处方模板"
    width="760px"
    append-to-body
    @open="reset"
  >
    <el-form :model="form" label-width="90px" class="tpl-form">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="模板名称" required>
            <el-input v-model="form.name" placeholder="请输入模板名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="模板分类" required>
            <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
              <el-option label="常用处方" value="common" />
              <el-option label="协定处方" value="agreement" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="药品明细">
        <el-table :data="form.items" border class="item-table" max-height="260">
          <el-table-column type="index" label="序号" width="50" />
          <el-table-column label="药品名称" min-width="160">
            <template #default="{ row }">
              <el-input v-model="row.name" placeholder="请输入" />
            </template>
          </el-table-column>
          <el-table-column label="规格" width="110">
            <template #default="{ row }">
              <el-input v-model="row.spec" placeholder="规格" />
            </template>
          </el-table-column>
          <el-table-column label="用法" width="100">
            <template #default="{ row }">
              <el-input v-model="row.usage" placeholder="用法" />
            </template>
          </el-table-column>
          <el-table-column label="频次" width="100">
            <template #default="{ row }">
              <el-input v-model="row.frequency" placeholder="频次" />
            </template>
          </el-table-column>
          <el-table-column label="天数" width="80">
            <template #default="{ row }">
              <el-input v-model="row.days" placeholder="天" />
            </template>
          </el-table-column>
          <el-table-column label="总量" width="100">
            <template #default="{ row }">
              <el-input v-model="row.total" placeholder="总量" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="70">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button class="add-btn" :icon="Plus" @click="addItem">添加药品</el-button>
      </el-form-item>

      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button :icon="Close" @click="visible = false">取消</el-button>
      <el-button type="primary" :icon="Check" @click="onSubmit">保存模板</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Check, Close } from '@element-plus/icons-vue'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['confirm'])

const emptyForm = () => ({
  name: '', category: '', remark: '',
  items: [{ name: '', spec: '', usage: '', frequency: '', days: '', total: '' }],
})
const form = reactive(emptyForm())

const reset = () => Object.assign(form, emptyForm())
const addItem = () => form.items.push({ name: '', spec: '', usage: '', frequency: '', days: '', total: '' })
const removeItem = (i) => form.items.splice(i, 1)

const onSubmit = () => {
  if (!form.name || !form.category) {
    ElMessage.warning('请填写模板名称和分类')
    return
  }
  emit('confirm', { ...form })
  ElMessage.success('模板保存成功')
  visible.value = false
}
</script>

<style lang="scss" scoped>
.tpl-form {
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }
}
.item-table {
  margin-bottom: 8px;
}
.add-btn {
  width: 100%;
  border-style: dashed;
}
</style>
