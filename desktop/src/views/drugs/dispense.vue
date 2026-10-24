<template>
  <div class="his-page">
    <div class="his-page-head">
      <div>
        <div class="his-page-title">药品发药</div>
        <div class="his-page-subtitle">处方收费后发药，自动扣减库存并生成发药记录</div>
      </div>
    </div>

    <el-card shadow="never">
      <el-tabs v-model="statusTab" @tab-change="onTabChange">
        <el-tab-pane label="待发药" name="paid" />
        <el-tab-pane label="已发药" name="dispensed" />
      </el-tabs>

      <el-table :data="tableData" border stripe v-loading="loading">
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

      <div class="dispense-tip">
        说明：发药后库存自动扣减；租户开启「药师审核」时，发药记录先生成为待审核，由药师在审核通过后完成发药。
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

defineOptions({ name: 'DrugDispense' })

const router = useRouter()
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
.dispense-tip {
  margin-top: 12px;
  color: #909399;
  font-size: 12px;
}
.list-pagination { justify-content: flex-end; margin-top: 12px; }
</style>
