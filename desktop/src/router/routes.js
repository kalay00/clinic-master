import Layout from '@/layout/index.vue'

export const constantRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', hidden: true }
  },
  {
    path: '/retrieve-password',
    name: 'RetrievePassword',
    component: () => import('@/views/login/retrieve-password.vue'),
    meta: { title: '找回密码', hidden: true }
  },
  {
    path: '/apply-trial',
    name: 'ApplyTrial',
    component: () => import('@/views/login/apply-trial.vue'),
    meta: { title: '申请试用', hidden: true }
  },
  {
    path: '/tenant-select',
    name: 'TenantSelect',
    component: () => import('@/views/login/tenant-select.vue'),
    meta: { title: '选择租户', hidden: true }
  },
  {
    path: '/redirect/:path(.*)',
    name: 'Redirect',
    component: () => import('@/views/redirect/index.vue'),
    meta: { title: '重定向', hidden: true }
  },
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404', hidden: true }
  },
  {
    path: '/403',
    name: '403',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '403', hidden: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/overview',
    meta: { hidden: true, homeGroup: true },
    children: [
      {
        path: 'overview',
        name: 'Overview',
        component: () => import('@/views/home/overview.vue'),
        meta: { title: '经营概况', icon: 'DataLine', isFirstMenu: true }
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/home/dashboard.vue'),
        meta: { title: '工作台', icon: 'HomeFilled' }
      }
    ]
  }
]

