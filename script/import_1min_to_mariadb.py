#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import csv
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import pymysql


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# =========================
# 默认值可被环境变量覆盖
# =========================
DATA_DIR = os.getenv("DATA_DIR", "/root/download/1min")   # 1分钟CSV根目录
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "backquant")
DB_TABLE = os.getenv("DB_TABLE", "dbbardata")
CSV_ENCODING = os.getenv("CSV_ENCODING", "utf-8")

TRUNCATE_BEFORE_IMPORT = _env_flag("TRUNCATE_BEFORE_IMPORT", False)
REPLACE_DUPLICATES = _env_flag("REPLACE_DUPLICATES", False)   # True -> REPLACE, False -> INSERT IGNORE
MIN_CONTRACT_YEAR = int(os.getenv("MIN_CONTRACT_YEAR", "2015"))
INTERVAL_VALUE = os.getenv("INTERVAL_VALUE", "1m")
PRODUCT_CODES_RAW = os.getenv("PRODUCT_CODES", "")
PRODUCT_CODES = {
    code.strip().lower()
    for code in PRODUCT_CODES_RAW.split(",")
    if code.strip()
}


# 目录里的交易所代码 -> vn.py风格交易所值
EXCHANGE_MAP: Dict[str, str] = {
    "XSGE": "SHFE",
    "SHFE": "SHFE",
    "XDCE": "DCE",
    "DCE": "DCE",
    "XZCE": "CZCE",
    "CZCE": "CZCE",
    "XINE": "INE",
    "INE": "INE",
    "CCFX": "CFFEX",
    "CFFEX": "CFFEX",
    "XGFEX": "GFEX",
    "GFEX": "GFEX",
}


@dataclass
class ContractFile:
    path: Path
    symbol: str
    product_code: str
    exchange: str
    contract_year: int


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        local_infile=True,
        autocommit=False,
        cursorclass=pymysql.cursors.Cursor,
    )


