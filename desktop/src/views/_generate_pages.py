import os, re

VIEWS_DIR = '/Users/damimi/Downloads/开发/his/outpatient-management-system/desktop/src/views'
ROUTES_FILE = '/Users/damimi/Downloads/开发/his/outpatient-management-system/desktop/src/router/routes.js'

routes_text = open(ROUTES_FILE, encoding='utf-8').read()
# 提取: path 'xxx', name 'xxx', component import('@/views/xxx'), meta { title: 'xxx', hidden? }
route_blocks = re.findall(
    r"\{\s*path:\s*'([^']+)'\s*,\s*name:\s*'([^']+)'\s*,\s*component:\s*\(\)\s*=>\s*import\('@/views/([^']+)'\)\s*,\s*meta:\s*\{([^}]+)\}",
    routes_text, re.S
)
routes = []
for path, name, view, meta_text in route_blocks:
    tm = re.search(r"title:\s*'([^']+)'", meta_text)
    routes.append({'path':path, 'name':name, 'view':view, 'title':(tm.group(1) if tm else name),
                   'hidden': 'hidden: true' in meta_text})

# ========== 工具函数 ==========
def page_type(title):
    t = title
    if '工作台' in t: return 'workbench'
    if '概况' in t: return 'overview'
    if t in ('新开就诊','西药处方','中药处方','检查项目','病历','收费') or ('处方' in t and '模板' not in t): return 'consultation'
    if '详情' in t or '查看' in t: return 'detail'
    if any(k in t for k in ('新增','编辑','设置','维护','申请','找回')): return 'form'
    return 'list'

def infer_columns(title):
    t = title
    if '患者' in t and any(k in t for k in ('管理','列表')): return [('序号',60),('患者编码',120),('患者姓名',100),('性别',80),('年龄',80),('手机号码',140),('会员等级',100),('创建时间',160),('操作人员',120),('操作',200)]
    if '挂号' in t: return [('挂号单号',160),('患者姓名',100),('性别',80),('年龄',80),('科室',100),('医生',100),('挂号费',100),('就诊状态',100),('创建时间',160),('操作',180)]
    if '药品信息维护' in t: return [('序号',60),('编码',100),('药品名称',180),('规格',120),('收费类别',100),('采购价',100),('售药价',100),('生产厂家',160),('状态',80),('创建时间',160),('操作',180)]
    if '入库' in t and '管理' in t: return [('入库单号',160),('供应商',140),('入库数量',100),('入库金额',120),('状态',100),('创建时间',160),('操作',180)]
    if '出库' in t and '管理' in t: return [('出库单号',160),('领用方',140),('出库数量',100),('出库金额',120),('状态',100),('创建时间',160),('操作',180)]
    if '库存管理' in t: return [('药品编码',120),('药品名称',180),('规格',120),('批号',140),('库存数量',100),('锁定数量',100),('有效期',120),('操作',140)]
    if '库存盘点' in t: return [('盘点单号',160),('盘点人',100),('盘点状态',100),('盘点时间',160),('操作',160)]
    if '药品调价' in t: return [('药品编码',120),('药品名称',180),('原售价',100),('新售价',100),('生效日期',120),('状态',100),('操作',160)]
    if '会员列表' in t: return [('序号',60),('卡号',140),('会员类型',100),('会员等级',100),('会员姓名',100),('手机号码',140),('储值余额',100),('累计储值',100),('积分',80),('开卡时间',160),('到期时间',160),('会员状态',100),('操作',220)]
    if '储值' in t: return [('序号',60),('会员姓名',100),('卡号',140),('类型',100),('金额',120),('赠送金额',120),('时间',160),('操作',140)]
    if '积分管理' in t: return [('序号',60),('会员姓名',100),('卡号',140),('变动积分',100),('剩余积分',120),('变动类型',120),('时间',160),('操作',140)]
    if '收费统计' in t: return [('日期',120),('收费笔数',100),('收费金额',140),('退费金额',140),('实收金额',140),('操作',120)]
    if '患者统计' in t: return [('日期',120),('新增患者',100),('复诊患者',100),('就诊人次',100),('流失患者',100),('操作',120)]
    if '检查项目统计' in t: return [('项目名称',180),('数量',100),('金额',120),('占比',100),('操作',120)]
    if '药品统计' in t: return [('药品名称',180),('销量',100),('金额',120),('占比',100),('操作',120)]
    if '已收费' in t: return [('订单号',180),('患者姓名',100),('应收金额',120),('实收金额',120),('收费时间',160),('收费员',100),('操作',160)]
    if '退费' in t or '已退费' in t: return [('订单号',180),('患者姓名',100),('退费金额',120),('退费原因',160),('退费时间',160),('操作',160)]
    if '员工' in t: return [('序号',60),('姓名',100),('工号',100),('岗位',120),('角色',120),('手机号',140),('状态',100),('操作',160)]
    if '供应商' in t: return [('序号',60),('供应商名称',180),('联系人',120),('联系电话',140),('状态',100),('操作',160)]
    if '操作日志' in t: return [('序号',60),('操作人员',120),('操作模块',120),('操作内容',200),('IP地址',140),('操作时间',180),('操作',120)]
    return [('序号',60),('名称',180),('状态',100),('创建时间',160),('操作',180)]

