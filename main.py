# -*- coding: utf-8 -*-

import sys
import pathlib
import re
import pandas as pd
import postal_number
import datetimeutil
import datetime
import config
from typing import Optional

# Web郵便サービスに提出するCSVフォーマット
POSTAL_CODE_TOP3: str = "郵便番号上3桁"  # 郵便番号の上3桁
POSTAL_CODE_LAST4: str = "郵便番号下4桁"  # 郵便番号の下4桁
PREFECTURE: str = "都道府県名"  # 都道府県名（例: 東京都）
CITY: str = "市区町村名"  # 市区町村名（例: 千代田区）
AREA: str = "町域名"  # 町域名（例: 大手町）
ADDRESS: str = "丁目・番地等"  # 丁目・番地等（例: 1-1-1）
BUILDING: str = "アパート・ビル・マンション"  # 建物名（例: ○○ビル 101号室）
COMPANY: str = "会社名等"  # 会社名
COMPANY_HONORIFIC: str = "会社名等敬称"  # 会社名の敬称（例: 御中）
DEPARTMENT: str = "部署名等"  # 部署名
DEPARTMENT_HONORIFIC: str = "部署名等敬称"  # 部署名の敬称（例: 様）
TITLE: str = "肩書・役職等"  # 肩書や役職（例: 部長）
NAME: str = "氏名等"  # 氏名
NAME_HONORIFIC: str = "氏名等敬称"  # 氏名の敬称（例: 様）
GROUP: str = "グループ名"  # グループ名

WEB_POST_REQUIRED_FIELDS: list[str] = [
    POSTAL_CODE_TOP3,
    POSTAL_CODE_LAST4,
    PREFECTURE,
    CITY,
    AREA,
    ADDRESS,
    BUILDING,
    COMPANY,
    COMPANY_HONORIFIC,
    DEPARTMENT,
    DEPARTMENT_HONORIFIC,
    TITLE,
    NAME,
    NAME_HONORIFIC,
    GROUP,
]


def normalize_postal_code(postal_code: str) -> str:
    """
    郵便番号を標準形式に正規化する関数。

    - 入力された郵便番号を「000-0000」の形式に変換します。
    - 数字が全角の場合は半角に変換し、余分なハイフンや文字を処理します。
    - 数字以外が含まれる場合、デフォルト値「000-0000」を返します。

    Args:
        postal_code (str): 郵便番号（「000-0000」形式、または数値7桁の形式を想定）

    Returns:
        str: 標準形式「000-0000」の郵便番号。不正な入力の場合は「000-0000」を返します。

    Examples:
        >>> normalize_postal_code("000-0000")
        '000-0000'
        >>> normalize_postal_code("0000000")
        '000-0000'
        >>> normalize_postal_code("０００００００")
        '000-0000'
        >>> normalize_postal_code("０００ー００００")
        '000-0000'
    """
    # 余分な文字を削除し、全角数字を半角に変換
    postal_code = re.sub(
        r"[^\d０１２３４５６７８９]", "", postal_code
    )  # 数字以外を削除
    postal_code = postal_code.translate(
        str.maketrans("０１２３４５６７８９", "0123456789")
    )  # 全角数字→半角

    # 郵便番号が7桁の数字になればフォーマット適用
    if re.match(r"^\d{7}$", postal_code):
        return postal_code[:3] + "-" + postal_code[3:]

    # 不正な場合はデフォルト値を返す
    return "000-0000"


def save_to_csv(df: pd.DataFrame, filename: str | pathlib.Path):
    """ノーザの出力ファイルはshift_jis、外字のエラーは無視"""
    df_ = df[WEB_POST_REQUIRED_FIELDS]
    df_.to_csv(filename, index=False, encoding="shift_jis", errors="replace")


def load_csv(input_path: pathlib.Path) -> pd.DataFrame:
    return pd.read_csv(
        input_path, encoding="shift_jis", index_col=False, encoding_errors="replace"
    )


def validate_required_columns(df: pd.DataFrame):
    # 郵便番号は現状必要
    if config.POSTAL_CODE_COLUMN not in df.columns:
        print(
            f"###ERROR### {config.POSTAL_CODE_COLUMN}を含むデータを指定してください。処理続行不能ですので終了します。今後住所から補完できるように対応予定です"
        )
        print(f"現在のカラム{list(df.columns)}")
        raise ValueError
    # 住所は必要
    if config.ADDRESS_COLUMN not in df.columns:
        print(
            f"###ERROR### {config.ADDRESS_COLUMN}を含むデータを指定してください。処理続行不能ですので終了します"
        )
        print(f"現在のカラム{list(df.columns)}")
        raise ValueError

    # 患者氏名も必要
    if config.NAME_COLUMN not in df.columns:
        print(
            f"###ERROR### {config.NAME_COLUMN}を含むデータを指定してください。処理続行不能ですので終了します"
        )
        raise ValueError


