# text-agent 出力の仕方（再設計）

## 大枠

output/                             # .yamlで指定された保存先フォルダ
├── yymmdd_name/                    # 案件ごとの個別フォルダ
│   ├── temp/                       # 中間ファイル（diffなど、下記に該当しないファイル）を保存
│   ├── original.txt                # Web等から取得したファイル
│   ├── original.md                 # MarkerでPDFから抽出した.md
│   ├── final.md                    # LLMで各種編集を加えた最終ファイル（現状ではMarkdown）
│   ├── original.pdf                # 抽出元となる.pdf
│   └── xxx.jpg                     # MarkerでPDFから抽出される画像ファイル。抽出・編集された.mdへのリンクを含むので、案件直下に保存（デフォでそうなってるはず）