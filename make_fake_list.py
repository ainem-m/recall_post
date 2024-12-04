import pandas as pd
import random
import faker
from datetime import datetime, timedelta

# ダミーデータ生成に使用するライブラリ
fake = faker.Faker("ja_JP")


# 半角を全角に変換する関数
def to_full_width(text):
    return text.translate(
        str.maketrans(
            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ",
        )
    )


# 診療の開始日と最終来院日を2024年内でランダムに設定
def generate_random_date(start_year=2024):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(start_year, 12, 31)
    return start_date + (end_date - start_date) * random.random()


# 1人分のダミーデータを生成する関数
def generate_patient_data():
    # ランダムな日付（最終来院日）
    last_visit_date = generate_random_date()

    # ランダムに患者データを生成
    patient_data = {
        "患者カナ氏名": fake.name(),
        "患者漢字氏名": fake.name(),
        "カルテ番号": f"{random.randint(10000, 99999)}",  # ランダムなカルテ番号
        "生年月日": fake.date_of_birth(minimum_age=2, maximum_age=89).strftime(
            "%Y年 %m月 %d日"
        ),
        "年齢": random.randint(18, 99),
        "性別": random.choice(["男", "女"]),
        "本人家族区分": random.choice(["本人", "家族"]),
        "郵便番号": fake.zipcode(),
        "住所": fake.address().replace("\n", " "),  # 改行を削除
        "電話番号": fake.phone_number(),
        "保険区分（本人）": random.choice(
            [None, "国保", "社保", "公費", "老人/後期", "退職者", "その他自費"]
        ),
        "保険区分（家族）": random.choice([None, "家族"]),
        "保険区分（国保）": random.choice([None, "国保"]),
        "保険区分（社保）": random.choice([None, "社保"]),
        "保険区分（公費）": random.choice([None, "公費"]),
        "保険区分（老人/後期）": random.choice([None, "老人/後期"]),
        "保険区分（退職者）": random.choice([None, "退職者"]),
        "保険区分（その他自費）": random.choice([None, "その他自費"]),
        "保険診療開始日": fake.date_this_decade().strftime("%Y年 %m月 %d日"),
        "保険最終来院日": last_visit_date.strftime("%Y年 %m月 %d日"),
        "主担当医師": fake.name(),
        "原簿コメント": "",
        "職業": fake.job(),
        "統計１": random.randint(1, 100),
        "統計２": random.randint(1, 100),
        "連絡先電話番号": fake.phone_number(),
    }

    # 生年月日、最終来院日など、全角数字に変換したい項目を全角に変換
    patient_data["生年月日"] = to_full_width(patient_data["生年月日"])
    patient_data["保険診療開始日"] = to_full_width(patient_data["保険診療開始日"])
    patient_data["保険最終来院日"] = to_full_width(patient_data["保険最終来院日"])

    return patient_data


# 生成する患者数
num_patients = 1000  # ここでは10人分のダミーデータを生成

# ダミーデータをリストに保存
patients_data = [generate_patient_data() for _ in range(num_patients)]

# DataFrameに変換
df = pd.DataFrame(patients_data)

# CSVファイルとして保存
df.to_csv("dummy_patient_data.csv", index=False, encoding="shift_jis")

# データ確認
print(df.head())
