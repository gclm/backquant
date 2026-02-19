<template>
  <section class="coming-soon-page">
    <div class="coming-soon-card">
      <h2>开发中</h2>
      <p>敬请期待</p>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ComingSoonPage'
};
</script>

<style scoped>
.coming-soon-page {
  min-height: calc(100vh - 64px - 48px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.coming-soon-card {
  width: min(520px, 100%);
  border: 1px solid #dfe7f2;
  border-radius: 14px;
  background: #ffffff;
  text-align: center;
  padding: 42px 24px;
  box-shadow: 0 10px 30px rgba(15, 43, 78, 0.08);
}

.coming-soon-card h2 {
  margin: 0;
  font-size: 30px;
  color: #1f6feb;
  letter-spacing: 2px;
}

.coming-soon-card p {
  margin: 12px 0 0;
  font-size: 18px;
  color: #5f6f86;
}
</style>
