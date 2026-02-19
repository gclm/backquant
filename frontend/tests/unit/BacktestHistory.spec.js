/* global describe, it, expect, vi, beforeEach */
import { mount } from '@vue/test-utils';
import BacktestHistory from '@/components/BacktestHistory.vue';
import {
  listStrategies,
  listStrategyJobs,
  getResult,
  getLog,
  deleteJob
} from '@/api/backtest';

vi.mock('chart.js/auto', () => {
  return {
    default: class MockChart {
      constructor() {
        // noop
      }
      destroy() {
        // noop
      }
    }
  };
});

vi.mock('@/api/backtest', () => {
  return {
    listStrategies: vi.fn(),
    listStrategyJobs: vi.fn(),
    getJob: vi.fn(),
    getResult: vi.fn(),
    getLog: vi.fn(),
    deleteJob: vi.fn()
  };
});

async function flushPromises(times = 8) {
  for (let i = 0; i < times; i += 1) {
    await Promise.resolve();
  }
}

function createJob(overrides = {}) {
  return {
    job_id: 'job-1',
    strategy_id: 'demo',
    status: 'FINISHED',
    error: null,
    created_at: '2026-02-16T10:00:00Z',
    updated_at: '2026-02-16T10:01:00Z',
    params: {
      start_date: '2026-01-01',
      end_date: '2026-01-31',
      cash: 1000000,
      benchmark: '000300.XSHG',
      frequency: '1d'
    },
    ...overrides
  };
}

async function mountPage(jobs = [createJob()]) {
  listStrategies.mockResolvedValue({
    strategies: [{ id: 'demo', created_at: '', updated_at: '', size: 1 }],
    total: 1
  });
  listStrategyJobs.mockResolvedValue({
    strategy_id: 'demo',
    jobs,
    total: jobs.length
  });
  getLog.mockResolvedValue('history log line');

  const wrapper = mount(BacktestHistory);
  await flushPromises();
  return wrapper;
}

describe('BacktestHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders jobs list after loading', async () => {
    const wrapper = await mountPage([createJob({ job_id: 'job-render-1' })]);

    const rows = wrapper.findAll('[data-testid="job-row"]');
    expect(rows).toHaveLength(1);
    expect(rows[0].text()).toContain('job-render-1');
    expect(rows[0].text()).toContain('FINISHED');
  });

  it('requests jobs with status when filter changes', async () => {
    const wrapper = await mountPage();
    listStrategyJobs.mockClear();

    await wrapper.get('[data-testid="status-filter"]').setValue('FAILED');
    await flushPromises();

    expect(listStrategyJobs).toHaveBeenCalledTimes(1);
    const [strategyId, params] = listStrategyJobs.mock.calls[0];
    expect(strategyId).toBe('demo');
    expect(params.status).toBe('FAILED');
  });

  it('shows friendly not-ready state for 409 RESULT_NOT_READY', async () => {
    getLog.mockResolvedValue('log');
    getResult.mockRejectedValue({
      response: {
        status: 409,
        data: {
          error: {
            code: 'RESULT_NOT_READY'
          }
        }
      }
    });

    const wrapper = await mountPage([createJob({ job_id: 'job-409' })]);
    await flushPromises();

    expect(getResult).toHaveBeenCalledTimes(1);
    expect(wrapper.find('[data-testid="result-not-ready"]').exists()).toBe(true);
  });

  it('deletes a job when delete is confirmed', async () => {
    getLog.mockResolvedValue('log');
    deleteJob.mockResolvedValue({ ok: true });
    listStrategyJobs
      .mockResolvedValueOnce({
        strategy_id: 'demo',
        jobs: [createJob({ job_id: 'job-del-1' })],
        total: 1
      })
      .mockResolvedValueOnce({
        strategy_id: 'demo',
        jobs: [],
        total: 0
      });

    const wrapper = mount(BacktestHistory);
    await flushPromises(20);

    await wrapper.get('.btn-danger.btn-mini').trigger('click');
    await flushPromises();
    await wrapper.get('.dialog .btn-danger').trigger('click');
    await flushPromises();

    expect(deleteJob).toHaveBeenCalledTimes(1);
    expect(deleteJob).toHaveBeenCalledWith('job-del-1');
    expect(listStrategyJobs).toHaveBeenCalledTimes(2);
  });

  it('shows job log in detail section after selecting finished job', async () => {
    getResult.mockResolvedValue({
      summary: {
        total_returns: 0.12
      },
      equity: {
        dates: ['2026-01-01'],
        nav: [1]
      },
      trades: []
    });

    const wrapper = await mountPage([createJob({ job_id: 'job-log-1' })]);
    await wrapper.get('[data-testid="job-row"]').trigger('click');
    await flushPromises();

    expect(getLog).toHaveBeenCalledWith('job-log-1');
    expect(wrapper.text()).toContain('history log line');
  });

  it('loads alias jobs for renamed strategy ids', async () => {
    localStorage.setItem('backtest_strategy_rename_map_v1', JSON.stringify({
      legacy_demo: 'demo'
    }));

    listStrategies.mockResolvedValue({
      strategies: [{ id: 'demo', created_at: '', updated_at: '', size: 1 }],
      total: 1
    });
    listStrategyJobs.mockImplementation(async (strategyId) => {
      if (strategyId === 'legacy_demo') {
        return {
          strategy_id: 'legacy_demo',
          jobs: [createJob({ job_id: 'job-legacy', strategy_id: 'legacy_demo' })],
          total: 1
        };
      }
      return {
        strategy_id: 'demo',
        jobs: [createJob({ job_id: 'job-new', strategy_id: 'demo' })],
        total: 1
      };
    });

    mount(BacktestHistory);
    await flushPromises(20);

    expect(listStrategyJobs).toHaveBeenCalledTimes(2);
    expect(listStrategyJobs).toHaveBeenCalledWith('demo', expect.any(Object));
    expect(listStrategyJobs).toHaveBeenCalledWith('legacy_demo', expect.any(Object));

    const allLimits = listStrategyJobs.mock.calls.map(([, params]) => params.limit);
    expect(allLimits.every((limit) => limit === 500)).toBe(true);
  });
});
