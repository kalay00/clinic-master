<template>
  <div class="patient-form">
    <div class="form-row">
      <div class="form-item">
        <label class="form-label required">患者姓名</label>
        <div class="input-group">
          <input class="his-input" placeholder="患者姓名/手机号码/证件号码/卡号" />
          <button class="search-btn">
            <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
              <path d="M11.7422 10.3439C12.5329 9.2673 13 7.9382 13 6.5C13 2.91015 10.0899 0 6.5 0C2.91015 0 0 2.91015 0 6.5C0 10.0899 2.91015 13 6.5 13C7.9382 13 9.2673 12.5329 10.3439 11.7422L14.1464 15.5456L15 14.6921L11.7422 10.3439ZM6.5 11.5C3.73858 11.5 1.5 9.26142 1.5 6.5C1.5 3.73858 3.73858 1.5 6.5 1.5C9.26142 1.5 11.5 3.73858 11.5 6.5C11.5 9.26142 9.26142 11.5 6.5 11.5Z" />
            </svg>
          </button>
        </div>
      </div>
      <div class="form-item">
        <label class="form-label">患者卡号</label>
        <input class="his-input" placeholder="请输入病人卡号" />
      </div>
      <div class="form-item">
        <label class="form-label required">患者年龄</label>
        <div class="input-group">
          <input class="his-input" placeholder="请输入数字" />
          <span class="unit">岁</span>
        </div>
      </div>
      <div class="form-item">
        <label class="form-label required">出生日期</label>
        <input class="his-input" type="date" />
      </div>
    </div>
    <div class="form-row">
      <div class="form-item">
        <label class="form-label required">性别</label>
        <select class="his-select">
          <option>男</option>
          <option>女</option>
        </select>
      </div>
      <div class="form-item">
        <label class="form-label">手机号码</label>
        <input class="his-input" placeholder="请输入手机号码" />
      </div>
      <div class="form-item">
        <label class="form-label">证件号码</label>
        <input class="his-input" placeholder="请输入证件号码" />
      </div>
      <div class="form-item">
        <label class="form-label required">接诊类型</label>
        <select class="his-select">
          <option>请选择</option>
          <option>初诊</option>
          <option>复诊</option>
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-item">
        <label class="form-label">地址</label>
        <select class="his-select">
          <option>广东省/深圳市</option>
        </select>
      </div>
      <div class="form-item" style="grid-column: span 3">
        <label class="form-label" style="visibility: hidden">详细地址</label>
        <input class="his-input" placeholder="请输入详细地址" />
      </div>
    </div>
    <div class="form-row">
      <div class="form-item" style="grid-column: span 2">
        <label class="form-label required">诊断</label>
        <div class="input-group">
          <input class="his-input" />
          <button class="search-btn">
            <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
              <path d="M11.7422 10.3439C12.5329 9.2673 13 7.9382 13 6.5C13 2.91015 10.0899 0 6.5 0C2.91015 0 0 2.91015 0 6.5C0 10.0899 2.91015 13 6.5 13C7.9382 13 9.2673 12.5329 10.3439 11.7422L14.1464 15.5456L15 14.6921L11.7422 10.3439ZM6.5 11.5C3.73858 11.5 1.5 9.26142 1.5 6.5C1.5 3.73858 3.73858 1.5 6.5 1.5C9.26142 1.5 11.5 3.73858 11.5 6.5C11.5 9.26142 9.26142 11.5 6.5 11.5Z" />
            </svg>
          </button>
        </div>
      </div>
      <div class="form-item" style="grid-column: span 2">
        <label class="form-label">医嘱</label>
        <div class="input-group">
          <input class="his-input" />
          <button class="search-btn">
            <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
              <path d="M11.7422 10.3439C12.5329 9.2673 13 7.9382 13 6.5C13 2.91015 10.0899 0 6.5 0C2.91015 0 0 2.91015 0 6.5C0 10.0899 2.91015 13 6.5 13C7.9382 13 9.2673 12.5329 10.3439 11.7422L14.1464 15.5456L15 14.6921L11.7422 10.3439ZM6.5 11.5C3.73858 11.5 1.5 9.26142 1.5 6.5C1.5 3.73858 3.73858 1.5 6.5 1.5C9.26142 1.5 11.5 3.73858 11.5 6.5C11.5 9.26142 9.26142 11.5 6.5 11.5Z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.patient-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.form-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-label {
  font-size: 13px;
  color: #374151;
}
.form-label.required::after {
  content: '*';
  color: #ef4444;
  margin-left: 2px;
}
.input-group {
  display: flex;
  align-items: stretch;
}
.input-group .his-input {
  flex: 1;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
.search-btn {
  width: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #7b8dfd;
  color: #fff;
  border: none;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  cursor: pointer;
}
.search-btn:hover {
  background: #6876e8;
}
.unit {
  display: flex;
  align-items: center;
  padding: 0 10px;
  background: #fff;
  border: 1px solid #d1d5db;
  border-left: none;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  font-size: 13px;
  color: #6b7280;
}
</style>
