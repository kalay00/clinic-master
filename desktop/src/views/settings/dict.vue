<template>
  <div class="dict-page">
    <div class="dict-header">
      <el-tabs v-model="activeCategory" class="dict-tabs" @tab-change="onCategoryChange">
        <el-tab-pane v-for="cat in menuData" :key="cat.key" :label="cat.label" :name="cat.key" />
      </el-tabs>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        <span>新增</span>
      </el-button>
    </div>

    <el-card class="dict-body-card" :body-style="{ padding: '20px' }">
      <div class="dict-body">
        <div class="left-panel">
          <div
            v-for="sub in currentCategory.children"
            :key="sub.key"
            class="menu-item"
            :class="{ active: activeSubType === sub.key }"
            @click="handleSelect(sub.key)"
          >
            {{ sub.label }}
          </div>
        </div>

        <div class="right-panel">
          <div class="card-header">
            <div class="search-box">
              <template v-if="isDrugCategory">
                <el-select v-model="categoryType" placeholder="处方类别" clearable style="width: 140px" @change="fetchList">
                  <el-option v-for="opt in categoryTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
                <el-input
                  v-model="keyword"
                  placeholder="分类名称"
                  clearable
                  class="search-input"
                  @keyup.enter="fetchList"
                  @clear="fetchList"
                />
              </template>
              <template v-else>
                <el-input
                  v-model="keyword"
                  placeholder="模板内容"
                  clearable
                  class="search-input"
                  @keyup.enter="fetchList"
                  @clear="fetchList"
                />
              </template>
              <el-button type="primary" @click="fetchList">
                <el-icon><Search /></el-icon>
              </el-button>
            </div>
          </div>

          <el-table :data="tableData" border stripe v-loading="loading" class="dict-table">
            <el-table-column type="index" label="序号" width="80" align="center" />
            <template v-if="isDrugCategory">
              <el-table-column prop="category_type" label="处方分类" width="140" align="center">
                <template #default="{ row }">
                  {{ categoryTypeText[row.category_type] || row.category_type || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="name" label="分类名称" min-width="240" />
            </template>
            <template v-else>
              <el-table-column prop="content" :label="`${currentShortLabel}内容`" min-width="240" />
            </template>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column prop="creator" label="创建人" width="120" />
            <el-table-column label="操作" width="140" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
                <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              layout="total, prev, pager, next, jumper"
              @current-change="fetchList"
            />
          </div>
        </div>
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="`${form.id ? '编辑' : '新增'}${currentSubLabel}`"
      width="520px"
    >
      <el-form :model="form" label-width="90px" ref="formRef">
        <el-form-item :label="isDrugCategory ? '分类名称' : `${currentSubLabel}内容`" required>
          <el-input v-model="form.content" :placeholder="`请输入${isDrugCategory ? '分类名称' : currentSubLabel + '内容'}`" />
        </el-form-item>
        <el-form-item v-if="isDrugCategory" label="处方分类" required>
          <el-select v-model="form.category_type" placeholder="请选择处方分类" style="width: 100%">
            <el-option v-for="opt in categoryTypeOptions.filter(o => o.value !== 'all')" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="编码">
          <el-input v-model="form.code" placeholder="选填" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
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
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getDictionaryList, createDictionary, updateDictionary, deleteDictionary } from '@/api/dictionary'
import { getDrugCategories, createDrugCategory, updateDrugCategory, deleteDrugCategory } from '@/api/pharmacy'
import { fetchAllPages } from '@/utils/paging'
import { useDrugCategoryConfig } from '@/composables/useDrugCategoryConfig'

const { westernEnabled, chineseEnabled, load: loadDrugCategoryConfig } = useDrugCategoryConfig()

// 一级分类 → 二级子类型 菜单配置
const menuData = [
  { key: 'medical_record', label: '病历信息', children: [
    { key: 'diagnosis', label: '诊断信息', shortLabel: '诊断' },
    { key: 'doctor_advice', label: '医嘱信息', shortLabel: '医嘱' },
    { key: 'chief_complaint', label: '主诉信息', shortLabel: '主诉' },
    { key: 'present_illness', label: '现病史', shortLabel: '现病史' },
    { key: 'past_history', label: '既往史', shortLabel: '既往史' },
    { key: 'allergy_history', label: '过敏史', shortLabel: '过敏史' },
    { key: 'personal_history', label: '个人史', shortLabel: '个人史' },
    { key: 'auxiliary_exam', label: '辅助检查', shortLabel: '辅助检查' },
    { key: 'treatment_opinion', label: '治疗意见', shortLabel: '治疗意见' },
  ]},
  { key: 'drug', label: '药品信息', children: [
    { key: 'drug_category', label: '药品分类', shortLabel: '药品分类', kind: 'drug_category' },
    { key: 'drug_usage', label: '药品用法', shortLabel: '药品用法' },
    { key: 'drug_form', label: '药品剂型', shortLabel: '药品剂型' },
    { key: 'fee_item', label: '发票项目', shortLabel: '发票项目' },
    { key: 'manufacturer', label: '生产厂家', shortLabel: '生产厂家' },
    { key: 'package_unit', label: '包装单位', shortLabel: '包装单位' },
    { key: 'stock_in_type', label: '入库类型', shortLabel: '入库类型' },
    { key: 'stock_out_type', label: '出库类型', shortLabel: '出库类型' },
  ]},
  { key: 'inspection', label: '检查项目', children: [
    { key: 'inspection_item', label: '检查项目', shortLabel: '检查项目' },
    { key: 'inspection_part', label: '检查部位', shortLabel: '检查部位' },
  ]},
  { key: 'patient', label: '患者信息', children: [
    { key: 'patient_source', label: '患者来源', shortLabel: '患者来源' },
    { key: 'patient_type', label: '患者类型', shortLabel: '患者类型' },
  ]},
]

const activeCategory = ref('medical_record')
const activeSubType = ref('diagnosis')
const currentCategory = computed(() => menuData.find(cat => cat.key === activeCategory.value) || menuData[0])
const currentSub = computed(() => currentCategory.value.children.find(s => s.key === activeSubType.value))
const currentSubLabel = computed(() => currentSub.value?.label || '')
const currentShortLabel = computed(() => currentSub.value?.shortLabel || currentSubLabel.value)
const isDrugCategory = computed(() => currentSub.value?.kind === 'drug_category')

const baseCategoryTypeOptions = [
  { label: '西/成药处方', value: 'western' },
  { label: '中成药处方', value: 'chinese_patent' },
  { label: '中药处方', value: 'herb' },
]
const categoryTypeText = { western: '西/成药处方', chinese_patent: '中成药处方', herb: '中药处方', all: '全部' }

// 继承「基础设置 - 药品设置」的西药/中药开关
const allowedCategoryTypes = computed(() => {
  const set = new Set()
  if (westernEnabled.value) set.add('western')
  if (chineseEnabled.value) {
    set.add('chinese_patent')
    set.add('herb')
  }
  return set
})
const categoryTypeOptions = computed(() => [
  { label: '全部', value: 'all' },
  ...baseCategoryTypeOptions.filter(o => allowedCategoryTypes.value.has(o.value)),
])

function onCategoryChange(category) {
  activeCategory.value = category
  activeSubType.value = currentCategory.value.children[0]?.key || ''
  page.value = 1
  keyword.value = ''
  categoryType.value = 'all'
  fetchList()
}

const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const categoryType = ref('all')
const loading = ref(false)

async function fetchList() {
  loading.value = true
  try {
    let res
    if (isDrugCategory.value) {
      // 需按开关剔除未启用的处方类别，故全量拉取后在前端过滤并分页
      const all = await fetchAllPages(p => getDrugCategories({
        keyword: keyword.value || undefined,
        category_type: categoryType.value === 'all' ? undefined : categoryType.value,
        ...p,
      }))
      const filtered = all.filter(i => !i.category_type || allowedCategoryTypes.value.has(i.category_type))
      total.value = filtered.length
      const start = (page.value - 1) * pageSize.value
      tableData.value = filtered.slice(start, start + pageSize.value)
      return
    } else {
      res = await getDictionaryList({
        category: activeCategory.value,
        sub_type: activeSubType.value,
        keyword: keyword.value || undefined,
        page: page.value,
        page_size: pageSize.value,
      })
    }
    // 后端 SuccessResponse(data=PageResult) → 拦截器返回 res.data = { items, total, ... }
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    // 接口错误由全局拦截处理
  } finally {
    loading.value = false
  }
}

function handleSelect(index) {
  // el-menu-item index 为 sub_type，需要回溯父级 category
  for (const cat of menuData) {
    if (cat.children.some(s => s.key === index)) {
      activeCategory.value = cat.key
      break
    }
  }
  activeSubType.value = index
  page.value = 1
  keyword.value = ''
  categoryType.value = 'all'
  fetchList()
}

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  content: '',
  code: '',
  category_type: '',
  sort: 0,
  status: 'active',
  remark: '',
})