def infer_filters(title):
    if '患者' in title: return [("会员类型","select",["全部","普通会员","VIP会员"]),("创建时间","daterange"),("关键词","input","患者姓名/手机号/会员卡号")]
    if '挂号' in title: return [("就诊状态","select",["全部","待就诊","就诊中","已结束"]),("创建时间","daterange"),("关键词","input","患者姓名/挂号单号")]
    if '药品信息维护' in title: return [("处方类别","select",["全部","西/成药","中药"]),("药品状态","select",["全部","启用","停用"]),("创建时间","daterange"),("关键词","input","药品名称/编码/生产厂家")]
    if '入库' in title: return [("状态","select",["全部","待审核","已通过","已驳回"]),("时间","daterange"),("关键词","input","单号/供应商")]
    if '出库' in title: return [("状态","select",["全部","待审核","已通过","已驳回"]),("时间","daterange"),("关键词","input","单号/领用方")]
    if '库存管理' in title: return [("药品分类","select",["全部","西/成药","中药"]),("关键词","input","药品名称/编码")]
    if '库存盘点' in title: return [("状态","select",["全部","盘点中","已完成"]),("时间","daterange"),("关键词","input","单号")]
    if '药品调价' in title: return [("状态","select",["全部","待生效","已生效","已过期"]),("时间","daterange"),("关键词","input","药品名称/编码")]
    if '会员列表' in title: return [("会员等级","select",["全部","VIP1","VIP2","VIP3"]),("创建时间","daterange"),("关键词","input","患者姓名/手机号/会员卡号")]
    if '储值' in title: return [("类型","select",["全部","充值","退款"]),("时间","daterange"),("关键词","input","会员姓名/卡号")]
    if '积分管理' in title: return [("变动类型","select",["全部","获得","抵扣"]),("时间","daterange"),("关键词","input","会员姓名/卡号")]
    if '统计' in title: return [("时间","daterange"),("关键词","input","项目名称")]
    if '已收费' in title or '退费' in title or '已退费' in title: return [("时间","daterange"),("关键词","input","订单号/患者姓名")]
    if '员工' in title: return [("状态","select",["全部","在职","离职"]),("关键词","input","姓名/工号/手机号")]
    if '供应商' in title: return [("状态","select",["全部","启用","停用"]),("关键词","input","供应商名称")]
    if '操作日志' in title: return [("时间","daterange"),("关键词","input","操作人/操作内容")]
    return [("关键词","input","请输入关键词")]

FIELD_MAP = {'会员类型':'memberType','创建时间':'createTime','关键词':'keyword','就诊状态':'visitStatus','处方类别':'category','药品状态':'drugStatus','状态':'status','时间':'dateRange','药品分类':'drugCategory','会员等级':'memberLevel','变动类型':'changeType','类型':'type'}

def fkey(label): return FIELD_MAP.get(label, 'keyword')

def render_col(col): return f'<el-table-column prop="{col[0]}" label="{col[0]}" min-width="{col[1]}" align="center" show-overflow-tooltip />'

def render_filters(filters):
    lines = []
    for f in filters:
        label, ftype = f[0], f[1]
        if ftype == 'input':
            lines.append(f'        <div class="filter-item">\n          <label class="filter-label">{label}</label>\n          <el-input v-model="searchForm.keyword" placeholder="{f[2]}" clearable style="width:220px" />\n        </div>')
        elif ftype == 'select':
            opts = '\n'.join(f'              <el-option label="{o}" value="{o}" />' for o in f[2])
            lines.append(f'        <div class="filter-item">\n          <label class="filter-label">{label}</label>\n          <el-select v-model="searchForm.{fkey(label)}" placeholder="全部" clearable style="width:140px">\n{opts}\n          </el-select>\n        </div>')
        elif ftype == 'daterange':
            lines.append(f'        <div class="filter-item">\n          <label class="filter-label">{label}</label>\n          <el-date-picker v-model="searchForm.dateRange" type="daterange" range-separator="-" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width:240px" />\n        </div>')
    return '\n'.join(lines)

