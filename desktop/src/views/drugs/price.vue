<template>
  <div class="price-page">
    <el-card class="page-card" shadow="never">
      <div class="card-header">
        <el-tabs v-model="activeTab" class="top-tabs" @tab-change="onTabChange">
          <el-tab-pane label="调价记录" name="records" />
          <el-tab-pane label="药品价格" name="drugs" />
        </el-tabs>
        <el-button type="primary" :icon="Plus" @click="goCreate">新增调价</el-button>
      </div>

      <div class="page-body">
        <template v-if="activeTab === 'records'">
          <el-form :inline="true" class="filter-form">
            <el-form-item label="审批状态">
              <el-select v-model="query.status" placeholder="全部" clearable style="width: 130px" @change="onSearch">
                <el-option label="全部" value="" />
                <el-option label="草稿" value="draft" />
                <el-option label="已审批" value="approved" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
              <el-button :icon="Refresh" @click="onReset">重置</el-button>
            </el-form-item>
          </el-form>

          <div class="table-wrap" ref="wrapRef">
            <el-table :data="tableData" border stripe v-loading="loading" ref="tableRef" :height="tableHeight">
              <el-table-column type="index" label="序号" width="55" />
              <el-table-column prop="adjustment_no" label="调价单号" min-width="160" />
              <el-table-column prop="adjust_date" label="调价日期" width="120" />
              <el-table-column prop="status" label="审批状态" width="90">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'approved' ? 'success' : 'info'" size="small">{{ row.status === 'approved' ? '已审批' : '草稿' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
              <el-table-column label="操作" width="140" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link :icon="View" @click="onDetail(row)">查看</el-button>
                  <el-button v-if="row.status !== 'approved'" type="success" link :icon="Check" @click="onApprove(row)">审批</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <el-pagination class="list-pagination" v-model:current-page="query.page" v-model:page-size="query.pageSize" layout="total, prev, pager, next, jumper" :total="total" @current-change="fetchList" @size-change="onSizeChange" />
        </template>

        <template v-else>
          <el-form :inline="true" class="filter-form">
            <el-form-item>
              <el-input v-model="drugQuery.search" placeholder="药品编码/名称" style="width: 220px" @keyup.enter="onDrugSearch" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="Search" @click="onDrugSearch">查询</el-button>
            </el-form-item>
          </el-form>
          <div class="table-wrap" ref="wrapRef">
            <el-table :data="drugList" border stripe v-loading="drugLoading" ref="tableRef" :height="tableHeight">
              <el-table-column prop="drug_code" label="药品编码" width="120" />
              <el-table-column prop="name" label="药品名称" min-width="160" />
              <el-table-column prop="specification" label="规格" width="120" />
              <el-table-column prop="price" label="当前售价（元）" width="120">
                <template #default="{ row }">{{ fmt(row.price) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="90" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link :icon="Edit" @click="onAdjust(row)">调价</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Check, Edit } from '@element-plus/icons-vue'
import { getPriceAdjustments, approvePriceAdjustment } from '@/api/pharmacy'
import { getDrugs } from '@/api/pharmacy'
import { useTableHeight } from '@/composables/useTableHeight'

defineOptions({ name: 'DrugPrice' })

const router = useRouter()
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const activeTab = ref('records')
const loading = ref(false)
const total = ref(0)
const query = reactive({ page: 1, pageSize: 10, status: '' })
const tableData = ref([])
const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

const drugLoading = ref(false)
const drugQuery = reactive({ search: '', page: 1, pageSize: 10 })
const drugList = ref([])

async function fetchList() {
  loading.value = true
  try {
    const res = await getPriceAdjustments({ page: query.page, page_size: query.pageSize, status: query.status || undefined })
    tableData.value = res.items || []
    total.value = res.pagination?.total || 0
  } catch (e) { ElMessage.error('加载调价记录失败') }
  finally { loading.value = false; refresh() }
}
const onSearch = () => { query.page = 1; fetchList() }
const onReset = () => { query.status = ''; query.page = 1; fetchList() }
const onSizeChange = () => { query.page = 1; fetchList() }
const goCreate = () => router.push('/drugs/price/create')
const onDetail = (row) => router.push(`/drugs/price/detail/${row.id}`)
const onApprove = async (row) => {
  try {
    await ElMessageBox.confirm(`确定审批调价单 ${row.adjustment_no}？审批后药品售价将更新。`, '提示', { type: 'warning' })
    await approvePriceAdjustment(row.id)
    ElMessage.success('审批成功，售价已更新')
    fetchList()
  } catch (e) { if (e !== 'cancel') ElMessage.error('审批失败') }
}

async function fetchDrugs() {
  drugLoading.value = true
  try {
    const res = await getDrugs({ page: drugQuery.page, page_size: drugQuery.pageSize, search: drugQuery.search || undefined })
    drugList.value = res.items || []
  } catch (e) { ElMessage.error('加载药品失败') }
  finally { drugLoading.value = false; refresh() }
}
const onDrugSearch = () => { drugQuery.page = 1; fetchDrugs() }
// 切换到药品价格 tab 时按需加载（首次或记录更新后）
const onTabChange = (name) => {
  if (name === 'drugs' && !drugList.value.length) fetchDrugs()
}
const onAdjust = (row) => router.push(`/drugs/price/create?drugId=${row.id}`)

onMounted(fetchList)
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动，筛选/分页固定，仅列表内部滚动 */
.price-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
.page-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  :deep(.el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
    padding: 16px 20px;
  }
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-shrink: 0;
  margin-bottom: 12px;
  .top-tabs { flex: 1; min-width: 0; :deep(.el-tabs__header) { margin-bottom: 0; } }
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.table-wrap { flex: 1; min-height: 0; overflow: hidden; }
.filter-form { flex-shrink: 0; margin-bottom: 12px; :deep(.el-form-item) { margin-bottom: 10px; } }
.list-pagination { flex-shrink: 0; justify-content: flex-end; margin-top: 12px; }
</style>