// 默认取第一个未被开关关闭的处方类别
const defaultCategoryType = () => categoryTypeOptions.value.find(o => o.value !== 'all')?.value || ''

function openDialog(row) {
  if (row) {
    form.id = row.id
    form.content = isDrugCategory.value ? row.name : row.content
    form.code = row.code || ''
    form.category_type = row.category_type || defaultCategoryType()
    form.sort = row.sort || 0
    form.status = row.status || 'active'
    form.remark = row.remark || ''
  } else {
    form.id = null
    form.content = ''
    form.code = ''
    form.category_type = defaultCategoryType()
    form.sort = 0
    form.status = 'active'
    form.remark = ''
  }
  dialogVisible.value = true
}

async function submit() {
  if (!form.content) {
    ElMessage.warning(isDrugCategory.value ? '请输入分类名称' : '请输入内容')
    return
  }
  submitting.value = true
  try {
    if (isDrugCategory.value) {
      const payload = {
        name: form.content,
        category_type: form.category_type,
        sort: form.sort,
        status: form.status,
        remark: form.remark || undefined,
      }
      if (form.id) {
        await updateDrugCategory(form.id, payload)
      } else {
        await createDrugCategory(payload)
      }
    } else {
      const payload = {
        category: activeCategory.value,
        sub_type: activeSubType.value,
        content: form.content,
        code: form.code || undefined,
        sort: form.sort,
        status: form.status,
        remark: form.remark || undefined,
      }
      if (form.id) {
        await updateDictionary(form.id, payload)
      } else {
        await createDictionary(payload)
      }
    }
    ElMessage.success(form.id ? '更新成功' : '新增成功')
    dialogVisible.value = false
    fetchList()
  } catch (e) {
    // ignore
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除该${currentSubLabel.value}？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    if (isDrugCategory.value) {
      await deleteDrugCategory([row.id])
    } else {
      await deleteDictionary(row.id)
    }
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    // ignore
  }
}