def render_actions(title, ptype):
    if ptype == 'form': return ''
    if '患者' in title: return '        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon> 新增患者</el-button>\n        <el-button @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>'
    if '药品信息维护' in title: return '        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon> 新增药品</el-button>\n        <el-button @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>'
    if '会员列表' in title: return '        <el-button @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>'
    return '        <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon> 新增</el-button>\n        <el-button @click="handleExport"><el-icon><Download /></el-icon> 导出</el-button>'

def build_search_reset(filters):
    sf = []
    reset = []
    for f in filters:
        fn = fkey(f[0])
        if f[1] == 'daterange':
            sf.append('  dateRange: []')
            reset.append('  searchForm.dateRange = []')
        else:
            sf.append(f'  {fn}: \'\'')
            reset.append(f'  searchForm.{fn} = \'\'')
    return ',\n'.join(sf) if sf else "  keyword: ''", '\n'.join(reset) if reset else "  searchForm.keyword = ''"


# ========== 页面模板（使用 $VAR 占位，用 replace 替换，不破坏 {{ }}） ==========
LIST_TPL = r'''<template>
  <div class="page-wrapper">
    <div class="page-head">
      <div>
        <h2 class="page-title">{{ title }}</h2>
        <p class="page-subtitle">$SUBTITLE</p>
      </div>
      <div class="page-actions">
$ACTIONS
      </div>
    </div>

    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
$FILTERS
        <div class="filter-item filter-btns">
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon> 查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>
      </div>
    </el-card>

    <el-card shadow="never" class="table-card">
      <el-table :data="tableData" border stripe v-loading="loading" empty-text="暂无数据" style="width:100%">
$COLUMNS
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small">编辑</el-button>
            <el-button type="success" link size="small">查看</el-button>
            <el-button type="danger" link size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50,100]" layout="total, sizes, prev, pager, next, jumper" background />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title || '$TITLE')
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableData = ref([])
const searchForm = reactive({
$SEARCH_FIELDS
})

onMounted(() => {
  handleSearch()
})

function handleSearch() {}
function handleReset() {
$RESET
}
function handleAdd() {}
function handleExport() {}
</script>

<style lang="scss" scoped>
.page-wrapper { padding: 16px; }
.page-head { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; }
.page-title { font-size:18px; font-weight:700; color:#333; padding-left:12px; border-left:4px solid #5b7cff; margin:0; }
.page-subtitle { font-size:13px; color:#909399; margin-top:6px; padding-left:16px; }
.page-actions { display:flex; gap:10px; }
.filter-card { margin-bottom:16px; border-radius:12px; }
.filter-bar { display:flex; flex-wrap:wrap; align-items:flex-end; gap:16px; }
.filter-item { display:flex; flex-direction:column; gap:6px; }
.filter-label { font-size:13px; color:#606266; font-weight:500; }
.filter-btns { flex-direction:row; align-items:flex-end; }
.table-card { border-radius:12px; }
.pagination-container { margin-top:16px; display:flex; justify-content:flex-end; }
</style>
'''

FORM_TPL = r'''<template>
  <div class="page-wrapper">
    <div class="page-head">
      <div>
        <h2 class="page-title">{{ title }}</h2>
        <p class="page-subtitle">$SUBTITLE</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="handleSave"><el-icon><Check /></el-icon> 保存</el-button>
        <el-button @click="handleBack"><el-icon><Back /></el-icon> 返回</el-button>
      </div>
    </div>

$SECTIONS
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const title = computed(() => route.meta.title || '$TITLE')

const form = reactive({
$FORM_DEFAULTS
})
const familyData = ref([])
const detailData = ref([])

function handleSave() {}
function handleBack() { router.back() }
</script>

<style lang="scss" scoped>
.page-wrapper { padding: 16px; }
.page-head { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; }
.page-title { font-size:18px; font-weight:700; color:#333; padding-left:12px; border-left:4px solid #5b7cff; margin:0; }
.page-subtitle { font-size:13px; color:#909399; margin-top:6px; padding-left:16px; }
.page-actions { display:flex; gap:10px; }
.section-block { background:#fff; border-radius:12px; padding:20px; margin-bottom:16px; box-shadow:0 2px 12px rgba(0,0,0,0.04); }
.section-title { font-size:16px; font-weight:700; color:#5b7cff; margin-bottom:20px; padding-left:12px; border-left:4px solid #5b7cff; }
.form-grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:20px 24px; }
:deep(.el-form-item) { margin-bottom:8px; }
:deep(.el-form-item__label) { color:#606266; font-weight:500; }
.required { color:#ff6b6b; }
@media (max-width: 1400px) { .form-grid { grid-template-columns:repeat(3, 1fr); } }
@media (max-width: 992px) { .form-grid { grid-template-columns:repeat(2, 1fr); } }
</style>
'''

