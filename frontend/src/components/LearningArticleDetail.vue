<template>
  <div class="learning-article-detail">
    <div class="detail-container">
      <!-- 返回按钮 -->
      <button class="back-button" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回
      </button>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <p>加载中...</p>
      </div>

      <!-- 文章内容 -->
      <div v-else-if="article" class="article-detail">
        <div class="article-header">
          <h1 class="article-title">{{ article.title }}</h1>
          <div class="article-meta">
            <span class="article-author">{{ article.author }}</span>
            <span class="article-separator">•</span>
            <span class="article-time">{{ article.publish_time }}</span>
            <template v-if="article.url">
              <span class="article-separator">•</span>
              <a
                :href="article.url"
                target="_blank"
                rel="noopener noreferrer"
                class="article-link-inline"
              >
                原文
              </a>
            </template>
          </div>
        </div>

        <div class="article-content">
          <div
            class="markdown-content"
            v-html="renderedContent"
          ></div>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else class="error-state">
        <p>文章加载失败</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axios';
import { marked } from 'marked';
import { API_ENDPOINTS } from '@/config/api';

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: true,
  mangle: false,
  sanitize: false
});

export default {
  name: 'LearningArticleDetail',
  props: {
    articleId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      article: null,
      loading: false,
      error: null
    };
  },
  computed: {
    renderedContent() {
      if (!this.article || !this.article.content) return '';
      try {
        return marked.parse(this.article.content);
      } catch (e) {
        console.error('Markdown parsing error:', e);
        return '<p>内容解析错误</p>';
      }
    }
  },
  mounted() {
    this.fetchArticle();
  },
  methods: {
    async fetchArticle() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(API_ENDPOINTS.GET_LEARNING_ARTICLE, {
          id: this.articleId
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.data.code === 0 && response.data.data) {
          this.article = response.data.data;
        } else {
          console.error('获取文章失败:', response.data.msg);
          this.error = response.data.msg || '获取文章失败';
        }
      } catch (error) {
        console.error('获取文章失败:', error);
        this.error = '获取文章失败，请稍后重试';
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      this.$emit('go-back');
    }
  }
};
</script>

<style scoped>
.learning-article-detail {
  padding: 20px;
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f5f7fa 0%, #f8f9fb 100%);
}

.detail-container {
  max-width: 900px;
  margin: 0 auto;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 1px solid #e2e8f0;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  color: #2d3748;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 24px;
}

.back-button:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.back-button svg {
  width: 20px;
  height: 20px;
}

/* 加载和错误状态 */
.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: #718096;
  font-size: 16px;
}

/* 文章详情 */
.article-detail {
  background: white;
  border-radius: 0.75rem; /* rounded-xl */
  padding: 32px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08); /* shadow-sm */
  border: 1px solid #e5e7eb; /* border */
}

.article-header {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.article-title {
  font-size: 28px;
  color: #2d3748;
  margin: 0 0 16px 0;
  font-weight: 600;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #718096;
  margin-bottom: 16px;
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

.article-content {
  line-height: 1.8;
}

/* Markdown 内容样式 */
.markdown-content {
  color: #2d3748;
  font-size: 16px;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.markdown-content :deep(h1) {
  font-size: 28px;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 8px;
}

.markdown-content :deep(h2) {
  font-size: 24px;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 6px;
}

.markdown-content :deep(h3) {
  font-size: 20px;
}

.markdown-content :deep(h4) {
  font-size: 18px;
}

.markdown-content :deep(p) {
  margin-bottom: 16px;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin-bottom: 16px;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin-bottom: 8px;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding-left: 16px;
  margin: 16px 0;
  color: #718096;
  font-style: italic;
}

.markdown-content :deep(code) {
  background: #f7fafc;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 14px;
  font-family: 'Courier New', monospace;
  color: #e53e3e;
}

.markdown-content :deep(pre) {
  background: #f7fafc;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #2d3748;
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 24px 0;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #2d3748;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .learning-article-detail {
    padding: 16px;
  }

  .article-detail {
    padding: 24px;
  }

  .article-title {
    font-size: 24px;
  }

  .markdown-content {
    font-size: 15px;
  }

  .markdown-content :deep(h1) {
    font-size: 24px;
  }

  .markdown-content :deep(h2) {
    font-size: 20px;
  }

  .markdown-content :deep(h3) {
    font-size: 18px;
  }
}

/* 暗黑模式 */
body.dark-mode .learning-article-detail {
  background: #1a1a1a !important;
}

body.dark-mode .back-button {
  background: #2d2d2d !important;
  border-color: #4c4d4f !important;
  color: #e8e8e8 !important;
}

body.dark-mode .back-button:hover {
  background: #363636 !important;
  border-color: #5a5a5a !important;
}

body.dark-mode .back-button svg {
  stroke: #e8e8e8;
}

body.dark-mode .article-detail {
  background: #2d2d2d !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

body.dark-mode .article-header {
  border-bottom-color: #4c4d4f !important;
}

body.dark-mode .article-title {
  color: #ffffff !important;
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

body.dark-mode .markdown-content {
  color: #e8e8e8 !important;
}

body.dark-mode .markdown-content :deep(h1),
body.dark-mode .markdown-content :deep(h2),
body.dark-mode .markdown-content :deep(h3),
body.dark-mode .markdown-content :deep(h4),
body.dark-mode .markdown-content :deep(h5),
body.dark-mode .markdown-content :deep(h6) {
  color: #ffffff !important;
}

body.dark-mode .markdown-content :deep(h1) {
  border-bottom-color: #4c4d4f !important;
}

body.dark-mode .markdown-content :deep(h2) {
  border-bottom-color: #4c4d4f !important;
}

body.dark-mode .markdown-content :deep(blockquote) {
  border-left-color: #667eea !important;
  color: #b0b3b8 !important;
  background: rgba(102, 126, 234, 0.1) !important;
  padding: 12px 16px;
  border-radius: 4px;
}

body.dark-mode .markdown-content :deep(code) {
  background: #363636 !important;
  color: #f56c6c !important;
}

body.dark-mode .markdown-content :deep(pre) {
  background: #363636 !important;
}

body.dark-mode .markdown-content :deep(pre code) {
  color: #e8e8e8 !important;
}

body.dark-mode .markdown-content :deep(hr) {
  border-top-color: #4c4d4f !important;
}

body.dark-mode .markdown-content :deep(strong) {
  color: #ffffff !important;
}

body.dark-mode .markdown-content :deep(a) {
  color: #7c9eff !important;
}

body.dark-mode .loading-state,
body.dark-mode .error-state {
  color: #b0b3b8 !important;
}
</style>
