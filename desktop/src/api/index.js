import authApi from './auth'
import patientApi from './patient'
import registrationApi from './registration'
import treatmentApi from './treatment'
import paymentApi from './payment'
import pharmacyApi from './pharmacy'
import reportApi from './report'
import userApi from './user'
import roleApi from './role'
import departmentApi from './department'
import doctorApi from './doctor'
import tenantApi from './tenant'
import inventoryApi from './inventory'
import printTemplateApi from './printTemplate'
import uploadApi from './upload'
import integrationApi from './integration'
import notificationApi from './notification'
import platformApi from './platform'
import dashboardApi from './dashboard'
import systemApi from './system'
import thirdPartyConfigApi from './thirdPartyConfig'

const api = {
  auth: authApi,
  patient: patientApi,
  registration: registrationApi,
  treatment: treatmentApi,
  payment: paymentApi,
  pharmacy: pharmacyApi,
  report: reportApi,
  user: userApi,
  role: roleApi,
  department: departmentApi,
  doctor: doctorApi,
  tenant: tenantApi,
  inventory: inventoryApi,
  printTemplate: printTemplateApi,
  upload: uploadApi,
  integration: integrationApi,
  notification: notificationApi,
  platform: platformApi,
  dashboard: dashboardApi,
  system: systemApi,
  thirdPartyConfig: thirdPartyConfigApi
}

export default api

export {
  authApi,
  patientApi,
  registrationApi,
  treatmentApi,
  paymentApi,
  pharmacyApi,
  reportApi,
  userApi,
  roleApi,
  departmentApi,
  doctorApi,
  tenantApi,
  inventoryApi,
  printTemplateApi,
  uploadApi,
  integrationApi,
  notificationApi,
  platformApi,
  thirdPartyConfigApi,
  dashboardApi,
  systemApi
}