WORKBENCH_TPL = r'''<template>
  <div class="page-wrapper">
    <div class="page-head">
      <div>
        <h2 class="page-title">{{ title }}</h2>
        <p class="page-subtitle">今日待接诊患者，点击卡片开始接诊</p>
      </div>
      <div class="page-actions">
        <el-button type="success" @click="handleNewVisit"><el-icon><Plus /></el-icon> 新开就诊</el-button>
      </div>
    </div>

    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <div class="filter-item"><label class="filter-label">创建时间</label><el-date-picker v-model="searchForm.dateRange" type="daterange" range-separator="-" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width:240px" /></div>
        <div class="filter-item"><label class="filter-label">接诊状态</label><el-select v-model="searchForm.status" placeholder="全部" clearable style="width:140px"><el-option label="待接诊" value="pending" /><el-option label="接诊中" value="processing" /><el-option label="已完成" value="done" /></el-select></div>
        <div class="filter-item"><label class="filter-label">患者姓名</label><el-input v-model="searchForm.keyword" placeholder="请输入患者姓名" clearable style="width:200px" /></div>
        <div class="filter-item filter-btns"><el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon> 查询</el-button><el-button @click="handleReset">重置</el-button></div>
      </div>
    </el-card>

    <div class="patient-grid">
      <div class="patient-card" v-for="i in 8" :key="i">
        <div class="card-header">
          <el-avatar :size="44" class="patient-avatar"><el-icon><User /></el-icon></el-avatar>
          <div class="patient-info">
            <div class="name-row"><span class="name">患者姓名</span><el-tag size="small" type="warning" effect="dark">VIP</el-tag></div>
            <div class="meta">男 · 28岁</div>
          </div>
          <el-tag type="primary" effect="plain" size="small">待接诊</el-tag>
        </div>
        <div class="card-body">
          <div class="info-row"><span class="label">创建时间</span><span class="value">2026-08-03 09:30</span></div>
          <div class="info-row"><span class="label">科室</span><span class="value">内科</span></div>
          <div class="info-row"><span class="label">医生</span><span class="value">张医生</span></div>
          <div class="info-row"><span class="label">手机号</span><span class="value">138****1234</span></div>
        </div>
        <div class="card-footer">
          <el-button type="primary" size="small" round>接诊</el-button>
          <el-button size="small" round>查看患者信息</el-button>
        </div>
      </div>
    </div>
    <div class="pagination-container">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[12,24,48]" layout="total, prev, pager, next" background />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const title = computed(() => route.meta.title || '工作台')
const page = ref(1)
const pageSize = ref(12)
const total = ref(48)
const searchForm = reactive({ dateRange: [], status: '', keyword: '' })
function handleSearch() {}
function handleReset() { searchForm.dateRange=[]; searchForm.status=''; searchForm.keyword=''; }
function handleNewVisit() { router.push('/consultation') }
</script>

<style lang="scss" scoped>
.page-wrapper { padding: 16px; }
.page-head { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; }
.page-title { font-size:18px; font-weight:700; color:#333; padding-left:12px; border-left:4px solid #5b7cff; margin:0; }
.page-subtitle { font-size:13px; color:#909399; margin-top:6px; padding-left:16px; }
.page-actions { display:flex; gap:10px; }
.filter-card { margin-bottom:16px; border-radius:12px; }
.filter-bar { display:flex; flex-wrap:wrap; align-items:flex-end; gap:16px; }
.filter-item { display:flex; flex-direction:column; gap:6px; }
.filter-label { font-size:13px; color:#606266; font-weight:500; }
.filter-btns { flex-direction:row; align-items:flex-end; }
.patient-grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; margin-bottom:16px; }
@media (max-width:1400px) { .patient-grid { grid-template-columns:repeat(3, 1fr); } }
@media (max-width:992px) { .patient-grid { grid-template-columns:repeat(2, 1fr); } }
.patient-card { background:#fff; border-radius:12px; padding:16px; box-shadow:0 2px 12px rgba(0,0,0,0.04); transition:transform .2s; }
.patient-card:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(91,124,255,0.12); }
.card-header { display:flex; align-items:center; gap:12px; margin-bottom:14px; }
.patient-avatar { background:linear-gradient(135deg,#5b7cff,#8aa4ff); color:#fff; }
.patient-info { flex:1; }
.name-row { display:flex; align-items:center; gap:8px; margin-bottom:4px; }
.name { font-size:16px; font-weight:600; color:#333; }
.meta { font-size:12px; color:#909399; }
.card-body { margin-bottom:14px; }
.info-row { display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px; }
.info-row .label { color:#909399; }
.info-row .value { color:#333; font-weight:500; }
.card-footer { display:flex; gap:8px; justify-content:flex-end; }
.pagination-container { display:flex; justify-content:flex-end; }
</style>
'''

