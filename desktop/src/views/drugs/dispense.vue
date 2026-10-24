<template>
  <div class="dispense-page">
    <el-card class="page-card" shadow="never">
      <div class="card-header">
        <el-tabs v-model="statusTab" @tab-change="onTabChange">
          <el-tab-pane label="待发药" name="paid" />
          <el-tab-pane label="已发药" name="dispensed" />
        </el-tabs>
      </div>

      <div class="page-body">
        <div class="table-wrap" ref="wrapRef">
          <el-table :data="tableData" border stripe v-loading="loading" ref="tableRef" :height="tableHeight">
        <el-table-column type="index" label="序号" width="55" />
        <el-table-column prop="prescription_no" label="处方号" min-width="150" />
        <el-table-column label="患者" min-width="140">
          <template #default="{ row }">{{ row.patient_name || '-' }}<span v-if="row.patient_no" style="color:#909399">（{{ row.patient_no }}）</span></template>
        </el-table-column>
        <el-table-column prop="doctor_name" label="开方医生" width="110" />
        <el-table-column label="药品数量" width="100">
          <template #default="{ row }">{{ Array.isArray(row.items) ? row.items.length : 0 }} 种</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额（元）" width="110">
          <template #default="{ row }">{{ fmt(row.total_amount) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="开方时间" min-width="160" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'paid'"
              type="primary"
              link
              :loading="actingId === row.id"
              @click="onDispense(row)"
            >发药</el-button>
            <el-button link type="primary" @click="onDetail(row)">详情</el-button>
            <span v-if="row.status !== 'paid'" style="color:#67c23a">已发药</span>
          </template>
        </el-table-column>
      </el-table>
        </div>

        <div class="dispense-tip">
          说明：发药后库存自动扣减；租户开启「药师审核」时，发药记录先生成为待审核，由药师在审核通过后完成发药。
        </div>
      </div>

      <el-pagination
        class="list-pagination"
        v-model:current-page="query.page"
        v-model:page-size="query.pageSize"
        layout="total, prev, pager, next, jumper"
        :total="total"
        @current-change="fetchList"
        @size-change="onSizeChange"
      />
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPrescriptions } from '@/api/treatment'
import { dispensePrescription } from '@/api/pharmacy'
import { useTableHeight } from '@/composables/useTableHeight'

defineOptions({ name: 'DrugDispense' })

const router = useRouter()
const { wrapRef, tableRef, tableHeight, refresh } = useTableHeight()
const loading = ref(false)
const actingId = ref('')
const statusTab = ref('paid')
const tableData = ref([])
const total = ref(0)
const query = reactive({ page: 1, pageSize: 10 })

const fmt = (v) => v == null ? '0.00' : Number(v).toFixed(2)

async function fetchList() {
  loading.value = true
  try {
    const res = await getPrescriptions({
      page: query.page,
      page_size: query.pageSize,
      status: statusTab.value,
    })
    tableData.value = res.items || []
    total.value = res.pagination?.total ?? res.total ?? 0
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
    refresh()
  }
}

const onTabChange = () => { query.page = 1; fetchList() }
const onSizeChange = () => { query.page = 1; fetchList() }

const onDetail = (row) => router.push(`/drugs/dispense/detail/${row.id}`)

const onDispense = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认对处方 ${row.prescription_no || ''} 发药？发药后库存将自动扣减。`,
      '发药确认',
      { type: 'warning' }
    )
  } catch {
    return // 用户取消
  }
  actingId.value = row.id
  try {
    // items 传空数组：后端按处方明细推导发药药品并扣减库存
    await dispensePrescription(row.id, [])
    ElMessage.success('发药成功')
    fetchList()
  } catch (e) {
    ElMessage.error(e?.message || '发药失败')
  } finally {
    actingId.value = ''
  }
}

onMounted(fetchList)
</script>

<style lang="scss" scoped>
/* 固定高度布局：页面不滚动，页签/分页固定，仅列表内部滚动 */
.dispense-page { height: 100%; box-sizing: border-box; padding: 16px; overflow: hidden; }
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
  flex-shrink: 0;
  margin-bottom: 12px;
  :deep(.el-tabs__header) { margin-bottom: 0; }
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.table-wrap { flex: 1; min-height: 0; overflow: hidden; }
.dispense-tip {
  margin-top: 12px;
  color: #909399;
  font-size: 12px;
  flex-shrink: 0;
}
.list-pagination { flex-shrink: 0; justify-content: flex-end; margin-top: 12px; }
</style>
