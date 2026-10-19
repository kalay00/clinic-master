import request from '@/utils/request'

// 通用字典接口（覆盖病历/药品用法/检查项目/患者来源等所有选项类数据）

// 列表
export function getDictionaryList(params) {
  return request({
    url: '/dictionaries',
    method: 'get',
    params
  }).then(res => res.data)
}

// 详情
export function getDictionaryDetail(id) {
  return request({
    url: `/dictionaries/${id}`,
    method: 'get'
  })
}

// 新增
export function createDictionary(data) {
  return request({
    url: '/dictionaries',
    method: 'post',
    data
  })
}

// 更新
export function updateDictionary(id, data) {
  return request({
    url: `/dictionaries/${id}`,
    method: 'put',
    data
  })
}

// 删除
export function deleteDictionary(id) {
  return request({
    url: `/dictionaries/${id}`,
    method: 'delete'
  })
}
