import mojimoji

from urlextract import URLExtract


def find_urls(text):
    extractor = URLExtract()
    return extractor.find_urls(text)


def share_text_to_formatted_name(text):
    return mojimoji.zen_to_han(text).lower().replace(' ', '')
    # 検索インデックスの形式 = 半角に変換して大文字は小文字にしてスペースをなくす
