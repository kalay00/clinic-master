import { get, post, put, del } from '@/utils/request'

export function getNotifications(params = {}) {
  const backend = {
    page: params.page || 1,
    page_size: params.page_size || params.pageSize || 20,
  }
  if (params.notification_type) backend.notification_type = params.notification_type
  if (params.status) backend.status = params.status
  return get('/notifications', backend).then(res => res.data)
}

export function getNotification(id) {
  return get(`/notifications/${id}`).then(res => res.data)
}

export function createNotification(data) {
  return post('/notifications', data).then(res => res.data)
}

export function updateNotification(id, data) {
  return put(`/notifications/${id}`, data).then(res => res.data)
}

export function deleteNotification(id) {
  return del(`/notifications/${id}`).then(res => res.data)
}

export function sendSMS(data) {
  return post('/notifications/send-sms', data).then(res => res.data)
}

export function sendWeChat(data) {
  return post('/notifications/send-wechat', data).then(res => res.data)
}

export default {
  getNotifications,
  getNotification,
  createNotification,
  updateNotification,
  deleteNotification,
  sendSMS,
  sendWeChat,
}
