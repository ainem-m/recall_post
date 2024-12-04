import datetime
import calendar


def zenkaku_to_datetime(zenkaku_date: str) -> datetime.datetime:
    # 全角の数字を半角に変換する辞書
    zenkaku_to_hankaku = {
        "０": "0",
        "１": "1",
        "２": "2",
        "３": "3",
        "４": "4",
        "５": "5",
        "６": "6",
        "７": "7",
        "８": "8",
        "９": "9",
    }
    # 全角の日付を半角に変換する
    hankaku_date = ""
    for c in zenkaku_date:
        if c in zenkaku_to_hankaku.keys():
            hankaku_date += zenkaku_to_hankaku[c]
        elif c.isspace():
            continue
        elif c in "年月日":
            hankaku_date += c
    # 半角の日付をdatetime.datetime型に変換する
    return datetime.datetime.strptime(hankaku_date, "%Y年%m月%d日")


def get_start_and_end_day(
    now: datetime.datetime, months: int, next=False
) -> tuple[datetime.datetime, datetime.datetime]:
    """現在の日付と何ヶ月前の日付が必要かを受け取り、対象の日付を返す

    Args:
        now (datetime.datetime): 現在の日付
        months (int): 何ヶ月前か
        next (bool, optional): 次の日付にするかどうか. Defaults to False.

    Returns:
        tuple[datetime.datetime, datetime.datetime]: _description_
    """
    # 0-indexにしてMOD12で扱えるようにする
    month = now.month - 1
    year = now.year
    month -= months
    if month < 0:
        year -= 1
    month %= 12
    if now.day < 4:
        start_day = 11 if not next else 21
        end_day = 20 if not next else 31
    elif 4 <= now.day < 14:
        start_day = 21 if not next else 1
        end_day = 31 if not next else 10
        if next:
            month += 1
            month %= 12
    elif 14 <= now.day < 26:
        start_day = 1 if not next else 11
        end_day = 10 if not next else 20
        month += 1
        month %= 12
    elif 26 <= now.day:
        start_day = 11 if not next else 21
        end_day = 20 if not next else 31
        month += 1
        month %= 12
    # 1-indexになおす
    month += 1
    start = datetime.datetime(year, month, start_day)
    done = False
    while not done:
        try:
            # 31日までない月だとエラー もしくは閏年でない2月で29日だとエラー
            end = datetime.datetime(year, month, end_day)
            done = True
        except ValueError:
            # エラー出たら30日にする
            end_day -= 1
    return start, end


def month_delta(now: datetime.datetime, months: int) -> datetime.datetime:
    month = now.month
    month += months
    year = now.year
    if month <= 0:
        month += 12
        year -= 1
    elif month > 12:
        month -= 12
        year += 1
    return datetime.datetime(year=year, month=month, day=now.day)


def get_start_and_end_day_2(
    now: datetime.datetime, months: int, next: int = 0
) -> tuple[datetime.datetime, datetime.datetime]:
    """
    指定された日付に基づき、開始日と終了日を計算し、返します。

    基準日（`now`）が月の上旬、中旬、下旬に応じて、それに対応する開始日と終了日を決定します。
    また、`next=True` が指定された場合、計算を次の月に基づいて行います。

    Args:
        now (datetime.datetime): 現在の日付（基準日）。
        months (int): 基準日から加算する月数。
        next (bool, optional): 次の月を計算する場合は `True` を指定します。デフォルトは `False`。

    Returns:
        tuple[datetime.datetime, datetime.datetime]: 計算された開始日（`start`）と終了日（`end`）をタプルで返します。

    Notes:
        - 基準日（`now`）の日付によって、上旬（1-10日）、中旬（11-20日）、下旬（21-31日）に分類し、
          それぞれの範囲に基づいて開始日と終了日を設定します。
        - `next=True` が指定された場合、次の月の基準日を計算します。
        - 月末日は 31日またはその月の最終日になる場合があります。

    Example:
        >>> get_start_and_end_day_2(datetime.datetime(2024, 12, 5), 1)
        (datetime.datetime(2025, 1, 1), datetime.datetime(2025, 1, 10))
    """
    # 月ごとの上旬、中旬、下旬を定義
    start_end_delta = [
        (1, 10, 0),
        (11, 20, 0),
        (21, 31, 0),
        (1, 10, 1),
        (11, 20, 1),
        (21, 31, 1),
    ]

    # 現在の日付（now）から、上旬、中旬、下旬を決定
    day = now.day
    ind = 1
    if day < 4:
        ind = 1  # 上旬
    elif day < 14:
        ind = 2  # 中旬
    elif day < 26:
        ind = 3  # 下旬
    else:
        ind = 4  # 下旬
    ind += next  # 次の月の場合、インデックスを調整

    # 開始日と終了日を決定するためのdelta調整
    start_day, end_day, delta = start_end_delta[ind]
    months += delta

    # 基準日を月数分加算
    now = month_delta(now, months)

    # 開始日と終了日を設定
    start = datetime.datetime(year=now.year, month=now.month, day=start_day)
    if end_day == 31:
        # 月末日が31日であれば、その月の最終日を使用
        end_day = calendar.monthrange(start.year, start.month)[1]
    end = datetime.datetime(year=now.year, month=now.month, day=end_day)

    return start, end


if __name__ == "__main__":
    now = input("yymmdd: ")
    now = datetime.datetime.strptime(now, "%y%m%d")
    print(f"now= {now}")
    start, end = get_start_and_end_day_2(now, -6)
    print(f"{start}\nto\n{end}")
