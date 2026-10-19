<template>
  <el-dialog
    v-model="visible"
    title="调用病历模板"
    width="780px"
    append-to-body
    @open="reset"
  >
    <el-form :inline="true" class="filter-bar">
      <el-form-item label="模板名称">
        <el-input v-model="filters.name" placeholder="请输入" clearable />
      </el-form-item>
      <el-form-item label="模板分类">
        <el-select v-model="filters.category" placeholder="请选择" clearable style="width: 160px">
          <el-option label="门诊病历" value="outpatient" />
          <el-option label="住院病历" value="inpatient" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
      </el-form-item>
    </el-form>

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
            <el-descriptions :column="2" border size="small" class="detail-desc">
              <el-descriptions-item label="诊断">{{ row.diagnosis }}</el-descriptions-item>
              <el-descriptions-item label="主诉">{{ row.chiefComplaint }}</el-descriptions-item>
              <el-descriptions-item label="现病史">{{ row.presentIllness }}</el-descriptions-item>
              <el-descriptions-item label="既往史">{{ row.pastHistory }}</el-descriptions-item>
              <el-descriptions-item label="过敏史">{{ row.allergyHistory }}</el-descriptions-item>
              <el-descriptions-item label="个人史">{{ row.personalHistory }}</el-descriptions-item>
              <el-descriptions-item label="家族史">{{ row.familyHistory }}</el-descriptions-item>
              <el-descriptions-item label="辅助检查">{{ row.auxiliaryExam }}</el-descriptions-item>
              <el-descriptions-item label="治疗意见">{{ row.treatmentOpinion }}</el-descriptions-item>
              <el-descriptions-item label="医嘱">{{ row.advice }}</el-descriptions-item>
            </el-descriptions>
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
    id: 1, name: '高血压随访模板', categoryName: '门诊病历', creator: '王阳明', createTime: '2026-08-01 10:20',
    diagnosis: '原发性高血压', chiefComplaint: '头晕1周', presentIllness: '患者1周前无明显诱因出现头晕',
    pastHistory: '高血压病史3年', allergyHistory: '无', personalHistory: '吸烟史',
    familyHistory: '父亲高血压', auxiliaryExam: '血压160/100mmHg', treatmentOpinion: '降压治疗', advice: '低盐饮食',
  },
  {
    id: 2, name: '糖尿病复诊模板', categoryName: '门诊病历', creator: '张仲景', createTime: '2026-07-30 15:40',
    diagnosis: '2型糖尿病', chiefComplaint: '口干多饮', presentIllness: '患者血糖控制欠佳',
    pastHistory: '糖尿病5年', allergyHistory: '无', personalHistory: '无特殊',
    familyHistory: '无', auxiliaryExam: '空腹血糖9.2', treatmentOpinion: '调整降糖方案', advice: '控制饮食',
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
.detail-desc {
  margin-top: 4px;
}
</style>