OVERVIEW_TPL = r'''<template>
  <div class="page-wrapper">
    <div class="page-head">
      <div>
        <h2 class="page-title">{{ title }}</h2>
        <p class="page-subtitle">诊所今日经营概况</p>
      </div>
    </div>
    <div class="stat-row">
      <div class="stat-card" v-for="(item, idx) in stats" :key="idx">
        <div class="stat-icon" :style="{ background: item.color }"><el-icon :size="28" color="#fff"><component :is="item.icon" /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </div>
    </div>
    <div class="chart-row">
      <el-card shadow="never" class="chart-card"><div class="section-title">近7日收费趋势</div><div class="chart-placeholder">图表区域</div></el-card>
      <el-card shadow="never" class="chart-card"><div class="section-title">患者来源分布</div><div class="chart-placeholder">图表区域</div></el-card>
    </div>
    <el-card shadow="never" class="todo-card">
      <div class="section-title">待办事项</div>
      <el-table :data="todoList" border empty-text="暂无待办">
        <el-table-column prop="title" label="事项" min-width="200" />
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="status" label="状态" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const title = computed(() => route.meta.title || '概况')
const stats = ref([
  { label: '今日就诊', value: '32', icon: 'FirstAidKit', color: 'linear-gradient(135deg,#5b7cff,#8aa4ff)' },
  { label: '今日收费', value: '¥ 12,580', icon: 'Money', color: 'linear-gradient(135deg,#4cd1a4,#6fdebb)' },
  { label: '新增患者', value: '8', icon: 'User', color: 'linear-gradient(135deg,#ffb347,#ffc670)' },
  { label: '药品库存预警', value: '3', icon: 'Box', color: 'linear-gradient(135deg,#ff6b6b,#ff8e8e)' },
])
const todoList = ref([
  { title: '待审核入库单 2 条', time: '2026-08-03 10:00', status: '待处理' },
  { title: '库存预警药品 3 种', time: '2026-08-03 09:30', status: '待处理' },
])
</script>

<style lang="scss" scoped>
.page-wrapper { padding: 16px; }
.page-head { margin-bottom:16px; }
.page-title { font-size:18px; font-weight:700; color:#333; padding-left:12px; border-left:4px solid #5b7cff; margin:0; }
.page-subtitle { font-size:13px; color:#909399; margin-top:6px; padding-left:16px; }
.stat-row { display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; margin-bottom:16px; }
@media (max-width:1200px) { .stat-row { grid-template-columns:repeat(2, 1fr); } }
.stat-card { background:#fff; border-radius:12px; padding:20px; display:flex; align-items:center; gap:16px; box-shadow:0 2px 12px rgba(0,0,0,0.04); }
.stat-icon { width:56px; height:56px; border-radius:12px; display:flex; align-items:center; justify-content:center; }
.stat-value { font-size:24px; font-weight:700; color:#333; margin-bottom:4px; }
.stat-label { font-size:13px; color:#909399; }
.chart-row { display:grid; grid-template-columns:repeat(2, 1fr); gap:16px; margin-bottom:16px; }
@media (max-width:1200px) { .chart-row { grid-template-columns:1fr; } }
.chart-card { border-radius:12px; }
.chart-placeholder { height:260px; display:flex; align-items:center; justify-content:center; color:#c0c4cc; background:#f8f9fb; border-radius:8px; }
.section-title { font-size:16px; font-weight:700; color:#5b7cff; margin-bottom:16px; padding-left:12px; border-left:4px solid #5b7cff; }
.todo-card { border-radius:12px; }
</style>
'''

DETAIL_TPL = r'''<template>
  <div class="page-wrapper">
    <div class="page-head">
      <div><h2 class="page-title">{{ title }}</h2><p class="page-subtitle">$SUBTITLE</p></div>
      <div class="page-actions"><el-button @click="handleBack"><el-icon><Back /></el-icon> 返回</el-button></div>
    </div>
    <el-card shadow="never" class="detail-card">
      <div class="section-title">$TITLE</div>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="字段1">内容1</el-descriptions-item>
        <el-descriptions-item label="字段2">内容2</el-descriptions-item>
        <el-descriptions-item label="字段3">内容3</el-descriptions-item>
        <el-descriptions-item label="字段4">内容4</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const title = computed(() => route.meta.title || '$TITLE')
function handleBack() { router.back() }
</script>

<style lang="scss" scoped>
.page-wrapper { padding: 16px; }
.page-head { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; }
.page-title { font-size:18px; font-weight:700; color:#333; padding-left:12px; border-left:4px solid #5b7cff; margin:0; }
.page-subtitle { font-size:13px; color:#909399; margin-top:6px; padding-left:16px; }
.page-actions { display:flex; gap:10px; }
.detail-card { border-radius:12px; }
.section-title { font-size:16px; font-weight:700; color:#5b7cff; margin-bottom:16px; padding-left:12px; border-left:4px solid #5b7cff; }
</style>
'''

