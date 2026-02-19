// 检查用户是否已登录
export function isAuthenticated() {
  const token = localStorage.getItem('token');
  return !!token;
}

// 获取token
export function getToken() {
  return localStorage.getItem('token');
}

// 获取用户ID
export function getUserId() {
  return localStorage.getItem('userid');
}

// 清除认证信息
export function clearAuth() {
  localStorage.removeItem('token');
  localStorage.removeItem('userid');
}

// 设置认证信息
export function setAuth(token, userid) {
  localStorage.setItem('token', token);
  localStorage.setItem('userid', userid);
} 