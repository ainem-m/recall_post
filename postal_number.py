import jusho

postman: jusho.Jusho = jusho.Jusho()


def int_to_kanji(num_: str):
    try:
        num = int(num_)
    except:
        return ""
    res = ""
    A = "十百千"
    num, rem = divmod(num, 10)
    if not (num and rem == 0):
        rem_str = str(rem).translate(
            str.maketrans("0123456789", "〇一二三四五六七八九")
        )
        res += rem_str
    for i, a in enumerate(A):
        if not num:
            break
        num, rem = divmod(num, 10)
        if num and rem == 0:
            continue
        if rem < 2:
            res += a
            continue
        rem_str = str(rem).translate(
            str.maketrans("0123456789", "〇一二三四五六七八九")
        )
        res += A[i]
        res += rem_str
    return res[::-1]


def trans_int_to_kanji(add):
    tmp = add
    ret = ""
    num = ""
    for t in tmp:
        if t.isdigit():
            num += t
            continue
        if num and not t.isdigit():
            num = int_to_kanji(num)
            ret += num
        ret += t
    return ret


def get_postal_number(address: str) -> tuple[str, str, str]:
    if type(address) is not str:
        print("nanじゃこれ", address, type(address))
        exit()
    address = address.replace("　", "")
    address = address.replace(" ", "")
    address = address.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    # 都道府県を含むかを判定、含んでいたら削除
    ind = 1
    pref = postman.search_prefectures(address[:ind])
    while True:
        # 候補が見つかる最長の文字列まで検索
        ind += 1
        pref = postman.search_prefectures(address[:ind])
        if not pref:
            ind -= 1
            pref = postman.search_prefectures(address[:ind])
            break
    if pref:
        pref = pref[0].kanji
        if pref in address:
            address = address.replace(pref, "")
    # 町域の判定
    ind = 1
    city = postman.search_cities(address[:ind])

    while True:
        ind += 1
        city = postman.search_cities(address[:ind])
        if not city or ind > len(address):
            ind -= 1
            city = postman.search_cities(address[:ind])
            break
    if not city:
        print("市区町村がみつかりません", pref, address)
        return pref if pref else "#####", "#####", address

    city = city[0]
    address = address[ind:]
    # それ以降
    address_kanji = trans_int_to_kanji(address)

    ind = 1
    add = postman.search_addresses(address_kanji[:ind], city=city)
    while True:
        ind += 1
        add = postman.search_addresses(address_kanji[:ind], city=city)
        if not add or ind > len(address_kanji):
            ind -= 1
            add = postman.search_addresses(address_kanji[:ind], city=city)
            break
    if not add:
        try:
            return pref.kanji if pref else city.prefecture.kanji, city.kanji, address
        except:
            print(
                f"住所を検索できません, add = {add} address = {address}, pref = {pref}, city = {city}"
            )
            print(f"便宜的な返り値: {city.prefecture.kanji}, {city.kanji}, {address}")
            print("この住所で処理を続行します")
            return city.prefecture.kanji, city.kanji, address
    add = add[0]
    return add.prefecture.kanji, add.city.kanji, address


def get_address(zip_code) -> jusho.Address | None:
    if zip_code == "0000000":
        return ["#####", "", ""]
    ret = postman.by_zip_code(zip_code)
    if not ret:
        print("郵便番号が存在しません")
        return ["#####郵便番号住所不明", "#####", "#####"]
    return [ret[0].prefecture.kanji, ret[0].city.kanji, ret[0].kanji + "*****"]


if __name__ == "__main__":
    address = input("郵便番号(半角数字7桁)か住所を入力してください")
    if address.isdecimal() and len(address) == 7:
        print(get_address(address))
    else:
        print(get_postal_number(address))