CONSULTATION_TPL = r'''<template>
  <div class="consultation-page">
    <div class="page-head"><div><h2 class="page-title">{{ title }}</h2><p class="page-subtitle">为患者开具处方、病历及检查项目</p></div></div>
    <div class="consultation-body">
      <div class="main-panel">
        <el-card shadow="never" class="section-card">
          <div class="section-title">患者信息</div>
          <el-form :model="patientForm" label-width="90px" class="form-grid">
            <el-form-item label="患者姓名"><el-input v-model="patientForm.name" placeholder="请输入或选择患者" /></el-form-item>
            <el-form-item label="病历号"><el-input v-model="patientForm.code" disabled /></el-form-item>
            <el-form-item label="年龄"><el-input v-model="patientForm.age" disabled /></el-form-item>
            <el-form-item label="出生日期"><el-date-picker v-model="patientForm.birth" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
            <el-form-item label="性别"><el-select v-model="patientForm.gender" style="width:100%"><el-option label="男" value="男" /><el-option label="女" value="女" /></el-select></el-form-item>
            <el-form-item label="手机号码"><el-input v-model="patientForm.phone" /></el-form-item>
            <el-form-item label="证件号码"><el-input v-model="patientForm.idCard" /></el-form-item>
            <el-form-item label="就诊类型"><el-select v-model="patientForm.visitType" style="width:100%"><el-option label="初诊" value="初诊" /><el-option label="复诊" value="复诊" /></el-select></el-form-item>
            <el-form-item label="地址" class="full-width"><el-input v-model="patientForm.address" /></el-form-item>
          </el-form>
        </el-card>
        <el-card shadow="never" class="section-card">
          <div class="section-title">病历</div>
          <el-form :model="recordForm" label-width="90px" class="form-grid">
            <el-form-item label="主诉"><el-input v-model="recordForm.chief" placeholder="请输入主诉" /></el-form-item>
            <el-form-item label="现病史"><el-input v-model="recordForm.present" placeholder="请输入现病史" /></el-form-item>
            <el-form-item label="诊断"><el-input v-model="recordForm.diagnosis" placeholder="请输入诊断" /></el-form-item>
            <el-form-item label="医嘱"><el-input v-model="recordForm.advice" placeholder="请输入医嘱" /></el-form-item>
          </el-form>
        </el-card>
        <el-card shadow="never" class="section-card">
          <div class="section-title">处方</div>
          <el-radio-group v-model="rxType" size="small" style="margin-bottom:12px">
            <el-radio-button label="western">西药处方</el-radio-button>
            <el-radio-button label="chinese">中药处方</el-radio-button>
            <el-radio-button label="inspect">检查项目</el-radio-button>
          </el-radio-group>
          <el-table :data="rxData" border empty-text="请从右侧添加药品">
            <el-table-column type="index" label="组号" width="60" align="center" />
            <el-table-column prop="name" label="药品名称" min-width="160" />
            <el-table-column prop="spec" label="规格" min-width="100" />
            <el-table-column prop="dose" label="单次用量" min-width="100" />
            <el-table-column prop="usage" label="用法" min-width="100" />
            <el-table-column prop="freq" label="频次" min-width="100" />
            <el-table-column prop="days" label="天数" width="80" />
            <el-table-column prop="total" label="总量" width="80" />
            <el-table-column prop="price" label="单价" width="100" />
            <el-table-column label="操作" width="80" align="center"><template #default><el-button type="danger" link>删除</el-button></template></el-table-column>
          </el-table>
        </el-card>
      </div>
      <div class="side-panel">
        <el-card shadow="never" class="drug-panel">
          <div class="panel-head">
            <span class="panel-title">药品选择</span>
            <el-input v-model="drugKeyword" placeholder="药品名称/拼音" size="small" style="width:160px"><template #suffix><el-icon><Search /></el-icon></template></el-input>
          </div>
          <div class="category-tabs">
            <span class="cat-item active">全部</span><span class="cat-item">西成药</span><span class="cat-item">中药</span><span class="cat-item">检查</span>
          </div>
          <div class="drug-list">
            <div class="drug-item" v-for="i in 8" :key="i">
              <div class="drug-name">复方氯化钠注射液</div><div class="drug-spec">6g*11袋/盒</div><div class="drug-price">¥ 4.00</div>
              <el-button type="primary" size="small" circle><el-icon><Plus /></el-icon></el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    <div class="bottom-bar">
      <div class="amount">合计：<span class="num">¥ 0.00</span></div>
      <div class="actions">
        <el-button type="default"><el-icon><DocumentCopy /></el-icon> 处方模板</el-button>
        <el-button type="default"><el-icon><Printer /></el-icon> 打印处方</el-button>
        <el-button type="default"><el-icon><Document /></el-icon> 存为模板</el-button>
        <el-button type="success"><el-icon><Check /></el-icon> 保存</el-button>
        <el-button type="warning"><el-icon><Money /></el-icon> 收费</el-button>
        <el-button type="danger"><el-icon><CircleClose /></el-icon> 结束就诊</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const title = computed(() => route.meta.title || '新开就诊')
const patientForm = reactive({ name:'', code:'', age:'', birth:'', gender:'', phone:'', idCard:'', visitType:'', address:'' })
const recordForm = reactive({ chief:'', present:'', diagnosis:'', advice:'' })
const rxType = ref('western')
const rxData = ref([])
const drugKeyword = ref('')
</script>

<style lang="scss" scoped>
.consultation-page { padding: 16px 16px 80px; }
.page-head { margin-bottom:16px; }
.page-title { font-size:18px; font-weight:700; color:#333; padding-left:12px; border-left:4px solid #5b7cff; margin:0; }
.page-subtitle { font-size:13px; color:#909399; margin-top:6px; padding-left:16px; }
.consultation-body { display:flex; gap:16px; }
.main-panel { flex:1; min-width:0; }
.side-panel { width:320px; flex-shrink:0; }
.section-card { border-radius:12px; margin-bottom:16px; }
.section-title { font-size:16px; font-weight:700; color:#5b7cff; margin-bottom:16px; padding-left:12px; border-left:4px solid #5b7cff; }
.form-grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; }
.form-grid .full-width { grid-column:1 / -1; }
:deep(.el-form-item) { margin-bottom:0; }
.drug-panel { border-radius:12px; height:calc(100vh - 220px); display:flex; flex-direction:column; }
.panel-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.panel-title { font-size:16px; font-weight:700; color:#333; }
.category-tabs { display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap; }
.cat-item { padding:4px 12px; border-radius:14px; font-size:13px; color:#606266; background:#f4f7ff; cursor:pointer; }
.cat-item.active { background:#5b7cff; color:#fff; }
.drug-list { flex:1; overflow:auto; }
.drug-item { display:flex; align-items:center; gap:8px; padding:10px; border-bottom:1px solid #f0f2f7; }
.drug-name { flex:1; font-size:13px; color:#333; }
.drug-spec { font-size:12px; color:#909399; width:90px; }
.drug-price { font-size:13px; color:#ff6b6b; font-weight:600; width:60px; }
.bottom-bar { position:fixed; bottom:0; left:220px; right:0; height:64px; background:#fff; border-top:1px solid #eef0f4; display:flex; align-items:center; justify-content:space-between; padding:0 24px; box-shadow:0 -2px 12px rgba(0,0,0,0.04); z-index:100; }
.amount { font-size:16px; color:#333; } .amount .num { color:#ff6b6b; font-size:22px; font-weight:700; }
.actions { display:flex; gap:10px; }
@media (max-width:1400px) { .form-grid { grid-template-columns:repeat(3, 1fr); } }
</style>
'''

