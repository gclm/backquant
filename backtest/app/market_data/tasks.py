"""Task functions for market data operations."""
import subprocess
import os
from pathlib import Path


def do_incremental_update(task_id: str):
    """Execute incremental update task."""
    from app.market_data.task_manager import get_task_manager
    from app.market_data.analyzer import analyze_bundle

    tm = get_task_manager()
    bundle_path = Path(os.environ.get('RQALPHA_BUNDLE_PATH', '/data/rqalpha/bundle'))
    db_path = Path(__file__).parent.parent.parent / "data" / "market_data.sqlite3"

    try:
        tm.update_progress(task_id, 0, 'download', '开始增量更新...')

        # Execute rqalpha update-bundle
        cmd = ['rqalpha', 'update-bundle']
        env = os.environ.copy()
        env['RQALPHA_BUNDLE_PATH'] = str(bundle_path)

        process = subprocess.Popen(
            cmd, env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Read output and update progress
        for line in process.stdout:
            tm.log(task_id, 'INFO', line.strip())
            if 'Downloading' in line:
                tm.update_progress(task_id, 50, 'download', '正在下载更新...')

        process.wait()

        if process.returncode != 0:
            raise RuntimeError(f'rqalpha update-bundle 失败，退出码: {process.returncode}')

        tm.update_progress(task_id, 100, 'download', '增量更新完成')

        # Auto-trigger analysis
        tm.log(task_id, 'INFO', '增量更新完成，自动触发数据分析')
        analyze_task_id = tm.submit_task('analyze', analyze_bundle,
                                         task_args=(bundle_path, db_path),
                                         source='auto')
        tm.log(task_id, 'INFO', f'已提交分析任务: {analyze_task_id}')

    except Exception as e:
        tm.log(task_id, 'ERROR', f'增量更新失败: {str(e)}')
        raise


def do_full_download(task_id: str):
    """Execute full download task using rqalpha download-bundle command."""
    from app.market_data.task_manager import get_task_manager
    from app.market_data.analyzer import analyze_bundle

    tm = get_task_manager()
    bundle_path = Path(os.environ.get('RQALPHA_BUNDLE_PATH', '/data/rqalpha/bundle'))
    db_path = Path(__file__).parent.parent.parent / "data" / "market_data.sqlite3"

    try:
        # Clear existing bundle directory
        tm.update_progress(task_id, 0, 'download', '准备下载环境...')
        tm.log(task_id, 'INFO', f'清理现有 bundle 目录: {bundle_path}')

        if bundle_path.exists():
            import shutil
            shutil.rmtree(bundle_path)
        bundle_path.mkdir(parents=True, exist_ok=True)

        # Use rqalpha download-bundle command
        tm.update_progress(task_id, 10, 'download', '开始下载数据包...')
        tm.log(task_id, 'INFO', '使用 rqalpha download-bundle 命令下载')

        # Determine bundle parent directory
        bundle_parent = bundle_path.parent

        cmd = ['rqalpha', 'download-bundle', '-d', str(bundle_parent)]
        env = os.environ.copy()
        env['RQALPHA_BUNDLE_PATH'] = str(bundle_path)

        process = subprocess.Popen(
            cmd, env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Read output and update progress
        for line in process.stdout:
            line = line.strip()
            if line:
                tm.log(task_id, 'INFO', line)
                if 'Downloading' in line or 'downloading' in line:
                    tm.update_progress(task_id, 50, 'download', '正在下载数据包...')
                elif 'Extracting' in line or 'extracting' in line:
                    tm.update_progress(task_id, 80, 'download', '正在解压数据包...')

        process.wait()

        if process.returncode != 0:
            raise RuntimeError(f'rqalpha download-bundle 失败，退出码: {process.returncode}')

        tm.update_progress(task_id, 100, 'download', '下载完成')
        tm.log(task_id, 'INFO', '数据包下载完成')

        # Auto-trigger analysis
        tm.log(task_id, 'INFO', '自动触发数据分析')
        analyze_task_id = tm.submit_task('analyze', analyze_bundle,
                                         task_args=(bundle_path, db_path),
                                         source='auto')
        tm.log(task_id, 'INFO', f'已提交分析任务: {analyze_task_id}')

    except Exception as e:
        tm.log(task_id, 'ERROR', f'全量下载失败: {str(e)}')
        raise
