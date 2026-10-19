// 系统管理相关 API（用户/角色/科室/医生）统一从这里导出，避免与旧占位实现混淆。
import userApi from './user'
import roleApi from './role'
import departmentApi from './department'
import doctorApi from './doctor'

export { userApi, roleApi, departmentApi, doctorApi }

export default {
  user: userApi,
  role: roleApi,
  department: departmentApi,
  doctor: doctorApi
}
