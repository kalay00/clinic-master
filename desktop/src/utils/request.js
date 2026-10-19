import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import config from '@/config'
import { logError } from '@/utils/logger'

const service = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: config.timeout,
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
})

const pendingRequests = new Map()

function generateRequestKey(config) {
  const { method, url, params, data } = config
  return [method, url, JSON.stringify(params), JSON.stringify(data)].join('&')
}

function addPendingRequest(config) {
  const requestKey = generateRequestKey(config)
  const controller = new AbortController()
  config.signal = controller.signal
  pendingRequests.set(requestKey, controller)
}

function removePendingRequest(config) {
  const requestKey = generateRequestKey(config)
  if (pendingRequests.has(requestKey)) {
    pendingRequests.delete(requestKey)
  }
}

service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    config.headers['timestamp'] = Date.now()
    addPendingRequest(config)
    return config
  },
  error => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    removePendingRequest(response.config)
    const res = response.data
    console.log('res', res)
    if (res.code !== undefined && res.code !== 200 && res.code !== 0) {
      ElMessage.error(res.message || '请求失败')

      if (res.code === 401) {
        handleUnauthorized()
      }

      if (res.code === 403) {
        ElMessage.error('没有权限访问')
      }

      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res
  },
  async error => {
    removePendingRequest(error.config || {})
    console.error('Response Error:', error)
    logError('Request Error: ' + error.message, { url: error.config?.url, status: error.response?.status })

    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
      return Promise.reject(error)
    }

    const status = error.response?.status
    switch (status) {
      case 400:
        ElMessage.error('请求参数错误')
        break
      case 401:
        handleUnauthorized()
        break
      case 403:
        ElMessage.error('没有权限访问')
        break
      case 404:
        ElMessage.error('请求资源不存在')
        break
      case 500:
      case 501:
      case 502:
      case 503:
      case 504:
        ElMessage.error('服务器错误，请稍后重试')
        break
      default:
        ElMessage.error(error.message || '网络错误')
    }

    return Promise.reject(error)
  }
)

function handleUnauthorized() {
  const userStore = useUserStore()
  ElMessageBox.confirm('登录状态已过期，请重新登录', '系统提示', {
    confirmButtonText: '重新登录',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      userStore.resetState()
      window.location.href = '/#/login'
    })
    .catch(() => {})
}

export function request(config) {
  return service(config)
}

export function get(url, params = {}, config = {}) {
  return service({ url, method: 'get', params, ...config })
}

export function post(url, data = {}, config = {}) {
  return service({ url, method: 'post', data, ...config })
}

export function put(url, data = {}, config = {}) {
  return service({ url, method: 'put', data, ...config })
}

export function del(url, params = {}, config = {}) {
  return service({ url, method: 'delete', params, ...config })
}

export function upload(url, file, data = {}, config = {}) {
  const formData = new FormData()
  formData.append('file', file)
  Object.keys(data).forEach(key => {
    formData.append(key, data[key])
  })
  return service({
    url,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    ...config
  })
}

export function download(url, params = {}, filename = '') {
  return service({
    url,
    method: 'get',
    params,
    responseType: 'blob'
  }).then(res => {
    const blob = new Blob([res])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)
  })
}

export default service
