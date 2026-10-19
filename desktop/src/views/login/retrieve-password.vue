<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-title">找回密码</div>
      <div class="login-form">
        <div class="his-form-item">
          <label class="his-form-label">手机号</label>
          <input class="his-input" placeholder="请输入手机号" />
        </div>
        <button class="his-btn his-btn-primary his-btn-lg" style="width:100%">提交</button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/his-ui.css';
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.login-box {
  width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}
.login-title {
  font-size: 22px;
  font-weight: 700;
  color: #5b7cff;
  text-align: center;
  margin-bottom: 32px;
}
.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
