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
    import tempfile
    import shutil

    tm = get_task_manager()
    bundle_path = Path(os.environ.get('RQALPHA_BUNDLE_PATH', '/data/rqalpha/bundle'))
    db_path = Path(__file__).parent.parent.parent / "data" / "market_data.sqlite3"
    temp_dir = None

    try:
        # Use temporary directory for download (similar to docker-entrypoint.sh)
        tm.update_progress(task_id, 0, 'download', '准备下载环境...')
        temp_dir = tempfile.mkdtemp(prefix='rqalpha-bundle-')
        tm.log(task_id, 'INFO', f'使用临时目录: {temp_dir}')

        # Download to temporary directory
        tm.update_progress(task_id, 10, 'download', '开始下载数据包...')
        tm.log(task_id, 'INFO', '使用 rqalpha download-bundle 命令下载')

        cmd = ['rqalpha', 'download-bundle', '-d', temp_dir]
        env = os.environ.copy()

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
                    tm.update_progress(task_id, 70, 'download', '正在解压数据包...')

        process.wait()

        if process.returncode != 0:
            raise RuntimeError(f'rqalpha download-bundle 失败，退出码: {process.returncode}')

        # Copy from temp directory to target bundle path
        tm.update_progress(task_id, 80, 'download', '正在复制数据...')
        temp_bundle = Path(temp_dir) / 'bundle'

        if not temp_bundle.exists():
            raise RuntimeError(f'下载的 bundle 目录不存在: {temp_bundle}')

        # Clear target directory contents
        tm.log(task_id, 'INFO', f'清理目标目录: {bundle_path}')
        if bundle_path.exists():
            for item in bundle_path.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            bundle_path.mkdir(parents=True, exist_ok=True)

        # Copy files from temp to target
        tm.log(task_id, 'INFO', f'复制文件到: {bundle_path}')
        for item in temp_bundle.iterdir():
            dest = bundle_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

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
    finally:
        # Clean up temporary directory
        if temp_dir and Path(temp_dir).exists():
            try:
                shutil.rmtree(temp_dir)
                tm.log(task_id, 'INFO', f'已清理临时目录: {temp_dir}')
            except Exception as e:
                tm.log(task_id, 'WARNING', f'清理临时目录失败: {str(e)}')
