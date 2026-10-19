import { post } from '@/utils/request'

// 医保
export function verifyMedicalInsurance(data) {
  return post('/integrations/medical-insurance/verify', data).then(res => res.data)
}
export function payMedicalInsurance(data) {
  return post('/integrations/medical-insurance/pay', data).then(res => res.data)
}
// 支付渠道
export function payWeChat(data) {
  return post('/integrations/wechat/pay', data).then(res => res.data)
}
export function payAlipay(data) {
  return post('/integrations/alipay/pay', data).then(res => res.data)
}
export function authWeChat(data) {
  return post('/integrations/wechat/auth', data).then(res => res.data)
}

export default {
  verifyMedicalInsurance,
  payMedicalInsurance,
  payWeChat,
  payAlipay,
  authWeChat
}
