# Whisper（ウィスパー）

[[ブログ]](https://openai.com/blog/whisper)
[[論文]](https://arxiv.org/abs/2212.04356)
[[モデルカード]](https://github.com/openai/whisper/blob/main/model-card.md)
[[Colab例]](https://colab.research.google.com/github/openai/whisper/blob/master/notebooks/LibriSpeech.ipynb)

Whisperは汎用の音声認識モデルです。多様な音声データセットで学習されており、多言語音声認識、音声翻訳、言語識別などのマルチタスクもこなせます。

## アプローチ

![アプローチ](https://raw.githubusercontent.com/openai/whisper/main/approach.png)

Transformerのシーケンス・ツー・シーケンスモデルを、多言語音声認識、音声翻訳、話し言葉の言語識別、音声活動検出など、様々な音声処理タスクで学習しています。これらのタスクは、デコーダーが予測するトークン列として統一的に表現され、従来の音声処理パイプラインの多くの段階を1つのモデルで置き換えることができます。マルチタスク学習形式では、タスク指定や分類ターゲットとなる特別なトークンを使用します。

## セットアップ

私たちはPython 3.9.9と [PyTorch](https://pytorch.org/) 1.10.1でモデルの学習とテストを行いましたが、コードベースはPython 3.8-3.11および最近のPyTorchバージョンと互換性があると想定しています。また、[OpenAIのtiktoken](https://github.com/openai/tiktoken)など、いくつかのPythonパッケージに依存しています。Whisperの最新版は以下のコマンドでインストールまたはアップデートできます。

    pip install -U openai-whisper

または、以下のコマンドでこのリポジトリの最新コミットと依存パッケージをインストールできます。

    pip install git+https://github.com/openai/whisper.git 

パッケージをこのリポジトリの最新版にアップデートするには、次のコマンドを実行してください。

    pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git

It also requires the command-line tool [`ffmpeg`](https://ffmpeg.org/) to be installed on your system, which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```

プラットフォーム向けに [tiktoken](https://github.com/openai/tiktoken) のプリビルドホイールが提供されていない場合は、[`rust`](http://rust-lang.org) のインストールが必要になることがあります。上記の `pip install` コマンド実行時にインストールエラーが発生した場合は、[Getting startedページ](https://www.rust-lang.org/learn/get-started) を参考にRust開発環境をインストールしてください。また、`PATH` 環境変数の設定（例: `export PATH="$HOME/.cargo/bin:$PATH"`）が必要な場合もあります。もし `No module named 'setuptools_rust'` というエラーでインストールに失敗した場合は、`setuptools_rust` をインストールする必要があります（例: 以下のコマンドを実行してください）。

```bash
pip install setuptools-rust
```


## 利用可能なモデルと対応言語

Whisperには6種類のモデルサイズがあり、そのうち4つは英語専用バージョンも用意されています。これらは速度と精度のトレードオフを提供します。
以下の表は、利用可能なモデル名と、それぞれの大まかなメモリ要件、およびlargeモデルに対する推論速度の相対値を示しています。
相対速度はA100上で英語音声を文字起こしした際のものであり、実際の速度は言語や話速、ハードウェアなど多くの要因によって大きく異なる場合があります。

|  サイズ  | パラメータ数 | 英語専用モデル | 多言語モデル | 必要VRAM | 相対速度 |
|:------:|:----------:|:------------------:|:------------------:|:-------------:|:--------------:|
|  tiny  |    39 M    |     `tiny.en`      |       `tiny`       |     ~1 GB     |      ~10倍      |
|  base  |    74 M    |     `base.en`      |       `base`       |     ~1 GB     |      ~7倍       |
| small  |   244 M    |     `small.en`     |      `small`       |     ~2 GB     |      ~4倍       |
| medium |   769 M    |    `medium.en`     |      `medium`      |     ~5 GB     |      ~2倍       |
| large  |   1550 M   |        該当なし    |      `large`       |    ~10 GB     |       1倍       |
| turbo  |   809 M    |        該当なし    |      `turbo`       |     ~6 GB     |      ~8倍       |

英語専用の `.en` モデルは、特に `tiny.en` や `base.en` で精度が高い傾向があります。`small.en` や `medium.en` ではその差は小さくなります。
また、`turbo` モデルは `large-v3` を最適化したもので、精度の低下を最小限に抑えつつ、より高速な文字起こしが可能です。

Whisperの性能は言語によって大きく異なります。下図は、Common Voice 15およびFleursデータセットで評価した際の、`large-v3` および `large-v2` モデルの言語ごとの性能（WER: 単語誤り率、CER: 文字誤り率（*イタリック*で表示））を示しています。他モデルやデータセットに対応する追加のWER/CER指標は[論文](https://arxiv.org/abs/2212.04356)の付録D.1, D.2, D.4に、翻訳のBLEUスコアは付録D.3に掲載されています。

![言語ごとのWER内訳](https://github.com/openai/whisper/assets/266841/f4619d66-1058-4005-8f67-a9d811b77c62)



## コマンドラインでの利用方法

以下のコマンドで、`turbo` モデルを使って音声ファイルを文字起こしできます。

    whisper audio.flac audio.mp3 audio.wav --model turbo

デフォルト設定（`turbo` モデル選択）は英語の文字起こしに適しています。英語以外の音声ファイルを文字起こしする場合は、`--language` オプションで言語を指定してください。

    whisper japanese.wav --language Japanese

`--task translate` を追加すると、音声を英語に翻訳します。

    whisper japanese.wav --language Japanese --task translate

利用可能な全オプションは以下で確認できます。

    whisper --help

利用可能な全言語の一覧は [tokenizer.py](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py) を参照してください。


## Pythonでの利用方法

Pythonからも文字起こしを実行できます。

```python
import whisper

model = whisper.load_model("turbo")
result = model.transcribe("audio.mp3")
print(result["text"])
```

内部的には、`transcribe()` メソッドはファイル全体を読み込み、30秒ごとにスライドするウィンドウで音声を処理し、それぞれのウィンドウに対して自己回帰型のシーケンス・ツー・シーケンス予測を行います。

以下は、モデルへのより低レベルなアクセスを提供する `whisper.detect_language()` および `whisper.decode()` の使用例です。

```python
import whisper

model = whisper.load_model("turbo")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("audio.mp3")
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

# decode the audio
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)
```

## その他の例

Whisperやサードパーティ製の拡張機能（ウェブデモ、他ツールとの連携、他プラットフォーム向けの移植など）の利用例を共有したい場合は、Discussionsの [🙌 Show and tell](https://github.com/openai/whisper/discussions/categories/show-and-tell) カテゴリをご利用ください。


## ライセンス

Whisperのコードおよびモデルの重みはMITライセンスのもとで公開されています。詳細は [LICENSE](https://github.com/openai/whisper/blob/main/LICENSE) をご覧ください。
