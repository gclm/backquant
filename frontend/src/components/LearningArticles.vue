<template>
  <div class="learning-articles">
    <div class="articles-container">
      <div class="articles-header">
        <h2 class="page-title">持续学习</h2>
        <p class="page-description">精选学习文章，助您提升交易技能</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <p>加载中...</p>
      </div>

      <!-- 文章列表 -->
      <div v-else-if="articles.length > 0" class="articles-list">
        <div
          v-for="article in articles"
          :key="article.id"
          class="article-card"
          @click="openArticle(article.id)"
        >
          <div class="article-content">
            <h3 class="article-title">{{ article.title }}</h3>
            <div class="article-meta">
              <span class="article-author">{{ article.author }}</span>
              <span class="article-separator">•</span>
              <span class="article-time">{{ article.publish_time }}</span>
              <span class="article-separator">•</span>
              <a
                :href="article.url"
                target="_blank"
                rel="noopener noreferrer"
                class="article-link-inline"
                @click.stop
              >
                原文
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <p>暂无文章</p>
      </div>

      <!-- 分页控件 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          上一页
        </button>
        <span class="pagination-info">
          第 {{ currentPage }} / {{ totalPages }} 页
        </span>
        <button
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axios';
import { API_ENDPOINTS } from '@/config/api';

export default {
  name: 'LearningArticles',
  data() {
    return {
      articles: [],
      loading: false,
      currentPage: 1,
      pageSize: 10,
      total: 0,
      totalPages: 0
    };
  },
  mounted() {
    this.fetchArticles();
  },
  methods: {
    async fetchArticles() {
      this.loading = true;
      try {
        const response = await axios.post(API_ENDPOINTS.LEARNING_ARTICLES, {
          page: this.currentPage,
          size: this.pageSize
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.data.code === 0 && response.data.data) {
          this.articles = response.data.data.list || [];
          this.total = response.data.data.total || 0;
          this.totalPages = response.data.data.total_pages || 0;
          this.currentPage = response.data.data.page || 1;
        } else {
          console.error('获取文章失败:', response.data.msg);
          this.articles = [];
        }
      } catch (error) {
        console.error('获取文章失败:', error);
        this.articles = [];
      } finally {
        this.loading = false;
      }
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page;
        this.fetchArticles();
        this.$el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    },
    openArticle(id) {
      // 通知父组件切换到详情页
      this.$emit('open-article', id);
    }
  }
};
</script>

<style scoped>
.learning-articles {
  padding: 20px;
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f5f7fa 0%, #f8f9fb 100%);
}

.articles-container {
  max-width: 1000px;
  margin: 0 auto;
}

.articles-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  color: #2c3e50;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.page-description {
  color: #718096;
  font-size: 16px;
  margin: 0;
}

/* 加载和空状态 */
.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #718096;
  font-size: 16px;
}

/* 文章列表 */
.articles-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.article-card {
  background: white;
  border-radius: 0.75rem; /* rounded-xl */
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08); /* shadow-sm */
  border: 1px solid #e5e7eb; /* border */
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.article-content {
  flex: 1;
  min-width: 0;
}

.article-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #2d3748;
  font-weight: 600;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #718096;
}

.article-separator {
  color: #cbd5e0;
}

.article-link-inline {
  color: #a0aec0;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s ease;
}

.article-link-inline:hover {
  color: #667eea;
  text-decoration: underline;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.pagination-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.pagination-btn:disabled {
  background: #cbd5e0;
  color: #a0aec0;
  cursor: not-allowed;
}

.pagination-info {
  color: #718096;
  font-size: 14px;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .learning-articles {
    padding: 16px;
  }

  .article-card {
    padding: 16px;
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}

/* 暗黑模式 */
body.dark-mode .learning-articles {
  background: #1a1a1a !important;
}

body.dark-mode .page-title {
  color: #ffffff !important;
}

body.dark-mode .page-description {
  color: #b0b3b8 !important;
}

body.dark-mode .article-card {
  background: #2d2d2d !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

body.dark-mode .article-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
}

body.dark-mode .article-title {
  color: #e8e8e8 !important;
}

body.dark-mode .article-meta {
  color: #b0b3b8 !important;
}

body.dark-mode .article-separator {
  color: #4c4d4f !important;
}

body.dark-mode .article-link-inline {
  color: #718096 !important;
}

body.dark-mode .article-link-inline:hover {
  color: #7c9eff !important;
}

body.dark-mode .loading-state,
body.dark-mode .empty-state {
  color: #b0b3b8 !important;
}

body.dark-mode .pagination {
  border-top-color: #4c4d4f !important;
}

body.dark-mode .pagination-info {
  color: #b0b3b8 !important;
}
</style>