def create_main_table_if_needed(conn, table_name: str) -> None:
    sql = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        `id` BIGINT NOT NULL AUTO_INCREMENT,
        `symbol` VARCHAR(32) NOT NULL,
        `exchange` VARCHAR(16) NOT NULL,
        `datetime` DATETIME NOT NULL,
        `interval` VARCHAR(8) NOT NULL,
        `volume` DOUBLE NOT NULL DEFAULT 0,
        `turnover` DOUBLE NOT NULL DEFAULT 0,
        `open_interest` DOUBLE NOT NULL DEFAULT 0,
        `open_price` DOUBLE NOT NULL,
        `high_price` DOUBLE NOT NULL,
        `low_price` DOUBLE NOT NULL,
        `close_price` DOUBLE NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE KEY `uniq_bar` (`symbol`, `exchange`, `interval`, `datetime`),
        KEY `idx_symbol_exchange_dt` (`symbol`, `exchange`, `datetime`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()


def create_stage_table(conn, stage_table: str) -> None:
    sql = f"""
    CREATE TABLE IF NOT EXISTS `{stage_table}` (
        `symbol` VARCHAR(32) NOT NULL,
        `exchange` VARCHAR(16) NOT NULL,
        `datetime` DATETIME NOT NULL,
        `interval` VARCHAR(8) NOT NULL,
        `volume` DOUBLE NOT NULL DEFAULT 0,
        `turnover` DOUBLE NOT NULL DEFAULT 0,
        `open_interest` DOUBLE NOT NULL DEFAULT 0,
        `open_price` DOUBLE NOT NULL,
        `high_price` DOUBLE NOT NULL,
        `low_price` DOUBLE NOT NULL,
        `close_price` DOUBLE NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()


def truncate_table(conn, table_name: str) -> None:
    with conn.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE `{table_name}`;")
    conn.commit()


def extract_contract_year(symbol: str) -> Optional[int]:
    """
    从合约代码提取年份
    例如：
        FG1709 -> 2017
        rb2405 -> 2024
        IF1506 -> 2015
    """
    m = re.search(r"(\d{4})$", symbol)
    if not m:
        return None

    yymm = m.group(1)
    yy = int(yymm[:2])
    return 2000 + yy


def infer_contract_file(path: Path, data_root: Path) -> Optional[ContractFile]:
    """
    目录结构示例：
        1min/CZCE/FG/FG1709.csv

    规则：
    - exchange 从相对路径第1级目录取：CZCE
    - symbol 从文件名取：FG1709
    """
    if path.suffix.lower() != ".csv":
        return None

    try:
        rel = path.relative_to(data_root)
    except ValueError:
        return None

    parts = rel.parts
    if len(parts) < 3:
        print(f"[跳过] 路径层级不足: {path}")
        return None

    exchange_raw = parts[0].upper()
    exchange = EXCHANGE_MAP.get(exchange_raw, exchange_raw)
    product_code = parts[1].strip().lower()

    symbol = path.stem.strip()
    if not symbol:
        print(f"[跳过] 无法识别合约代码: {path}")
        return None

    contract_year = extract_contract_year(symbol)
    if contract_year is None:
        print(f"[跳过] 无法从合约代码提取年份: {path.name}")
        return None

    return ContractFile(
        path=path,
        symbol=symbol,
        product_code=product_code,
        exchange=exchange,
        contract_year=contract_year,
    )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]

    column_aliases = {
        "datetime": "date",
        "time": "date",
        "timestamp": "date",
        "amount": "money",
        "turnover": "money",
        "openinterest": "open_interest",
        "hold": "open_interest",
        "oi": "open_interest",
    }

    rename_map: Dict[str, str] = {}
    for source, target in column_aliases.items():
        if source in df.columns and target not in df.columns:
            rename_map[source] = target

    if rename_map:
        df = df.rename(columns=rename_map)

    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"缺少必要列: {missing}")

    if "money" not in df.columns:
        df["money"] = 0.0
    if "open_interest" not in df.columns:
        df["open_interest"] = 0.0

    return df


def parse_datetime_series(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()

    dt = pd.to_datetime(s, errors="coerce")
    if dt.notna().all():
        return dt

    dt2 = pd.to_datetime(s, format="%Y/%m/%d %H:%M", errors="coerce")
    mask = dt.isna() & dt2.notna()
    dt.loc[mask] = dt2.loc[mask]

    dt3 = pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    mask = dt.isna() & dt3.notna()
    dt.loc[mask] = dt3.loc[mask]

    compact_mask = dt.isna()
    if compact_mask.any():
        compact = s.loc[compact_mask].str.replace(r"\s+", " ", regex=True)

        dt4 = pd.to_datetime(compact, format="%Y%m%d %H%M%S", errors="coerce")
        mask4 = dt.isna() & dt4.notna()
        dt.loc[mask4] = dt4.loc[mask4]

        dt5 = pd.to_datetime(compact, format="%Y%m%d %H%M", errors="coerce")
        mask5 = dt.isna() & dt5.notna()
        dt.loc[mask5] = dt5.loc[mask5]

    if dt.isna().any():
        bad = s.loc[dt.isna()].head(10).tolist()
        raise ValueError(f"存在无法解析的时间，示例: {bad}")

    return dt


def build_standard_dataframe(
    df: pd.DataFrame,
    symbol: str,
    exchange: str,
) -> pd.DataFrame:
    df = normalize_columns(df)
    dt = parse_datetime_series(df["date"])

    result = pd.DataFrame({
        "symbol": symbol,
        "exchange": exchange,
        "datetime": dt.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "interval": INTERVAL_VALUE,
        "volume": pd.to_numeric(df["volume"], errors="coerce").fillna(0.0),
        "turnover": pd.to_numeric(df["money"], errors="coerce").fillna(0.0),
        "open_interest": pd.to_numeric(df["open_interest"], errors="coerce").fillna(0.0),
        "open_price": pd.to_numeric(df["open"], errors="coerce"),
        "high_price": pd.to_numeric(df["high"], errors="coerce"),
        "low_price": pd.to_numeric(df["low"], errors="coerce"),
        "close_price": pd.to_numeric(df["close"], errors="coerce"),
    })

    numeric_cols = ["open_price", "high_price", "low_price", "close_price"]
    if result[numeric_cols].isna().any().any():
        raise ValueError("OHLC 存在无法转为数值的内容")

    result = result.drop_duplicates(subset=["datetime"], keep="last")
    result = result.sort_values("datetime")
    return result


def write_temp_csv_for_load(df: pd.DataFrame) -> str:
    fd, temp_path = tempfile.mkstemp(prefix="vnpy_stage_", suffix=".csv")
    os.close(fd)

    df.to_csv(
        temp_path,
        index=False,
        header=False,
        encoding="utf-8",
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )
    return temp_path


def load_temp_csv_into_stage(conn, stage_table: str, temp_csv_path: str) -> None:
    sql = f"""
    LOAD DATA LOCAL INFILE %s
    INTO TABLE `{stage_table}`
    CHARACTER SET utf8mb4
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\\n'
    (
        `symbol`,
        `exchange`,
        `datetime`,
        `interval`,
        `volume`,
        `turnover`,
        `open_interest`,
        `open_price`,
        `high_price`,
        `low_price`,
        `close_price`
    )
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (temp_csv_path,))
    conn.commit()