def process_postal_code(df: pd.DataFrame) -> pd.DataFrame:
    df[config.POSTAL_CODE_COLUMN] = df[config.POSTAL_CODE_COLUMN].apply(
        normalize_postal_code
    )
    df[[POSTAL_CODE_TOP3, POSTAL_CODE_LAST4]] = df[config.POSTAL_CODE_COLUMN].str.split(
        "-", expand=True
    )
    return df


def exclude_ng(df: pd.DataFrame):
    if config.PATIENT_ID_COLUMN not in df.columns:
        print(
            f"{config.PATIENT_ID_COLUMN}がデータに含まれていないため、NG処理を行わず処理を続行します"
        )
        return df
    nglist = pd.read_csv(
        config.NG_LIST_PATH,
        encoding="shift_jis",
        index_col=False,
        encoding_errors="replace",
    )

    return df[~df[config.PATIENT_ID_COLUMN].isin(nglist[config.PATIENT_ID_COLUMN])]


def split_by_birthday(df: pd.DataFrame) -> tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """
    患者データを生年月日を基準に小児患者と成人患者に分割する関数。

    Args:
        df (pd.DataFrame): 入力データフレーム。生年月日列を含むことを想定。

    Returns:
        tuple[pd.DataFrame, Optional[pd.DataFrame]]:
            - 成人患者のデータフレーム
            - 小児患者のデータフレーム（存在しない場合は None）
    """
    if config.BIRTHDAY_COLUMN not in df.columns:
        # 生年月日列がない場合の処理
        print(
            "###WARNING###: 生年月日が含まれないデータを指定されたので、年齢は考慮せず処理を続行します。"
        )
        return df, None

    # 生年月日を日付型に変換（必要ならエラー処理を加える）
    df[config.BIRTHDAY_COLUMN] = df[config.BIRTHDAY_COLUMN].apply(
        datetimeutil.zenkaku_to_datetime  # 生年月日を datetime.date に変換
    )

    # 現在の日付
    current_date = datetime.datetime.now().date()

    # 年齢を計算する関数
    def calculate_age(birth_date: datetime.date) -> int:
        # 現在の日付から生年月日を引き、満年齢を計算
        age = current_date.year - birth_date.year
        # 生年月日の「月日」が現在の「月日」より後の場合、1歳引く
        if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    # 年齢列を作成
    df["AGE"] = df[config.BIRTHDAY_COLUMN].apply(calculate_age)

    # 小児患者と成人患者を分割
    df_ped = df[df["AGE"] < config.PED_THRESHOLD]
    df_adult = df[df["AGE"] >= config.PED_THRESHOLD]

    # 小児患者が存在しない場合は None を返す
    return df_adult, df_ped if not df_ped.empty else None


def filter_by_last_visit(
    df: pd.DataFrame, months: int, next_flag: int
) -> tuple[pd.DataFrame, datetime.datetime, datetime.datetime]:
    now = datetime.datetime.now()
    if config.LAST_VISIT_COLUMN not in df.columns:
        print(
            "最終来院日が含まれないデータを指定されたので、来院日は考慮せず処理を続行します。"
        )
        return df, now, now
    df[config.LAST_VISIT_COLUMN] = df[config.LAST_VISIT_COLUMN].apply(
        datetimeutil.zenkaku_to_datetime
    )
    start, end = datetimeutil.get_start_and_end_day_2(now, -months, next_flag)
    return (
        df[
            (df[config.LAST_VISIT_COLUMN] >= start)
            & (df[config.LAST_VISIT_COLUMN] <= end)
        ],
        start,
        end,
    )


def resolve_address(df):
    """住所を都道府県・市区町村名・町域名に変換、住所がない場合郵便番号から検索して埋める"""
    # if pd.isna(df[config.ADDRESS_COLUMN]):
    #     return postal_number.get_address(df[POSTAL_CODE_TOP3] + df[POSTAL_CODE_LAST4])
    return postal_number.get_postal_number(df[config.ADDRESS_COLUMN])


def convert_to_postal_format(df: pd.DataFrame) -> pd.DataFrame:
    # 読み込んだCSVにweb郵便に必要なカラムを追加
    df = df.assign(**{field: float("NaN") for field in WEB_POST_REQUIRED_FIELDS})

    # 名前を入力
    df[NAME] = df[config.NAME_COLUMN]

    # 敬称の入力
    df[NAME_HONORIFIC] = config.NAME_HONORIFIC

    # 郵便番号を正規化し、上3桁と下4桁に分割

    df = process_postal_code(df)

    # 住所の解決
    df[[PREFECTURE, CITY, AREA]] = df.apply(
        resolve_address, axis=1, result_type="expand"
    )
    return df


