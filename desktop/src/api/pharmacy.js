import { get, post, put, del } from '@/utils/request'

// 后端路由前缀：/pharmacy/drugs
// 说明：桌面端的「药品目录 / 库存 / 出入库」统一在此模块封装，
// 后端药品目录接口挂在 /pharmacy/drugs，库存预警来自同模块，出入库复用进销存接口。

function toListParams(params = {}) {
  const backend = {
    page: params.page || 1,
    page_size: params.page_size || params.pageSize || 10
  }
  const keyword = params.keyword || params.search
  if (keyword) backend.search = keyword
  if (params.category) backend.category = params.category
  if (params.status) backend.status = params.status
  return backend
}

// 药品目录
export function getDrugs(params = {}) {
  return get('/pharmacy/drugs', toListParams(params)).then(res => res.data)
}

export function getDrug(id) {
  return get(`/pharmacy/drugs/${id}`).then(res => res.data)
}

export function createDrug(data) {
  return post('/pharmacy/drugs', data).then(res => res.data)
}

export function updateDrug(id, data) {
  return put(`/pharmacy/drugs/${id}`, data).then(res => res.data)
}

export function deleteDrug(id) {
  return del(`/pharmacy/drugs/${id}`).then(res => res.data)
}

// 药品分类（后端路由前缀：/pharmacy/drug-categories）
export function getDrugCategories(params = {}) {
  const backend = {
    page: params.page || 1,
    page_size: params.page_size || params.pageSize || 10
  }
  if (params.keyword || params.search) backend.search = params.keyword || params.search
  if (params.status) backend.status = params.status
  return get('/pharmacy/drug-categories', backend).then(res => res.data)
}

export function getDrugCategory(id) {
  return get(`/pharmacy/drug-categories/${id}`).then(res => res.data)
}

export function createDrugCategory(data) {
  return post('/pharmacy/drug-categories', data).then(res => res.data)
}

export function updateDrugCategory(id, data) {
  return put(`/pharmacy/drug-categories/${id}`, data).then(res => res.data)
}

export function deleteDrugCategory(id) {
  return del(`/pharmacy/drug-categories/${id}`).then(res => res.data)
}

// 处方发药（POST /pharmacy/drugs/dispense）
export function dispensePrescription(id, items = []) {
  return post('/pharmacy/drugs/dispense', { prescription_id: id, items }).then(res => res.data)
}

// 库存列表（GET /pharmacy/drugs/inventory，关联药品表返回药品信息 + 库存数量）
export function getInventory(params = {}) {
  const backend = {
    page_no: params.page || 1,
    page_size: params.pageSize || params.page_size || 100
  }
  if (params.keyword || params.search) backend.keyword = params.keyword || params.search
  if (params.category) backend.category = params.category
  return get('/pharmacy/drugs/inventory', backend).then(res => res.data)
}

// 库存预警（后端低库存接口）
export function getInventoryWarnings() {
  return get('/pharmacy/drugs/low-stock').then(res => res.data)
}

// 入库 / 出库（复用进销存接口）
export function stockIn(data) {
  return post('/inventory/stock-in', data).then(res => res.data)
}

export function stockOut(data) {
  return post('/inventory/stock-out', data).then(res => res.data)
}

// 药品调价（后端路由前缀：/pharmacy/price-adjustments）
export function getPriceAdjustments(params = {}) {
  const page = params.page || 1
  const pageSize = params.pageSize || params.page_size || 10
  const backend = {
    skip: (page - 1) * pageSize,
    limit: pageSize
  }
  if (params.status) backend.status = params.status
  return get('/pharmacy/price-adjustments', backend).then(res => res.data)
}
export function getPriceAdjustment(id) {
  return get(`/pharmacy/price-adjustments/${id}`).then(res => res.data)
}
export function createPriceAdjustment(data) {
  return post('/pharmacy/price-adjustments', data).then(res => res.data)
}
export function approvePriceAdjustment(id) {
  return post(`/pharmacy/price-adjustments/${id}/approve`).then(res => res.data)
}
export function deletePriceAdjustment(id) {
  return del(`/pharmacy/price-adjustments/${id}`).then(res => res.data)
}

export default {
  getDrugs,
  getDrug,
  createDrug,
  updateDrug,
  deleteDrug,
  getDrugCategories,
  getDrugCategory,
  createDrugCategory,
  updateDrugCategory,
  deleteDrugCategory,
  dispensePrescription,
  getInventory,
  getInventoryWarnings,
  stockIn,
  stockOut,
  getPriceAdjustments,
  getPriceAdjustment,
  createPriceAdjustment,
  approvePriceAdjustment,
  deletePriceAdjustment
}