def merge_stage_to_main(conn, stage_table: str, main_table: str, replace_duplicates: bool) -> int:
    verb = "REPLACE" if replace_duplicates else "INSERT IGNORE"

    sql = f"""
    {verb} INTO `{main_table}` (
        `symbol`, `exchange`, `datetime`, `interval`,
        `volume`, `turnover`, `open_interest`,
        `open_price`, `high_price`, `low_price`, `close_price`
    )
    SELECT
        `symbol`, `exchange`, `datetime`, `interval`,
        `volume`, `turnover`, `open_interest`,
        `open_price`, `high_price`, `low_price`, `close_price`
    FROM `{stage_table}`
    """
    with conn.cursor() as cursor:
        affected = cursor.execute(sql)
    conn.commit()
    return affected


def import_one_file(conn, contract_file: ContractFile) -> int:
    print(
        f"[读取] {contract_file.path} "
        f"-> symbol={contract_file.symbol}, exchange={contract_file.exchange}, year={contract_file.contract_year}"
    )

    df_raw = pd.read_csv(contract_file.path, encoding=CSV_ENCODING)
    df_std = build_standard_dataframe(df_raw, contract_file.symbol, contract_file.exchange)

    if df_std.empty:
        print(f"[跳过] {contract_file.path.name}: 无有效数据")
        return 0

    stage_table = f"{DB_TABLE}_stage"
    truncate_table(conn, stage_table)

    temp_csv_path = write_temp_csv_for_load(df_std)
    try:
        load_temp_csv_into_stage(conn, stage_table, temp_csv_path)
        affected = merge_stage_to_main(conn, stage_table, DB_TABLE, REPLACE_DUPLICATES)
    finally:
        if os.path.exists(temp_csv_path):
            os.remove(temp_csv_path)

    print(f"[写入] {contract_file.path.name}: 标准化 {len(df_std)} 条, 合并影响 {affected} 条")
    return len(df_std)


def main() -> int:
    data_dir = Path(DATA_DIR)

    if not DB_NAME:
        print("[错误] DB_NAME 为空")
        return 1
    if not DB_USER:
        print("[错误] DB_USER 为空")
        return 1

    if not data_dir.exists() or not data_dir.is_dir():
        print(f"[错误] 数据目录不存在: {data_dir}")
        return 1

    contract_files: List[ContractFile] = []

    for path in sorted(data_dir.rglob("*.csv")):
        info = infer_contract_file(path, data_dir)
        if not info:
            continue

        if info.contract_year < MIN_CONTRACT_YEAR:
            print(f"[跳过] {path.name}: 合约年份 {info.contract_year} < {MIN_CONTRACT_YEAR}")
            continue

        if PRODUCT_CODES and info.product_code not in PRODUCT_CODES:
            continue

        contract_files.append(info)

    if not contract_files:
        print(f"[错误] 在目录中未找到符合条件的 CSV: {data_dir}")
        return 1

    print(f"[配置] data_dir={data_dir}")
    print(f"[配置] mysql={DB_HOST}:{DB_PORT}/{DB_NAME} table={DB_TABLE} user={DB_USER}")
    if PRODUCT_CODES:
        print(f"[配置] product_codes={','.join(sorted(PRODUCT_CODES))}")
    print(f"[发现] 共 {len(contract_files)} 个合约文件符合条件（年份 >= {MIN_CONTRACT_YEAR}）")

    conn = get_connection()
    try:
        create_main_table_if_needed(conn, DB_TABLE)
        create_stage_table(conn, f"{DB_TABLE}_stage")

        if TRUNCATE_BEFORE_IMPORT:
            print(f"[清空] {DB_TABLE}")
            truncate_table(conn, DB_TABLE)

        total_files = 0
        total_rows = 0

        for contract_file in contract_files:
            try:
                inserted_rows = import_one_file(conn, contract_file)
                total_files += 1
                total_rows += inserted_rows
            except Exception as exc:
                conn.rollback()
                print(f"[失败] {contract_file.path}: {exc}")

        print(f"[完成] 成功处理 {total_files} 个文件，标准化导入 {total_rows} 条")
        return 0

    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
