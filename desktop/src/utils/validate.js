export const validateRules = {
  required: (message = '该项不能为空', trigger = 'blur') => ({
    required: true,
    message,
    trigger
  }),

  email: (message = '请输入正确的邮箱地址', trigger = 'blur') => ({
    type: 'email',
    message,
    trigger
  }),

  phone: (message = '请输入正确的手机号码', trigger = 'blur') => ({
    pattern: /^1[3-9]\d{9}$/,
    message,
    trigger
  }),

  number: (message = '请输入数字', trigger = 'blur') => ({
    type: 'number',
    message,
    trigger
  }),

  integer: (message = '请输入整数', trigger = 'blur') => ({
    pattern: /^-?\d+$/,
    message,
    trigger
  }),

  positiveInteger: (message = '请输入正整数', trigger = 'blur') => ({
    pattern: /^[1-9]\d*$/,
    message,
    trigger
  }),

  url: (message = '请输入正确的URL地址', trigger = 'blur') => ({
    type: 'url',
    message,
    trigger
  }),

  minLength: (min, message = '', trigger = 'blur') => ({
    min,
    message: message || `最少输入 ${min} 个字符`,
    trigger
  }),

  maxLength: (max, message = '', trigger = 'blur') => ({
    max,
    message: message || `最多输入 ${max} 个字符`,
    trigger
  }),

  rangeLength: (min, max, message = '', trigger = 'blur') => ({
    min,
    max,
    message: message || `字符长度需在 ${min}-${max} 之间`,
    trigger
  }),

  range: (min, max, message = '', trigger = 'blur') => ({
    type: 'number',
    min,
    max,
    message: message || `数值需在 ${min}-${max} 之间`,
    trigger
  })
}

export function createValidator(validateFn, message = '校验失败') {
  return (rule, value, callback) => {
    if (validateFn(value)) {
      callback()
    } else {
      callback(new Error(message))
    }
  }
}

export default validateRules
