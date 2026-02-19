<template>
  <div class="overlay" @click.self="handleClose">
    <div class="modal">
      <div class="modal-header">
        <div class="title">
          <h3>回测参数</h3>
          <span class="sub">确认参数后将创建回测任务并跳转结果页。</span>
        </div>
        <button class="icon-btn" type="button" @click="handleClose">×</button>
      </div>

      <div class="modal-body">
        <div class="grid">
          <div class="field">
            <label>开始日期</label>
            <input v-model="form.start_date" class="text-input" type="date">
          </div>
          <div class="field">
            <label>结束日期</label>
            <input v-model="form.end_date" class="text-input" type="date">
          </div>

          <div class="field">
            <label>初始资金</label>
            <input v-model="form.cash" class="text-input" type="number" min="0" step="1000" placeholder="例如：1000000">
          </div>

          <div class="field">
            <label>基准</label>
            <input v-model.trim="form.benchmark" class="text-input" type="text" placeholder="例如：000300.XSHG">
          </div>

          <div class="field">
            <label>频率</label>
            <select v-model="form.frequency" class="text-input">
              <option value="1d">日频（1d）</option>
              <option value="1m">分钟（1m）</option>
            </select>
          </div>
        </div>

        <div class="note">
          <div class="note-title">说明</div>
          <ul>
            <li>字段以现有后端接口 <span class="mono">POST /api/backtest/run</span> 支持为准。</li>
            <li v-if="warning" class="warn">{{ warning }}</li>
          </ul>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" type="button" @click="handleClose">取消</button>
        <button class="btn btn-primary" type="button" :disabled="submitting" @click="handleConfirm">
          {{ submitting ? '提交中...' : '开始回测' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
function formatDate(date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export default {
  name: 'BacktestParamModal',
  props: {
    submitting: {
      type: Boolean,
      default: false
    },
    defaultParams: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close', 'confirm'],
  data() {
    const today = new Date();
    const start = new Date(today);
    start.setMonth(start.getMonth() - 3);
    const defaults = {
      start_date: formatDate(start),
      end_date: formatDate(today),
      cash: 1000000,
      benchmark: '000300.XSHG',
      frequency: '1d'
    };

    return {
      form: {
        ...defaults,
        ...(this.defaultParams || {})
      },
      warning: ''
    };
  },
  methods: {
    handleClose() {
      this.$emit('close');
    },
    normalizeAndValidate() {
      const start = String(this.form.start_date || '').trim();
      const end = String(this.form.end_date || '').trim();
      const cash = Number(this.form.cash);
      const benchmark = String(this.form.benchmark || '').trim();
      const frequency = String(this.form.frequency || '').trim();

      if (!start || !end) {
        return { ok: false, message: '请填写开始/结束日期' };
      }
      if (start > end) {
        return { ok: false, message: '开始日期不能晚于结束日期' };
      }
      if (!Number.isFinite(cash) || cash <= 0) {
        return { ok: false, message: '初始资金需为正数' };
      }
      if (!frequency) {
        return { ok: false, message: '请选择频率' };
      }

      return {
        ok: true,
        params: {
          start_date: start,
          end_date: end,
          cash,
          benchmark,
          frequency
        }
      };
    },
    handleConfirm() {
      const validated = this.normalizeAndValidate();
      if (!validated.ok) {
        this.warning = validated.message;
        return;
      }
      this.warning = '';
      this.$emit('confirm', validated.params);
    }
  }
};
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 9998;
}

.modal {
  width: 100%;
  max-width: 720px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 18px 55px rgba(0, 0, 0, 0.22);
  overflow: hidden;
  border: 1px solid rgba(223, 231, 242, 0.85);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  background: #f6faff;
  border-bottom: 1px solid #ebeef5;
}

.title h3 {
  margin: 0;
  font-size: 16px;
}

.sub {
  display: inline-block;
  margin-top: 6px;
  font-size: 12px;
  color: #5f6f86;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  background: #fff;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  color: #334155;
}

.modal-body {
  padding: 14px 16px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 12px;
  color: #606266;
  font-weight: 600;
}

.text-input {
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 14px;
  background: #fff;
}

.text-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.12);
}

.note {
  margin-top: 12px;
  border: 1px solid #eef2f7;
  border-radius: 12px;
  background: #f8fafc;
  padding: 10px 12px;
  color: #475569;
  font-size: 12px;
}

.note-title {
  font-weight: 800;
  margin-bottom: 6px;
  color: #0f172a;
}

.note ul {
  margin: 0;
  padding-left: 18px;
}

.warn {
  color: #b45309;
  font-weight: 700;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
}

.modal-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
}

.btn {
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #1f2937;
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #1f6feb;
  border-color: #1f6feb;
  color: #fff;
}
</style>