# ========== 构建页面 ==========
def build_page(r):
    title = r['title']; ptype = page_type(title)
    if ptype == 'workbench': return WORKBENCH_TPL
    if ptype == 'overview': return OVERVIEW_TPL
    if ptype == 'consultation': return CONSULTATION_TPL
    if ptype == 'detail': return DETAIL_TPL.replace('$TITLE', title).replace('$SUBTITLE', '查看详细信息')
    if ptype == 'form':
        sections = infer_form_sections(title)
        fd = []; sec_html = []
        for sec_name, fields in sections:
            lines = []
            for f in fields:
                p = f[0].replace(' ','').replace('/',''); fd.append(f'  {p}: \'\'')
                rq = ' <span class="required">*</span>' if f[2] else ''
                if f[1] == 'input': lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-input v-model="form.{p}" placeholder="请输入{f[0]}" /></el-form-item>')
                elif f[1] == 'number': lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-input-number v-model="form.{p}" :min="0" controls-position="right" style="width:100%" /></el-form-item>')
                elif f[1] == 'textarea': lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-input v-model="form.{p}" type="textarea" :rows="3" placeholder="请输入{f[0]}" /></el-form-item>')
                elif f[1] == 'select':
                    opts = ''.join(f'<el-option label="{o}" value="{o}" />' for o in f[3]) if len(f)>3 else ''
                    lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-select v-model="form.{p}" placeholder="请选择{f[0]}" style="width:100%">{opts}</el-select></el-form-item>')
                elif f[1] == 'date': lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-date-picker v-model="form.{p}" type="date" placeholder="选择{f[0]}" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>')
                elif f[1] == 'datetime': lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-date-picker v-model="form.{p}" type="datetime" placeholder="选择{f[0]}" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" /></el-form-item>')
                elif f[1] == 'switch': lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-switch v-model="form.{p}" active-text="启用" inactive-text="停用" /></el-form-item>')
                elif f[1] == 'password': lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-input v-model="form.{p}" type="password" show-password placeholder="请输入{f[0]}" /></el-form-item>')
                elif f[1] == 'upload': lines.append(f'      <el-form-item label="{f[0]}{rq}" prop="{p}"><el-upload :show-file-list="false"><el-icon><Plus /></el-icon></el-upload></el-form-item>')
            field_html = '\n'.join(lines)
            table_html = ''
            if not fields and sec_name == '关联家庭成员':
                table_html = '      <el-table :data="familyData" border style="margin-top:12px"><el-table-column type="index" label="序号" width="60" align="center" /><el-table-column prop="relation" label="家庭关系" min-width="100" /><el-table-column prop="name" label="姓名" min-width="100" /><el-table-column prop="gender" label="性别" min-width="80" /><el-table-column prop="age" label="年龄" min-width="80" /><el-table-column prop="birth" label="出生日期" min-width="120" /><el-table-column prop="phone" label="手机号码" min-width="140" /><el-table-column label="操作" width="180" align="center"><template #default><el-button type="primary" link>查看</el-button><el-button type="success" link>编辑</el-button><el-button type="danger" link>取消关联</el-button></template></el-table-column></el-table><div style="margin-top:12px"><el-button type="success"><el-icon><Plus /></el-icon> 添加家庭成员</el-button></div>'
            elif not fields and '明细' in sec_name:
                table_html = '      <el-table :data="detailData" border style="margin-top:12px"><el-table-column type="index" label="序号" width="60" align="center" /><el-table-column prop="name" label="药品名称" min-width="180" /><el-table-column prop="spec" label="规格" min-width="120" /><el-table-column prop="quantity" label="数量" min-width="100" /><el-table-column prop="price" label="单价" min-width="100" /><el-table-column prop="amount" label="金额" min-width="100" /><el-table-column label="操作" width="100" align="center"><template #default><el-button type="danger" link>删除</el-button></template></el-table-column></el-table><div style="margin-top:12px"><el-button type="primary"><el-icon><Plus /></el-icon> 添加药品</el-button></div>'
            sec_html.append(f'    <div class="section-block">\n      <div class="section-title">{sec_name}</div>\n      <el-form :model="form" label-width="100px" class="form-grid">\n{field_html}\n      </el-form>\n{table_html}\n    </div>')
        return FORM_TPL.replace('$TITLE', title).replace('$SUBTITLE', '请填写以下信息').replace('$SECTIONS', '\n'.join(sec_html)).replace('$FORM_DEFAULTS', ',\n'.join(fd))

    # list page
    cols = infer_columns(title)
    filters = infer_filters(title)
    sf, rs = build_search_reset(filters)
    cols_html = '\n'.join(f'        {render_col(c)}' for c in cols)
    filters_html = render_filters(filters)
    actions_html = render_actions(title, ptype)
    return LIST_TPL.replace('$SUBTITLE', '数据列表').replace('$TITLE', title).replace('$ACTIONS', actions_html).replace('$FILTERS', filters_html).replace('$COLUMNS', cols_html).replace('$SEARCH_FIELDS', sf).replace('$RESET', rs)

# ========== 生成所有页面 ==========
generated = 0
for r in routes:
    if r['hidden']:
        # 详情/表单页也生成（更友好的模板）
        ptype = page_type(r['title'])
        if ptype in ('detail','form'):
            full_path = os.path.join(VIEWS_DIR, r['view'])
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            content = build_page(r)
            open(full_path, 'w', encoding='utf-8').write(content)
            generated += 1
    else:
        full_path = os.path.join(VIEWS_DIR, r['view'])
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        content = build_page(r)
        open(full_path, 'w', encoding='utf-8').write(content)
        generated += 1

print(f'Generated {generated} pages')
