# HARUO — 更新ガイド v4

## ディレクトリ構成

```
portal/
├── index.html          トップページ（LP）
├── works/
│   ├── index.html      作品一覧（3カラムグリッド・タグフィルター・Randomボタン）
│   └── work.html       個別作品ページ（左画像・右情報・モーダル拡大）
├── img/                新規画像の置き場
├── data/
│   └── works.json      ★作品追加はここだけ★
├── assets/
│   ├── style.css       共通スタイル
│   └── app.js          共通JS
└── animals/            既存画像（保持）
```

## 新作追加手順

### 1. img/ に画像を追加
例: `img/sandtail_200306_01.png`

### 2. data/works.json に追記

```json
{
  "id": "sandtail",
  "title": "sandtail",
  "series": "test-tube",
  "observed": "2003-06",
  "tags": ["test-tube animals", "speculative biology", "mutation"],
  "thumbnail": "/portal/img/sandtail_200306_01.png",
  "images": ["/portal/img/sandtail_200306_01.png"],
  "description": "",
  "links": []
}
```

### 3. コミット → プッシュ → 完了

## フィールド説明

| フィールド  | 必須 | 説明                      |
|-----------|:----:|--------------------------|
| id        | ✅   | URLに使われる一意のID     |
| title     | ✅   | 作品名                    |
| series    |      | シリーズ名                |
| observed  |      | 観察日 YYYY-MM            |
| tags      | ✅   | タグ配列（絞り込みに使用） |
| thumbnail | ✅   | 一覧サムネイル            |
| images    |      | 詳細ページ画像（複数可）  |
| description |    | 説明文                    |
| links     |      | 外部リンク配列            |

## links の追加例

```json
"links": [
  { "label": "YouTube", "url": "https://youtube.com/..." },
  { "label": "note",    "url": "https://note.com/..." }
]
```

## 検索エンジン・SNS向けの静的ページ（works/）

作品を追加・変更したら、`organize_animals.py` の後にリポジトリ直下で実行する:

```
python3 tools/build_static.py
```

- `works/<作品名>/` に作品ごとのページ（画像の説明文・OGP・構造化データ付き）を書き出す
- `works/` に全作品一覧、`sitemap.xml` に画像付きサイトマップを書き出す
- 別名・画像の説明文・短い一文は `animals/test-tube/overrides.json` に書く（再生成で消えない）
