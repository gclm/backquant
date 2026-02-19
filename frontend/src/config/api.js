// 支持运行时配置（public/config.js）与构建时环境变量
const runtimeBase =
  typeof window !== 'undefined' &&
  window.__APP_CONFIG__ &&
  window.__APP_CONFIG__.API_BASE_URL
    ? window.__APP_CONFIG__.API_BASE_URL
    : '';
const envBase = process.env.VUE_APP_API_BASE || '';
// 默认空字符串表示同域（通过反向代理转发 /api）
export const API_BASE_URL = runtimeBase || envBase || '';

export const API_ENDPOINTS = {
  SMALL: `${API_BASE_URL}/api/small`,
  SMALL_REAL_HQ: `${API_BASE_URL}/api/small_real_hq`,
  ETF: `${API_BASE_URL}/api/etf`,
  STAT: `${API_BASE_URL}/api/stat`,
  CONTINUOUS: `${API_BASE_URL}/api/continuous`,
  MAX_ETF: `${API_BASE_URL}/api/max_etf`,
  QUERY_SIMILAR_ETF: `${API_BASE_URL}/api/query_similar_etf`,
  GET_ETF_HQ: `${API_BASE_URL}/api/get_etf_hq`,
  GET_ETFS: `${API_BASE_URL}/api/get_etfs`,
  ETF_ARBITRAGE: `${API_BASE_URL}/api/etf_arbitrage`,
  MOVE_WEEK_LINE: `${API_BASE_URL}/api/move_week_line`,
  DAMA: `${API_BASE_URL}/api/dama`,
  DAMA_LOG: `${API_BASE_URL}/api/dama_log`,
  MARKET_WIDTH: `${API_BASE_URL}/api/market_width`,
  SCAN: `${API_BASE_URL}/api/scan`,
  BIG_OR_SMALL: `${API_BASE_URL}/api/big_or_small`,
  AI_SUMMARY: `${API_BASE_URL}/api/ai_summary`,
  OVERBUY: `${API_BASE_URL}/api/get_overbuy`,
  NNG: `${API_BASE_URL}/api/nng`,
  REAL_NNG_HQ: `${API_BASE_URL}/api/real_nng_hq`,
  ADJUST_LOG: `${API_BASE_URL}/api/adjust_log`,
  MIN_HQ: `${API_BASE_URL}/api/min_hq`,
  TREND_SIGNAL: `${API_BASE_URL}/api/trend_signal`,
  SPEC_TREND_SIGNAL: `${API_BASE_URL}/api/spec_trend_signal`,
  ALL_CODE_MIN: `${API_BASE_URL}/api/all_code_min`,
  SPEC_MIN_HQ: `${API_BASE_URL}/api/spec_min_hq`,
  OVER_OVERBUY: `${API_BASE_URL}/api/over_overbuy`,
  LOGIN: `${API_BASE_URL}/api/login`,
  POSITION_INFO: `${API_BASE_URL}/api/position_info`,
  ACCOUNT_INFO: `${API_BASE_URL}/api/account_info`,
  MARKET_VOL_WIDTH: `${API_BASE_URL}/api/market_vol_width`,
  DYNAMIC_MOM: `${API_BASE_URL}/api/dynamic_mom`,
  DAILY_REAL_MOM: `${API_BASE_URL}/api/daily_real_mom`,
  WX_ARTICLES: `${API_BASE_URL}/api/wx_articals`,
  LEARNING_ARTICLES: `${API_BASE_URL}/api/learning_articles`,
  GET_LEARNING_ARTICLE: `${API_BASE_URL}/api/get_learning_article`,
  GET_ETF_DAY_SUMMARY: `${API_BASE_URL}/api/get_etf_day_summary`,
  GET_LATEST_CLEAR: `${API_BASE_URL}/api/get_latest_clear`,
  GET_PREMIUM_ETF: `${API_BASE_URL}/api/get_premium_etf`,
  GET_COCKPIT: `${API_BASE_URL}/api/get_cockpit`,
  GET_DAILY_STAT: `${API_BASE_URL}/api/get_daily_stat`,
  GET_TRADE_INFO: `${API_BASE_URL}/api/get_trade_info`
};
