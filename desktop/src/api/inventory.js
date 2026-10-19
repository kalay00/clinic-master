import { get, post, put, del } from '@/utils/request'

function toBackendListParams(params = {}) {
  const page = params.page || 1
  const pageSize = params.page_size || params.pageSize || 10
  const backend = {
    page,
    page_size: pageSize
  }
  const keyword = params.keyword || params.search
  if (keyword) backend.search = keyword
  if (params.status) backend.status = params.status
  if (params.supplier_id) backend.supplier_id = params.supplier_id
  if (params.purchase_order_id) backend.purchase_order_id = params.purchase_order_id
  if (params.drug_id) backend.drug_id = params.drug_id
  if (params.transaction_type) backend.transaction_type = params.transaction_type
  if (params.start_date) backend.start_date = params.start_date
  if (params.end_date) backend.end_date = params.end_date
  return backend
}

// 供应商（后端路径为 /inventory/suppliers）
export function getSuppliers(params = {}) {
  return get('/inventory/suppliers', toBackendListParams(params)).then(res => res.data)
}
export function getSupplier(id) {
  return get(`/inventory/suppliers/${id}`).then(res => res.data)
}
export function createSupplier(data) {
  return post('/inventory/suppliers', data).then(res => res.data)
}
export function updateSupplier(id, data) {
  return put(`/inventory/suppliers/${id}`, data).then(res => res.data)
}
export function deleteSupplier(id) {
  return del(`/inventory/suppliers/${id}`).then(res => res.data)
}

// 采购单
export function getPurchaseOrders(params = {}) {
  return get('/inventory/purchase-orders', toBackendListParams(params)).then(res => res.data)
}
export function getPurchaseOrder(id) {
  return get(`/inventory/purchase-orders/${id}`).then(res => res.data)
}
export function createPurchaseOrder(data) {
  return post('/inventory/purchase-orders', data).then(res => res.data)
}
export function updatePurchaseOrder(id, data) {
  return put(`/inventory/purchase-orders/${id}`, data).then(res => res.data)
}
export function approvePurchaseOrder(id) {
  return post(`/inventory/purchase-orders/${id}/approve`).then(res => res.data)
}
export function receivePurchaseOrder(id) {
  return post(`/inventory/purchase-orders/${id}/receive`).then(res => res.data)
}
export function deletePurchaseOrder(id) {
  return del(`/inventory/purchase-orders/${id}`).then(res => res.data)
}
export function getReturnablePurchaseOrder(id) {
  return get(`/inventory/purchase-orders/${id}/returnable`).then(res => res.data)
}

// 库存流水
export function getTransactions(params = {}) {
  return get('/inventory/transactions', toBackendListParams(params)).then(res => res.data)
}

// 盘点单
export function getInventoryChecks(params = {}) {
  return get('/inventory/checks', toBackendListParams(params)).then(res => res.data)
}
export function getInventoryCheck(id) {
  return get(`/inventory/checks/${id}`).then(res => res.data)
}
export function createInventoryCheck(data) {
  return post('/inventory/checks', data).then(res => res.data)
}
export function completeInventoryCheck(id) {
  return post(`/inventory/checks/${id}/complete`).then(res => res.data)
}
export function deleteInventoryCheck(id) {
  return del(`/inventory/checks/${id}`).then(res => res.data)
}

// 退货单
export function getReturnOrders(params = {}) {
  return get('/inventory/return-orders', toBackendListParams(params)).then(res => res.data)
}
export function getReturnOrder(id) {
  return get(`/inventory/return-orders/${id}`).then(res => res.data)
}
export function createReturnOrder(data) {
  return post('/inventory/return-orders', data).then(res => res.data)
}
export function updateReturnOrder(id, data) {
  return put(`/inventory/return-orders/${id}`, data).then(res => res.data)
}
export function approveReturnOrder(id) {
  return post(`/inventory/return-orders/${id}/approve`).then(res => res.data)
}
export function completeReturnOrder(id) {
  return post(`/inventory/return-orders/${id}/complete`).then(res => res.data)
}
export function cancelReturnOrder(id) {
  return post(`/inventory/return-orders/${id}/cancel`).then(res => res.data)
}
export function deleteReturnOrder(id) {
  return del(`/inventory/return-orders/${id}`).then(res => res.data)
}

export default {
  getSuppliers,
  getSupplier,
  createSupplier,
  updateSupplier,
  deleteSupplier,
  getPurchaseOrders,
  getPurchaseOrder,
  createPurchaseOrder,
  updatePurchaseOrder,
  approvePurchaseOrder,
  receivePurchaseOrder,
  deletePurchaseOrder,
  getReturnablePurchaseOrder,
  getTransactions,
  getInventoryChecks,
  getInventoryCheck,
  createInventoryCheck,
  completeInventoryCheck,
  deleteInventoryCheck,
  getReturnOrders,
  getReturnOrder,
  createReturnOrder,
  updateReturnOrder,
  approveReturnOrder,
  completeReturnOrder,
  cancelReturnOrder,
  deleteReturnOrder
}
