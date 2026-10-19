import { get, post, put, del } from '@/utils/request'

// 第三方配置接口（后端 module_third_party_config）
// 路由前缀：/third-party/configs

export function getThirdPartyConfigs(params = {}) {
  const backend = {
    page: params.page || 1,
    page_size: params.page_size || params.pageSize || 20,
  }
  if (params.service_type) backend.service_type = params.service_type
  if (params.provider) backend.provider = params.provider
  if (params.is_enabled !== undefined && params.is_enabled !== null && params.is_enabled !== '') {
    backend.is_enabled = params.is_enabled
  }
  return get('/third-party/configs', backend).then(res => res.data)
}

export function getThirdPartyConfig(id) {
  return get(`/third-party/configs/${id}`).then(res => res.data)
}

export function createThirdPartyConfig(data) {
  return post('/third-party/configs', data).then(res => res.data)
}

export function updateThirdPartyConfig(id, data) {
  return put(`/third-party/configs/${id}`, data).then(res => res.data)
}

export function deleteThirdPartyConfig(id) {
  return del(`/third-party/configs/${id}`).then(res => res.data)
}

export function testThirdPartyConfig(id, data = {}) {
  return post(`/third-party/configs/${id}/test`, data).then(res => res.data)
}

export default {
  getThirdPartyConfigs,
  getThirdPartyConfig,
  createThirdPartyConfig,
  updateThirdPartyConfig,
  deleteThirdPartyConfig,
  testThirdPartyConfig,
}
