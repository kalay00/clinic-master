<template>
  <div class="app-container">
    <div class="page-head">
      <div class="page-title">库存管理</div>
      <div class="head-actions">
        <el-button :icon="Download" @click="onExport">导出</el-button>
      </div>
    </div>

    <el-card class="page-card" shadow="never">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="处方类别">
          <el-select v-model="query.category" placeholder="全部" clearable style="width: 130px">
            <el-option label="全部" value="" />
            <el-option label="西/成药" value="western" />
            <el-option label="中成药" value="chinese" />
            <el-option label="中药" value="herb" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="输入药品名称/编码/生产厂家" style="width: 260px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
        </el-form-item>
        <el-form-item class="filter-right">
          <el-link type="primary" :icon="Warning" @click="onStockWarning">库存预警</el-link>
          <el-link type="primary" :icon="Calendar" @click="onExpireWarning" class="ml-md">有效期预警</el-link>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="drug_code" label="药品编码" width="100" />
        <el-table-column prop="drug_name" label="药品名称" min-width="160" />
        <el-table-column prop="specification" label="规格" width="110" />
        <el-table-column prop="supplier_name" label="供应商" min-width="140" />
        <el-table-column prop="batch_no" label="批号" width="120" />
        <el-table-column prop="quantity" label="当前库存" width="90" align="right" />
        <el-table-column prop="min_quantity" label="库存下限" width="90" align="right" />
        <el-table-column prop="expiry_date" label="有效期至" width="120" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.quantity <= row.min_quantity ? 'danger' : 'success'" size="small">
              {{ row.quantity <= row.min_quantity ? '库存预警' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="onDetail(row)">查看</el-button>
            <el-button type="primary" link :icon="Setting" @click="onAdjust(row)">调整</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="summary-bar">
        <span>采购金额合计：<span class="amount">67379.12元</span></span>
        <span class="ml-lg">零售金额合计：<span class="amount">81111.08元</span></span>
      </div>

      <el-pagination
        class="list-pagination"
        v-model:current-page="query.page"
        v-model:page-size="query.pageSize"
        layout="total, prev, pager, next, jumper"
        :total="total"
        @current-change="onSearch"
        @size-change="onSearch"
      />
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, View, Warning, Calendar, Setting, Download } from '@element-plus/icons-vue'
import { getInventory, getInventoryWarnings } from '@/api/pharmacy'

defineOptions({ name: 'DrugStock' })

const router = useRouter()
const loading = ref(false)
const total = ref(0)
const tableData = ref([])

const query = reactive({
  page: 1, pageSize: 10,
  category: '', keyword: ''
})

async function onSearch() {
  loading.value = true
  try {
    const data = await getInventory({
      page: query.page,
      pageSize: query.pageSize,
      keyword: query.keyword || undefined
    })
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    ElMessage.error('加载库存列表失败')
  } finally {
    loading.value = false
  }
}
const onStockWarning = async () => {
  try {
    const data = await getInventoryWarnings()
    const list = (data.items || data.low_stock || [])
    ElMessage.info(`当前库存预警药品 ${list.length} 种`)
  } catch (e) { ElMessage.error('获取库存预警失败') }
}
const onExpireWarning = () => ElMessage.info('有效期预警功能开发中')
const onExport = () => ElMessage.info('导出功能开发中')
const onDetail = (row) => router.push(`/drugs/stock/detail/${row.drug_id || row.id}`)
const onAdjust = (row) => ElMessage.info('调整库存功能开发中')

onMounted(onSearch)
</script>

<style lang="scss" scoped>
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.head-actions {
  display: flex;
  gap: 10px;
}
.filter-form {
  margin-bottom: 12px;
  :deep(.el-form-item) {
    margin-bottom: 10px;
  }
}
.filter-right {
  margin-left: auto;
}
.summary-bar {
  margin-top: 12px;
  font-size: 14px;
  color: #606266;
  .amount {
    color: #f56c6c;
    font-weight: 600;
  }
}
.list-pagination {
  justify-content: flex-end;
  margin-top: 12px;
}
</style>
