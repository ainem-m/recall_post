### 読み込むCSVの郵便番号のフィールド名 (ノーザでは"郵便番号")
POSTAL_CODE_COLUMN = "郵便番号"

### 氏名のフィールド名(ノーザでは"患者漢字氏名")
NAME_COLUMN = "患者漢字氏名"

### 最終来院日(ノーザでは"最終来院日")
LAST_VISIT_COLUMN = "保険最終来院日"

### 生年月日(ノーザでは"生年月日")小児かそうでないかの判定に使用します
BIRTHDAY_COLUMN = "生年月日"
### 小児かどうかを判定する年齢---この年齢未満であれば小児として扱う
PED_THRESHOLD = 12

### 住所(ノーザでは"住所")
ADDRESS_COLUMN = "住所"

### カルテ番号(ノーザでは"カルテ番号")NGリストの判定に使います
PATIENT_ID_COLUMN = "カルテ番号"
### NGリストのファイルパス
NG_LIST_PATH = "nglist.csv"

### 敬称
NAME_HONORIFIC = "様"
### リコール間隔
RECALL_INTERVAL_MONTHS = 6
PED_RECALL_INTERVAL_MONTHS = 3

### 出力先フォルダ
OUTPUT_DIR = "result"


### 参考:ノーザで全項目CSV出力した際のコラム名一覧
"""
患者カナ氏名,
患者漢字氏名,
カルテ番号,
生年月日,
年齢,
性別,
本人家族区分,
郵便番号,
住所,
電話番号,
保険区分（本人）,
保険区分（家族）,
保険区分（国保）,
保険区分（社保）,
保険区分（公費）,
保険区分（老人/後期）,
保険区分（退職者）,
保険区分（その他自費）,
保険診療開始日,
保険最終来院日,
主担当医師,
原簿コメント,
職業,
統計１,
統計２,
連絡先電話番号,
"""