onMounted(async () => {
  await loadDrugCategoryConfig()
  // 当前筛选的处方类别已被关闭时，回退到「全部」
  if (categoryType.value !== 'all' && !allowedCategoryTypes.value.has(categoryType.value)) {
    categoryType.value = 'all'
  }
  fetchList()
})
</script>

<style scoped lang="scss">
.dict-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  height: 100%;
  box-sizing: border-box;
}
.dict-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  .dict-tabs {
    flex: 1;
    :deep(.el-tabs__header) {
      margin-bottom: 0;
      border-bottom: none;
    }
    :deep(.el-tabs__nav-wrap::after) {
      display: none;
    }
    :deep(.el-tabs__item) {
      height: 40px;
      line-height: 40px;
      padding: 0 24px;
      font-size: 14px;
      color: #606266;
      border-radius: 4px 4px 0 0;
      transition: all 0.2s;
      &.is-active {
        color: #fff;
        background: #5b7cff;
      }
      &:hover {
        color: #5b7cff;
      }
      &.is-active:hover {
        color: #fff;
      }
    }
    :deep(.el-tabs__active-bar) {
      display: none;
    }
  }
}
.dict-body-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #ebeef5;
  :deep(.el-card__body) {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
}
.dict-body {
  display: flex;
  gap: 20px;
  flex: 1;
  overflow: hidden;
}
.left-panel {
  width: 180px;
  flex-shrink: 0;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  .menu-item {
    height: 44px;
    line-height: 44px;
    padding: 0 16px;
    background: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    color: #606266;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    &:hover {
      border-color: #5b7cff;
      color: #5b7cff;
    }
    &.active {
      background: #5b7cff;
      border-color: #5b7cff;
      color: #fff;
    }
  }
}
.right-panel {
  flex: 1;
  overflow: auto;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 16px;
  .search-box {
    display: flex;
    align-items: center;
    gap: 8px;
    .search-input {
      width: 260px;
    }
  }
}
.dict-table {
  width: 100%;
  :deep(.el-table__header-wrapper th) {
    background: #e8eeff;
    color: #303133;
    font-weight: 600;
  }
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