export const asyncRoutes = [
  // ===== 新开就诊 =====
  {
    path: '/consultation',
    component: Layout,
    redirect: '/consultation/record',
    name: 'Consultation',
    meta: { title: '新开就诊', icon: 'FirstAidKit' },
    children: [
      {
        path: 'western',
        name: 'ConsultationWestern',
        component: () => import('@/views/consultation/western.vue'),
        meta: { title: '西药处方', icon: 'FirstAidKit' }
      },
      {
        path: 'chinese',
        name: 'ConsultationChinese',
        component: () => import('@/views/consultation/chinese.vue'),
        meta: { title: '中药处方', icon: 'FirstAidKit', hidden: true }
      },
      {
        path: 'inspection',
        name: 'ConsultationInspection',
        component: () => import('@/views/consultation/inspection.vue'),
        meta: { title: '检查项目', icon: 'FirstAidKit', hidden: true }
      },
      {
        path: 'record',
        name: 'ConsultationRecord',
        component: () => import('@/views/consultation/record.vue'),
        meta: { title: '病历', icon: 'Document', hidden: true }
      },
      {
        path: 'charge',
        name: 'ConsultationCharge',
        component: () => import('@/views/consultation/charge.vue'),
        meta: { title: '收费', icon: 'Money', hidden: true }
      },
    ]
  },
  // ===== 挂号 =====
  {
    path: '/registration',
    component: Layout,
    redirect: '/registration/index',
    name: 'Registration',
    meta: { title: '挂号管理', icon: 'Tickets' },
    children: [
      {
        path: 'create',
        name: 'RegistrationCreate',
        component: () => import('@/views/registration/create.vue'),
        meta: { title: '新增挂号', icon: 'Plus' }
      },
      {
        path: 'index',
        name: 'RegistrationList',
        component: () => import('@/views/registration/index.vue'),
        meta: { title: '挂号记录', icon: 'Tickets' }
      },
      {
        path: 'schedule',
        name: 'RegistrationSchedule',
        component: () => import('@/views/registration/schedule.vue'),
        meta: { title: '排班管理', icon: 'Calendar' }
      },
      {
        path: 'view/:id',
        name: 'RegistrationView',
        component: () => import('@/views/registration/view.vue'),
        meta: { title: '查看挂号信息', hidden: true }
      },
      {
        path: 'edit/:id',
        name: 'RegistrationEdit',
        component: () => import('@/views/registration/edit.vue'),
        meta: { title: '编辑挂号信息', hidden: true }
      }
    ]
  },
  // ===== 药品零售 =====
  {
    path: '/retail',
    component: Layout,
    redirect: '/retail/select',
    name: 'Retail',
    meta: { title: '药品零售', icon: 'ShoppingCart' },
    children: [
      {
        path: 'select',
        name: 'RetailSelect',
        component: () => import('@/views/retail/select.vue'),
        meta: { title: '选择药品', icon: 'ShoppingCart' }
      },
      {
        path: 'charge',
        name: 'RetailCharge',
        component: () => import('@/views/retail/charge.vue'),
        meta: { title: '收费', icon: 'Money', hidden: true }
      }
    ]
  },
  // ===== 收费管理 =====
  {
    path: '/charge',
    component: Layout,
    redirect: '/charge/paid',
    name: 'ChargeManage',
    meta: { title: '收费管理', icon: 'Wallet' },
    children: [
      {
        path: 'paid',
        name: 'ChargePaid',
        component: () => import('@/views/charge/paid.vue'),
        meta: { title: '已收费', icon: 'Wallet' }
      },
      {
        path: 'refund/:id',
        name: 'ChargeRefund',
        component: () => import('@/views/charge/refund.vue'),
        meta: { title: '退费', icon: 'RefreshLeft', hidden: true }
      },
      {
        path: 'refunded/:id',
        name: 'ChargeRefunded',
        component: () => import('@/views/charge/refunded.vue'),
        meta: { title: '已退费', icon: 'CircleCheck', hidden: true }
      },
      {
        path: 'detail/:id',
        name: 'OrderDetail',
        component: () => import('@/views/charge/detail.vue'),
        meta: { title: '订单详情', hidden: true }
      }
    ]
  },
  // ===== 患者管理 =====
  {
    path: '/patients',
    component: Layout,
    redirect: '/patients/index',
    name: 'Patients',
    meta: { title: '患者管理', icon: 'Postcard' },
    children: [
      {
        path: 'index',
        name: 'PatientList',
        component: () => import('@/views/patients/index.vue'),
        meta: { title: '患者管理', icon: 'Postcard' }
      },
      {
        path: 'create',
        name: 'PatientCreate',
        component: () => import('@/views/patients/create.vue'),
        meta: { title: '新增患者信息', hidden: true }
      },
      {
        path: 'edit/:id',
        name: 'PatientEdit',
        component: () => import('@/views/patients/edit.vue'),
        meta: { title: '编辑患者信息', hidden: true }
      }
    ]
  },
  // ===== 药品管理 =====
  {
    path: '/drugs',
    component: Layout,
    redirect: '/drugs/maintain',
    name: 'DrugManage',
    meta: { title: '药品管理', icon: 'SwitchFilled' },
    children: [
      {
        path: 'maintain',
        name: 'DrugMaintain',
        component: () => import('@/views/drugs/maintain.vue'),
        meta: { title: '药品信息维护', icon: 'MedicineBox' }
      },
      {
        path: 'inbound',
        name: 'DrugInbound',
        component: () => import('@/views/drugs/inbound.vue'),
        meta: { title: '入库管理', icon: 'Box' }
      },
      {
        path: 'outbound',
        name: 'DrugOutbound',
        component: () => import('@/views/drugs/outbound.vue'),
        meta: { title: '出库管理', icon: 'Promotion' }
      },
      {
        path: 'stock',
        name: 'DrugStock',
        component: () => import('@/views/drugs/stock.vue'),
        meta: { title: '库存管理', icon: 'Histogram' }
      },
      {
        path: 'check',
        name: 'DrugCheck',
        component: () => import('@/views/drugs/check.vue'),
        meta: { title: '库存盘点', icon: 'ListCheck' }
      },
      {
        path: 'price',
        name: 'DrugPrice',
        component: () => import('@/views/drugs/price.vue'),
        meta: { title: '药品调价', icon: 'PriceTag' }
      },
      {
        path: 'create-western',
        name: 'DrugCreateWestern',
        component: () => import('@/views/drugs/create-western.vue'),
        meta: { title: '新增药品-西成药', hidden: true }
      },
      {
        path: 'create-chinese-patent',
        name: 'DrugCreateChinesePatent',
        component: () => import('@/views/drugs/create-chinese-patent.vue'),
        meta: { title: '新增药品-中成药', hidden: true }
      },
      {
        path: 'create-herb',
        name: 'DrugCreateHerb',
        component: () => import('@/views/drugs/create-herb.vue'),
        meta: { title: '新增药品-中药', hidden: true }
      },
      {
        path: 'inbound/create',
        name: 'InboundCreate',
        component: () => import('@/views/drugs/inbound-create.vue'),
        meta: { title: '新增入库信息', hidden: true }
      },
      {
        path: 'inbound/edit/:id',
        name: 'InboundEdit',
        component: () => import('@/views/drugs/inbound-edit.vue'),
        meta: { title: '编辑入库信息', hidden: true }
      },
      {
        path: 'inbound/detail/:id',
        name: 'InboundDetail',
        component: () => import('@/views/drugs/inbound-detail.vue'),
        meta: { title: '入库详情', hidden: true }
      },
      {
        path: 'outbound/create',
        name: 'OutboundCreate',
        component: () => import('@/views/drugs/outbound-create.vue'),
        meta: { title: '新增出库信息', hidden: true }
      },
      {
        path: 'outbound/edit/:id',
        name: 'OutboundEdit',
        component: () => import('@/views/drugs/outbound-edit.vue'),
        meta: { title: '编辑出库信息', hidden: true }
      },
      {
        path: 'outbound/detail/:id',
        name: 'OutboundDetail',
        component: () => import('@/views/drugs/outbound-detail.vue'),
        meta: { title: '出库详情', hidden: true }
      },
      {
        path: 'stock/detail/:id',
        name: 'StockDetail',
        component: () => import('@/views/drugs/stock-detail.vue'),
        meta: { title: '查看库存明细', hidden: true }
      },
      {
        path: 'check/create',
        name: 'CheckCreate',
        component: () => import('@/views/drugs/check-create.vue'),
        meta: { title: '新增盘点', hidden: true }
      },
      {
        path: 'check/detail/:id',
        name: 'CheckDetail',
        component: () => import('@/views/drugs/check-detail.vue'),
        meta: { title: '盘点详情', hidden: true }
      },
      {
        path: 'price/create',
        name: 'PriceCreate',
        component: () => import('@/views/drugs/price-create.vue'),
        meta: { title: '新增药品调价', hidden: true }
      },
      {
        path: 'price/detail/:id',
        name: 'PriceDetail',
        component: () => import('@/views/drugs/price-detail.vue'),
        meta: { title: '查看调价详情', hidden: true }
      },
      {
        path: 'price/edit/:id',
        name: 'PriceEdit',
        component: () => import('@/views/drugs/price-edit.vue'),
        meta: { title: '编辑药品调价', hidden: true }
      }
    ]
  },
  // ===== 会员管理 =====
  {
    path: '/members',
    component: Layout,
    redirect: '/members/index',
    name: 'MemberManage',
    meta: { title: '会员管理', icon: 'Star' },
    children: [
      {
        path: 'index',
        name: 'MemberList',
        component: () => import('@/views/members/index.vue'),
        meta: { title: '会员管理', icon: 'Star' }
      }
    ]
  },
  // ===== 统计报表 =====
  {
    path: '/statistics',
    component: Layout,
    redirect: '/statistics/charge',
    name: 'Statistics',
    meta: { title: '统计报表', icon: 'PieChart' },
    children: [
      {
        path: 'charge',
        name: 'StatCharge',
        component: () => import('@/views/statistics/charge.vue'),
        meta: { title: '收费统计', icon: 'PieChart' }
      },
      {
        path: 'patient',
        name: 'StatPatient',
        component: () => import('@/views/statistics/patient.vue'),
        meta: { title: '患者统计', icon: 'User' }
      },
      {
        path: 'inspection',
        name: 'StatInspection',
        component: () => import('@/views/statistics/inspection.vue'),
        meta: { title: '检查项目统计', icon: 'DataAnalysis' }
      },
      {
        path: 'drug',
        name: 'StatDrug',
        component: () => import('@/views/statistics/drug.vue'),
        meta: { title: '药品统计', icon: 'Histogram' }
      }
    ]
  },
  // ===== 系统设置 =====
  {
    path: '/settings',
    component: Layout,
    redirect: '/settings/clinic',
    name: 'Settings',
    meta: { title: '系统设置', icon: 'Setting' },
    children: [
      {
        path: 'clinic',
        name: 'SettingClinic',
        component: () => import('@/views/settings/clinic.vue'),
        meta: { title: '诊所信息维护', icon: 'OfficeBuilding' }
      },
      {
        path: 'dict',
        name: 'SettingDict',
        component: () => import('@/views/settings/dict.vue'),
        meta: { title: '字典表维护', icon: 'Notebook' }
      },
      {
        path: 'record',
        name: 'SettingRecord',
        component: () => import('@/views/settings/record.vue'),
        meta: { title: '病历信息', icon: 'Document', hidden: true }
      },
      {
        path: 'drug',
        name: 'SettingDrug',
        component: () => import('@/views/settings/drug.vue'),
        meta: { title: '药品信息', icon: 'MedicineBox', hidden: true }
      },
      {
        path: 'inspection',
        name: 'SettingInspection',
        component: () => import('@/views/settings/inspection.vue'),
        meta: { title: '检查项目', icon: 'FirstAidKit', hidden: true }
      },
      {
        path: 'patient-source',
        name: 'SettingPatientSource',
        component: () => import('@/views/settings/patient-source.vue'),
        meta: { title: '患者来源', icon: 'Connection', hidden: true }
      },
      {
        path: 'employee',
        name: 'SettingEmployee',
        component: () => import('@/views/settings/employee.vue'),
        meta: { title: '员工管理', icon: 'UserFilled' }
      },
      {
        path: 'template',
        name: 'SettingTemplate',
        component: () => import('@/views/settings/template.vue'),
        meta: { title: '模版维护', icon: 'Files' }
      },
      {
        path: 'supplier',
        name: 'SettingSupplier',
        component: () => import('@/views/settings/supplier.vue'),
        meta: { title: '供应商管理', icon: 'Van' }
      },
      {
        path: 'fee',
        name: 'SettingFee',
        component: () => import('@/views/settings/fee.vue'),
        meta: { title: '费用设置', icon: 'Money' }
      },
      {
        path: 'surcharge',
        name: 'SettingSurcharge',
        component: () => import('@/views/settings/surcharge.vue'),
        meta: { title: '附加费用设置', icon: 'Money', hidden: true }
      },
      {
        path: 'payment-method',
        name: 'SettingPaymentMethod',
        component: () => import('@/views/settings/payment-method.vue'),
        meta: { title: '支付方式设置', icon: 'CreditCard', hidden: true }
      },
      {
        path: 'payment',
        name: 'SettingPayment',
        component: () => import('@/views/settings/payment.vue'),
        meta: { title: '支付记录', icon: 'Wallet', hidden: true }
      },
      {
        path: 'basic',
        name: 'SettingBasic',
        component: () => import('@/views/settings/basic.vue'),
        meta: { title: '基础设置', icon: 'Tools' }
      },
      {
        path: 'log',
        name: 'SettingLog',
        component: () => import('@/views/settings/log.vue'),
        meta: { title: '操作日志', icon: 'DocumentCopy' }
      },
      {
        path: 'account',
        name: 'SettingAccount',
        component: () => import('@/views/settings/account.vue'),
        meta: { title: '账号资料', icon: 'Avatar', hidden: true }
      },
      {
        path: 'password',
        name: 'SettingPassword',
        component: () => import('@/views/settings/password.vue'),
        meta: { title: '修改密码', icon: 'Key', hidden: true }
      },
      {
        path: 'notify',
        name: 'SettingNotify',
        component: () => import('@/views/settings/notify.vue'),
        meta: { title: '消息通知', icon: 'Bell', hidden: true }
      },
      {
        path: 'notice',
        name: 'SettingNotice',
        component: () => import('@/views/settings/notice.vue'),
        meta: { title: '系统公告', icon: 'Bell', hidden: true }
      },
      {
        path: 'third-party',
        name: 'SettingThirdParty',
        component: () => import('@/views/settings/third-party.vue'),
        meta: { title: '第三方配置', icon: 'Connection', hidden: true }
      },
      {
        path: 'platform',
        name: 'SettingPlatform',
        component: () => import('@/views/settings/platform.vue'),
        meta: { title: '平台管理', icon: 'Platform', hidden: true }
      }
    ]
  },
  // 404
  { path: '/:pathMatch(.*)*', redirect: '/404', meta: { hidden: true } }
]

export default asyncRoutes
