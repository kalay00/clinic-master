<template>
  <el-dialog
    v-model="visible"
    title="调用处方模板"
    width="760px"
    append-to-body
    @open="reset"
  >
    <!-- 筛选区 -->
    <el-form :inline="true" class="filter-bar">
      <el-form-item label="模板名称">
        <el-input v-model="filters.name" placeholder="请输入" clearable />
      </el-form-item>
      <el-form-item label="模板分类">
        <el-select v-model="filters.category" placeholder="请选择" clearable style="width: 160px">
          <el-option label="常用处方" value="common" />
          <el-option label="协定处方" value="agreement" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
      </el-form-item>
    </el-form>

    <!-- 模板表格 -->
    <el-table :data="templates" border max-height="320" @expand-change="onExpand">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="detail-box">
            <div class="detail-grid">
              <div><span class="d-label">模板分类：</span>{{ row.categoryName }}</div>
              <div><span class="d-label">模板名称：</span>{{ row.name }}</div>
              <div><span class="d-label">创建人员：</span>{{ row.creator }}</div>
              <div><span class="d-label">创建时间：</span>{{ row.createTime }}</div>
            </div>
            <el-table :data="row.items" border size="small" class="detail-table">
              <el-table-column type="index" label="序号" width="50" />
              <el-table-column prop="name" label="药品名称" min-width="160" />
              <el-table-column prop="spec" label="规格" width="100" />
              <el-table-column prop="usage" label="用法" width="90" />
              <el-table-column prop="frequency" label="频次" width="90" />
              <el-table-column prop="days" label="天数" width="70" />
              <el-table-column prop="total" label="总量" width="90" />
            </el-table>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="模板名称" min-width="160" />
      <el-table-column prop="categoryName" label="模板分类" width="140" />
      <el-table-column prop="creator" label="创建人员" width="120" />
      <el-table-column prop="createTime" label="创建时间" width="160" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="onUse(row)">调用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const visible = defineModel({ type: Boolean, default: false })
const emit = defineEmits(['confirm'])

const filters = ref({ name: '', category: '' })

const templates = ref([
  {
    id: 1, name: '感冒发热方', categoryName: '常用处方', creator: '王阳明', createTime: '2026-08-01 09:30',
    items: [
      { name: '阿莫西林胶囊', spec: '0.25g*20', usage: '口服', frequency: '一天3次', days: '3', total: '2盒' },
      { name: '布洛芬缓释胶囊', spec: '0.3g*20', usage: '口服', frequency: '一天2次', days: '3', total: '1盒' },
    ],
  },
  {
    id: 2, name: '咳嗽咳痰方', categoryName: '协定处方', creator: '张仲景', createTime: '2026-07-28 14:12',
    items: [
      { name: '蜜炼川贝枇杷膏', spec: '138g', usage: '口服', frequency: '一天3次', days: '5', total: '1瓶' },
      { name: '复方甘草片', spec: '100片', usage: '含服', frequency: '一天3次', days: '5', total: '1瓶' },
    ],
  },
])

const reset = () => { filters.value = { name: '', category: '' } }
const onSearch = () => ElMessage.info('按条件查询模板')
const onExpand = () => {}
const onUse = (row) => {
  emit('confirm', row)
  ElMessage.success(`已调用模板「${row.name}」`)
  visible.value = false
}
</script>

<style lang="scss" scoped>
.filter-bar {
  margin-bottom: 12px;
}
.detail-box {
  padding: 8px 16px;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px 32px;
  margin-bottom: 10px;
  .d-label {
    color: #909399;
  }
}
.detail-table {
  margin-top: 4px;
}
</style>