def create_output_dir(input_path: pathlib.Path) -> pathlib.Path:
    """
    入力パスに基づいて出力ディレクトリを作成し、そのパスを返します。

    出力ディレクトリは `config.OUTPUT_DIR` の指定された場所に作成され、現在の日付（`YYYYMMDD`）
    と入力パスのファイル名を基にサブディレクトリを作成します。

    Args:
        input_path (pathlib.Path): 入力ファイルのパス。

    Returns:
        pathlib.Path: 作成された出力ディレクトリのパス。
    """
    # 出力親ディレクトリの取得
    output_parent_dir = pathlib.Path(config.OUTPUT_DIR)

    # 出力親ディレクトリが存在しない場合は作成
    output_parent_dir.mkdir(parents=True, exist_ok=True)

    # 現在の日付をフォーマット
    now = datetime.datetime.now()
    dirname = now.strftime("%Y%m%d") + "_" + input_path.stem  # ファイル名に日付を追加

    # 出力パスを作成
    output_path = output_parent_dir / dirname

    # 出力ディレクトリが存在しない場合は作成
    output_path.mkdir(parents=True, exist_ok=True)

    return output_path


def save_debug_csv(df, df_ped, output_dir: pathlib.Path):
    if df_ped is not None:
        df = pd.concat([df, df_ped])
    debug_candidate = [
        config.NAME_COLUMN,
        config.PATIENT_ID_COLUMN,
        config.BIRTHDAY_COLUMN,
        config.LAST_VISIT_COLUMN,
        config.POSTAL_CODE_COLUMN,
        config.ADDRESS_COLUMN,
    ]
    debug_columns = [c for c in debug_candidate if c in df.columns]

    df = df[debug_columns]
    df.to_csv(
        output_dir / "debug.csv", index=False, encoding="shift_jis", errors="replace"
    )


if __name__ == "__main__":
    input_csv_path: pathlib.Path
    # 受け取るファイルのフルパス
    try:
        input_csv_path = pathlib.Path(sys.argv[1])
    except IndexError as e:
        print(
            "###ERROR### 変換するファイルを指定してください ex) python3 main.py test.txt"
        )
        print(e)
        exit()

    # オプション引数の確認
    try:
        next_flag = int(sys.argv[2])
    except IndexError:
        next_flag = 0
    except ValueError as e:
        print(e)
        print("###ERROR 第二引数next_flagは-1 ~ 1の範囲の整数にしてください")
        next_flag = 0

    # CSVデータを読み込み
    df = load_csv(input_csv_path)

    # 郵便番号と患者氏名の必須カラム確認
    validate_required_columns(df)

    # ngリストに当てはまるものを除外
    df = exclude_ng(df)

    # 生年月日が含まれるデータの場合、小児と成人を分けて処理
    df, df_ped = split_by_birthday(df)

    # 最終来院日が存在する場合、対象をしぼる
    df, adult_start, adult_end = filter_by_last_visit(
        df, config.RECALL_INTERVAL_MONTHS, next_flag
    )
    if df_ped is not None:
        df_ped, ped_start, ped_end = filter_by_last_visit(
            df_ped, config.PED_RECALL_INTERVAL_MONTHS, next_flag
        )

    # web郵便のフォーマットにする
    df = convert_to_postal_format(df)
    if df_ped is not None:
        df_ped = convert_to_postal_format(df_ped)
    # ディレクトリ作成とCSV出力
    output_dir = create_output_dir(input_csv_path)
    save_to_csv(
        df,
        output_dir
        / f"{adult_start.strftime('%Y_%m_%d')}-{adult_end.strftime('%Y_%m_%d')}.csv",
    )
    if df_ped is not None:
        save_to_csv(
            df_ped,
            output_dir
            / f"{ped_start.strftime('%Y_%m_%d')}-{ped_end.strftime('%Y_%m_%d')}_ped.csv",
        )

    # デバッグ用CSV出力
    save_debug_csv(df_ped, df, output_dir)

    # 処理結果の表示
    print(
        f"{adult_start.strftime('%Y/%m/%d')}~{adult_end.strftime('%d')}の成人患者数: {len(df)}"
    )
    if df_ped is not None:
        print(
            f"{ped_start.strftime('%Y/%m/%d')}~{ped_end.strftime('%d')}の小児患者数: {len(df_ped)}"
        )
