export type BacktestJobStatus = 'QUEUED' | 'RUNNING' | 'FAILED' | 'CANCELLED' | 'FINISHED';

export interface BacktestStrategyItem {
  id: string;
  created_at: string;
  updated_at: string;
  size: number;
}

export interface ListBacktestStrategiesResponse {
  strategies: BacktestStrategyItem[];
  total: number;
}

export interface BacktestJobError {
  code: string;
  message: string;
}

export interface BacktestJobParams {
  start_date: string;
  end_date: string;
  cash: number;
  benchmark: string;
  frequency: string;
}

export interface BacktestJobItem {
  job_id: string;
  strategy_id: string;
  status: BacktestJobStatus;
  error: BacktestJobError | null;
  created_at: string;
  updated_at: string;
  params: BacktestJobParams;
}

export interface ListBacktestJobsResponse {
  strategy_id: string;
  jobs: BacktestJobItem[];
  total: number;
}

export interface GetBacktestJobResponse {
  job_id: string;
  status: BacktestJobStatus;
  error: BacktestJobError | null;
  error_message?: string;
}

export interface BacktestEquity {
  dates: string[];
  nav: number[];
  returns: number[];
  benchmark_nav: number[];
}

export interface GetBacktestJobResultResponse {
  summary: Record<string, unknown>;
  equity: BacktestEquity;
  trades: Array<Record<string, unknown> | unknown[]>;
  trade_columns: string[];
  trades_total: number;
  raw_keys: string[];
}
