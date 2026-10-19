/**
 * 权限管理模块（对齐 frontend/js/permission.js）
 * 提供菜单权限、功能权限检查，并支持：
 *  - 平台管理员 / 租户内 admin 拥有全部权限
 *  - 带租户前缀的权限码（如 TEST001_treatment:list）兼容匹配
 *  - 资源级兜底（拥有某资源的任意动作权限即可访问该资源菜单）
 */

import { useUserStore } from '@/store/modules/user'

/**
 * 菜单权限映射：路由名 -> 所需权限
 * 与前端 MENU_PERMISSIONS 对齐；未列出的路由默认允许访问
 */
export const MENU_PERMISSIONS = {
  // 首页
  Overview: [],
  Dashboard: [],
  // 新开就诊
  Consultation: ['treatment:list'],
  ConsultationWestern: ['treatment:list'],
  ConsultationChinese: ['treatment:list'],
  ConsultationInspection: ['treatment:list'],
  ConsultationRecord: ['treatment:list'],
  ConsultationCharge: ['treatment:list'],
  WesternBatch: ['treatment:list'],
  WesternExtra: ['treatment:list'],
  PrescriptionTemplateCall: ['treatment:list'],
  PrescriptionTemplateCreate: ['treatment:list'],
  RecordTemplateCreate: ['treatment:list'],
  RecordTemplateCall: ['treatment:list'],
  RecordInfoCall: ['treatment:list'],
  ChargeConfirm: ['treatment:list'],
  // 挂号
  Registration: ['registration:list'],
  RegistrationCreate: ['registration:list'],
  RegistrationList: ['registration:list'],
  RegistrationSchedule: ['registration:list'],
  RegistrationView: ['registration:list'],
  RegistrationEdit: ['registration:list'],
  // 药品零售 / 收费管理
  Retail: ['payment:list'],
  RetailSelect: ['payment:list'],
  RetailCharge: ['payment:list'],
  ChargeManage: ['payment:list'],
  ChargePaid: ['payment:list'],
  ChargeRefund: ['payment:list'],
  ChargeRefunded: ['payment:list'],
  RefundInfo: ['payment:list'],
  OrderDetail: ['payment:list'],
  // 患者管理
  Patients: ['patient:list'],
  PatientList: ['patient:list'],
  PatientCreate: ['patient:list'],
  PatientEdit: ['patient:list'],
  PatientFamily: ['patient:list'],
  PatientRecords: ['patient:list'],
  PatientCharge: ['patient:list'],
  // 药品管理
  DrugManage: ['drug:list'],
  DrugMaintain: ['drug:list'],
  DrugInbound: ['drug:list'],
  DrugOutbound: ['drug:list'],
  DrugStock: ['drug:list'],
  DrugCheck: ['drug:list'],
  DrugPrice: ['drug:list'],
  DrugCreateWestern: ['drug:list'],
  DrugCreateChinesePatent: ['drug:list'],
  DrugCreateHerb: ['drug:list'],
  InboundCreate: ['drug:list'],
  InboundEdit: ['drug:list'],
  InboundDetail: ['drug:list'],
  OutboundCreate: ['drug:list'],
  OutboundEdit: ['drug:list'],
  OutboundDetail: ['drug:list'],
  StockDetail: ['drug:list'],
  CheckCreate: ['drug:list'],
  CheckDetail: ['drug:list'],
  PriceCreate: ['drug:list'],
  PriceEdit: ['drug:list'],
  // 会员管理
  MemberManage: ['member:list'],
  MemberList: ['member:list'],
  MemberStored: ['member:list'],
  MemberPoints: ['member:list'],
  MemberSettings: ['member:list'],
  MemberRecharge: ['member:list'],
  MemberRefund: ['member:list'],
  MemberPointsChange: ['member:list'],
  MemberLevel: ['member:list'],
  MemberChangeLog: ['member:list'],
  // 统计报表
  Statistics: [],
  StatCharge: [],
  StatPatient: [],
  StatInspection: [],
  StatDrug: [],
  // 系统设置
  Settings: ['system:list'],
  SettingClinic: ['system:list'],
  SettingRecord: ['system:list'],
  SettingDrug: ['system:list'],
  SettingInspection: ['system:list'],
  SettingPatientSource: ['system:list'],
  SettingEmployee: ['system:list'],
  SettingTemplate: ['system:list'],
  SettingSupplier: ['system:list'],
  SettingFee: ['system:list'],
  SettingBasic: ['system:list'],
  SettingLog: ['system:list'],
  SettingAccount: ['system:list'],
  SettingPassword: ['system:list'],
  SettingNotify: ['system:list'],
  // 登录相关
  RetrievePassword: [],
  ApplyTrial: []
}

