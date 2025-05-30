このディレクトリは、論文の補足として、評価用データの準備方法に関する詳細を記載しています。これにより、実験の再現が容易になります。

## 英語のみの短文データセット

### LibriSpeech

[LibriSpeech ASRコーパス](https://www.openslr.org/12)のtest-cleanおよびtest-otherスプリットを使用しました。

### TED-LIUM 3

[TED-LIUM Release 3](https://www.openslr.org/51/)のテストスプリットを使用し、リリースに含まれるセグメント化された手動転写を利用しました。

### Common Voice 5.1

[公式ウェブサイト](https://commonvoice.mozilla.org/en/datasets)からCommon Voice Corpus 5.1の英語サブセットをダウンロードしました。

### Artie

[Artie bias corpus](https://github.com/artie-inc/artie-bias-corpus)を使用しました。これはCommon Voiceデータセットのサブセットです。

### CallHome & Switchboard

[LDC2002S09](https://catalog.ldc.upenn.edu/LDC2002S09)および[LDC2002T43](https://catalog.ldc.upenn.edu/LDC2002T43)の2つのコーパスを使用し、前処理には[eval2000_data_prep.sh](https://github.com/kaldi-asr/kaldi/blob/master/egs/fisher_swbd/s5/local/eval2000_data_prep.sh)スクリプトに従いました。`wav.scp`ファイルは、以下のbashコマンドでWAVファイルに変換できます。

```bash
mkdir -p wav
while read name cmd; do
    echo $name
    echo ${cmd/\|/} wav/$name.wav | bash
done < wav.scp
```
### WSJ

[LDC93S6B](https://catalog.ldc.upenn.edu/LDC93S6B) および [LDC94S13B](https://catalog.ldc.upenn.edu/LDC94S13B) を使用し、[s5レシピ](https://github.com/kaldi-asr/kaldi/tree/master/egs/wsj/s5)に従ってデータセットを前処理しました。

### CORAAL

[CORAAL (v. 2021.07)](https://oraal.uoregon.edu/coraal) の231件のインタビューを使用し、[FairSpeechプロジェクト](https://github.com/stanford-policylab/asr-disparities/blob/master/input/CORAAL_transcripts.csv)のセグメンテーションを利用しました。

### CHiME-6

[CHiME-5データセット](https://spandh.dcs.shef.ac.uk//chime_challenge/CHiME5/download.html)をダウンロードし、[s5_track1レシピ](https://github.com/kaldi-asr/kaldi/tree/master/egs/chime6/s5_track1)のstage 0に従って同期を修正したCHiME-6データセットを作成しました。その後、バイノーラル録音（`*_P??.wav`）と対応する転写を使用しました。

### AMI-IHM, AMI-SDM1

[AMIコーパス](https://groups.inf.ed.ac.uk/ami/corpus/overview.shtml)を、[s5bレシピ](https://github.com/kaldi-asr/kaldi/tree/master/egs/ami/s5b)のstage 0および2に従って前処理しました。


## 英語長文データセット

### TED-LIUM 3

[TED-LIUM3](https://www.openslr.org/51/) データセットから長文転写データセットを作成するため、各トークの最初のラベル付きセグメントの開始から最後のラベル付きセグメントの終了までの音声を切り出し、テキストを連結してラベルとしました。テストスプリットに含まれる11件のTEDトークについて、切り出しに使用したタイムスタンプは以下の通りです。

| ファイル名              | 開始時刻 (秒)   | 終了時刻 (秒)   |
|------------------------|----------------|----------------|
| DanBarber_2010         | 16.09          | 1116.24        |
| JaneMcGonigal_2010     | 15.476         | 1187.61        |
| BillGates_2010         | 15.861         | 1656.94        |
| TomWujec_2010U         | 16.26          | 402.17         |
| GaryFlake_2010         | 16.06          | 367.14         |
| EricMead_2009P         | 18.434         | 536.44         |
| MichaelSpecter_2010    | 16.11          | 979.312        |
| DanielKahneman_2010    | 15.8           | 1199.44        |
| AimeeMullins_2009P     | 17.82          | 1296.59        |
| JamesCameron_2010      | 16.75          | 1010.65        |
| RobertGupta_2010U      | 16.8           | 387.03         |

### Meanwhile

このデータセットは「The Late Show with Stephen Colbert」から64セグメントで構成されています。YouTubeの動画ID、開始・終了タイムスタンプ、ラベルは [meanwhile.json](meanwhile.json) に記載されています。ラベルは各動画のクローズドキャプションデータから収集し、手動で確認・修正しています。

### Rev16

[Rev.AIのPodcast Transcription Benchmark](https://www.rev.ai/blog/podcast-transcription-benchmark-part-1/)に含まれる30エピソードのうち、音声とラベルが大きく一致しない（主にスポンサー紹介部分）ケースが複数見つかったため、それらの問題がない16ファイルのみを使用しました。選択したエピソードの「file number」は以下の通りです。

    3 4 9 10 11 14 17 18 20 21 23 24 26 27 29 32

### Kincaid46

このデータセットは、Jason Kincaidによるブログ記事 [Which automatic transcription service is the most accurate - 2018](https://medium.com/descript/which-automatic-transcription-service-is-the-most-accurate-2018-2e859b23ed19) でまとめられた46の音声ファイルと対応する転写から構成されています。記事内のAirtableウィジェットから音声ファイルと参照転写を取得しました。

論文中の人手転写ベンチマークでは、このデータから25例をサブセットとして使用しました。該当する「Ref ID」は以下の通りです。

    2 4 5 8 9 10 12 13 14 16 19 21 23 25 26 28 29 30 33 35 36 37 42 43 45

### Earnings-21, Earnings-22

これらのデータセットについては、[speech-datasetsリポジトリ](https://github.com/revdotcom/speech-datasets)（`202206`バージョン）で公開されているファイルを使用しました。

### CORAAL

[CORAAL (v. 2021.07)](https://oraal.uoregon.edu/coraal) の231件のインタビューを使用し、全長のインタビューファイルと転写を利用しました。


## 多言語データセット

### Multilingual LibriSpeech

[Multilingual LibriSpeech (MLS) コーパス](https://www.openslr.org/94/)の各言語のテストスプリットを使用しました。

### Fleurs

[HuggingFace datasets](https://huggingface.co/datasets/google/fleurs/blob/main/fleurs.py) で提供されている実装を用いて音声ファイルと転写を収集しました。翻訳データセットとして利用するため、数値の発話IDを一致させて対応する英語転写を取得しました。

### VoxPopuli

[公式リポジトリ](https://github.com/facebookresearch/voxpopuli)の `get_asr_data.py` スクリプトを用いて、14言語のASRデータを収集しました。

### Common Voice 9

[公式ウェブサイト](https://commonvoice.mozilla.org/en/datasets)からCommon Voice Corpus 9をダウンロードしました。

### CoVOST 2

[公式リポジトリ](https://github.com/facebookresearch/covost)を用いて収集された `X into English` データを利用しました。
