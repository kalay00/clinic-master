import { get, post, put, del } from '@/utils/request'

function toListParams(params = {}) {
  const backend = {
    page: params.page || 1,
    page_size: params.page_size || 10
  }
  if (params.type) backend.type = params.type
  return backend
}

// 打印模板列表
export function getPrintTemplates(params = {}) {
  return get('/print-templates', toListParams(params)).then(res => res.data)
}

export function getPrintTemplate(id) {
  return get(`/print-templates/${id}`).then(res => res.data)
}

export function createPrintTemplate(data) {
  return post('/print-templates', data).then(res => res.data)
}

export function updatePrintTemplate(id, data) {
  return put(`/print-templates/${id}`, data).then(res => res.data)
}

export function deletePrintTemplate(id) {
  return del(`/print-templates/${id}`).then(res => res.data)
}

// 设为默认模板
export function setDefaultPrintTemplate(id) {
  return post(`/print-templates/${id}/set-default`).then(res => res.data)
}

// 预览模板
export function previewPrintTemplate(id, params = {}) {
  return get(`/print-templates/${id}/preview`, params).then(res => res.data)
}

// 复制模板
export function duplicatePrintTemplate(id, newName = null) {
  const config = newName ? { params: { new_name: newName } } : {}
  return post(`/print-templates/${id}/duplicate`, null, config).then(res => res.data)
}

// 初始化预设模板
export function initPresetTemplates() {
  return post('/print-templates/init-preset-templates').then(res => res.data)
}

export default {
  getPrintTemplates,
  getPrintTemplate,
  createPrintTemplate,
  updatePrintTemplate,
  deletePrintTemplate,
  setDefaultPrintTemplate,
  previewPrintTemplate,
  duplicatePrintTemplate,
  initPresetTemplates
}