/**
 * 功能权限映射：功能码 -> 所需权限
 * 与前端 FUNCTION_PERMISSIONS 对齐
 */
export const FUNCTION_PERMISSIONS = {
  // 患者管理
  'patient:create': ['patient:create'],
  'patient:update': ['patient:update'],
  'patient:delete': ['patient:delete'],
  // 挂号管理
  'registration:create': ['registration:create'],
  'registration:update': ['registration:update'],
  'registration:delete': ['registration:delete'],
  // 诊疗管理
  'treatment:create': ['treatment:create'],
  'treatment:update': ['treatment:update'],
  'treatment:delete': ['treatment:delete'],
  // 收费管理
  'payment:create': ['payment:create'],
  'payment:update': ['payment:update'],
  'payment:delete': ['payment:delete'],
  // 药房管理
  'pharmacy:dispense': ['pharmacy:dispense'],
  'pharmacy:create': ['pharmacy:create'],
  'pharmacy:update': ['pharmacy:update'],
  'pharmacy:delete': ['pharmacy:delete'],
  // 系统管理
  'system:user:create': ['system:user:create'],
  'system:user:update': ['system:user:update'],
  'system:user:delete': ['system:user:delete'],
  'system:role:create': ['system:role:create'],
  'system:role:update': ['system:role:update'],
  'system:role:delete': ['system:role:delete']
}

// 取当前登录用户状态（从 userStore 读取，Pinia 已在 main.ts 激活）
function currentUser() {
  const store = useUserStore()
  return {
    isPlatformAdmin: store.isPlatformAdmin,
    roles: store.roles || [],
    permissions: store.permissions || []
  }
}

// 是否系统管理员（平台管理员或租户内 admin 均视为管理员）
export function isAdmin() {
  const { isPlatformAdmin, roles } = currentUser()
  return !!isPlatformAdmin || roles.includes('admin')
}

// 单个权限是否匹配（支持带租户前缀 TENANT_perm:action）
function matchesPermission(requiredPerm, userPerm) {
  if (!requiredPerm || !userPerm) return false
  // 完全匹配
  if (requiredPerm === userPerm) return true
  // 用户权限带租户前缀：TEST001_pharmacy:dispense 匹配 pharmacy:dispense
  if (userPerm.includes('_')) {
    const parts = userPerm.split('_', 2)
    if (parts.length === 2 && parts[1] === requiredPerm) return true
  }
  // 需要的权限带前缀，用户权限不带前缀（向后兼容）
  if (requiredPerm.includes('_')) {
    const parts = requiredPerm.split('_', 2)
    if (parts.length === 2 && parts[1] === userPerm) return true
  }
  return false
}

// 检查是否拥有权限（permission 可为字符串或数组）
export function hasPermission(permission) {
  if (isAdmin()) return true
  if (!permission || (Array.isArray(permission) && permission.length === 0)) return true
  const perms = currentUser().permissions
  if (Array.isArray(permission)) {
    return permission.some(p => perms.some(up => matchesPermission(p, up)))
  }
  return perms.some(up => matchesPermission(permission, up))
}

// 检查是否拥有角色
export function hasRole(role) {
  if (isAdmin()) return true
  if (!role) return false
  const roles = currentUser().roles
  if (Array.isArray(role)) return role.some(r => roles.includes(r))
  return roles.includes(role)
}

// 是否拥有某资源的任意权限（资源级兜底，兼容动作码差异与历史前缀）
export function hasResourcePermission(resource) {
  if (!resource || isAdmin()) return true
  const target = resource + ':'
  return currentUser().permissions.some(up => {
    const norm = up.includes('_') ? up.split('_', 2)[1] : up
    return norm === resource || norm.startsWith(target)
  })
}

// 是否可以访问菜单（按路由名）
export function canAccessMenu(routeName) {
  if (isAdmin()) return true
  const required = MENU_PERMISSIONS[routeName]
  if (!required || (Array.isArray(required) && required.length === 0)) return true
  // 1) 精确 / 带租户前缀匹配
  if (hasPermission(required)) return true
  // 2) 资源级兜底：对该资源拥有任意权限即可见菜单
  const firstPerm = Array.isArray(required) ? required[0] : required
  const normFirst = firstPerm && firstPerm.includes('_') ? firstPerm.split('_', 2)[1] : firstPerm
  const resource = normFirst && normFirst.includes(':') ? normFirst.split(':', 2)[0] : normFirst
  if (hasResourcePermission(resource)) return true
  return false
}

// 是否可以执行功能
export function canExecuteFunction(functionCode) {
  if (isAdmin()) return true
  const required = FUNCTION_PERMISSIONS[functionCode]
  if (!required) return true
  return hasPermission(required)
}
