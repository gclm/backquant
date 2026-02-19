<template>
  <div class="coming-soon-container">
    <div class="coming-soon-content">
      <div class="coming-soon-icon">
        📊
      </div>
      <h2 class="coming-soon-title">股票策略</h2>
      <p class="coming-soon-message">开发中，敬请期待</p>
      <div class="coming-soon-description">
        <p>我们正在努力开发股票策略功能，包括：</p>
        <ul>
          <li>量化选股模型</li>
          <li>风险控制策略</li>
          <li>实时交易信号</li>
          <li>业绩回测分析</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StockStrategy'
}
</script>

<style scoped>
.coming-soon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 144px);
  padding: 40px 20px;
}

.coming-soon-content {
  text-align: center;
  max-width: 600px;
  background: white;
  padding: 60px 40px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.coming-soon-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.coming-soon-title {
  font-size: 2.5rem;
  color: #303133;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.coming-soon-message {
  font-size: 1.2rem;
  color: #67c23a;
  margin: 0 0 30px 0;
  font-weight: 500;
}

.coming-soon-description {
  text-align: left;
  color: #606266;
}

.coming-soon-description p {
  margin: 0 0 20px 0;
  font-size: 1.1rem;
}

.coming-soon-description ul {
  margin: 0;
  padding-left: 20px;
}

.coming-soon-description li {
  margin-bottom: 10px;
  font-size: 1rem;
}

/* Dark mode styles */
body.dark-mode .coming-soon-content {
  background: #2d2d2d;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

body.dark-mode .coming-soon-title {
  color: #ffffff;
}

body.dark-mode .coming-soon-description {
  color: #b0b3b8;
}

body.dark-mode .coming-soon-description p {
  color: #e0e0e0;
}

/* Responsive styles */
@media screen and (max-width: 768px) {
  .coming-soon-container {
    padding: 20px 16px;
    min-height: calc(100vh - 120px);
  }

  .coming-soon-content {
    padding: 40px 20px;
  }

  .coming-soon-icon {
    font-size: 3rem;
  }

  .coming-soon-title {
    font-size: 2rem;
  }

  .coming-soon-message {
    font-size: 1.1rem;
  }
}
</style>