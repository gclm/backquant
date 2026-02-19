# Jupyter 使用说明

## 安装

后端的 `requirements.txt` 已包含 Jupyter 相关依赖。推荐在后端虚拟环境内安装：

```bash
cd backtest
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 启动 Jupyter Lab

下面命令与后端 Research 模块保持一致：

```bash
jupyter lab --ip 0.0.0.0 --port 8888 --no-browser \
  --ServerApp.base_url=/jupyter \
  --ServerApp.root_dir=/home/app/backquant/backtest/research/notebooks \
  --ServerApp.token= \
  --ServerApp.password=
```

说明：
- `base_url` 必须与 `RESEARCH_NOTEBOOK_PROXY_BASE` 一致（默认 `/jupyter`）。
- `root_dir` 必须与 `RESEARCH_NOTEBOOK_ROOT_DIR` 一致。
- 如果不需要鉴权，可以设置 `--ServerApp.token=`（空字符串），但不建议用于公网。

## 后端配置

在 `backtest/.env.wsgi` 中配置（token 可空）：

```bash
RESEARCH_NOTEBOOK_ROOT_DIR='/home/app/backquant/backtest/research/notebooks'
RESEARCH_NOTEBOOK_PROXY_BASE='/jupyter'
RESEARCH_NOTEBOOK_API_BASE='http://127.0.0.1:8888/jupyter'
RESEARCH_NOTEBOOK_API_TOKEN=''
```

## systemd 服务（可选）

可创建 `/etc/systemd/system/jupyter-backtest.service`：

```ini
[Unit]
Description=BackQuant Jupyter Lab
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/home/app/backquant/backtest
Environment=JUPYTER_TOKEN=
ExecStart=/home/app/backquant/backtest/.venv/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --ServerApp.base_url=/jupyter --ServerApp.root_dir=/home/app/backquant/backtest/research/notebooks --ServerApp.token=${JUPYTER_TOKEN} --ServerApp.password=
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用与查看日志：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jupyter-backtest
sudo journalctl -u jupyter-backtest -f
```

## 示例 Notebook

示例位于：`docs/notebooks/example.ipynb`。
