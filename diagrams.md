# restia アプリケーション設計図

このドキュメントは「仲良し子」アプリの設計とデータ構造を視覚化するための図（Mermaid形式）をまとめています。
GitHubなどのMarkdown対応エディタやプレビュー機能を使用することで図としてレンダリングされます。

## 1. ER図（データ構造図）
データベースの代わりに使用している `data.json` の構造と各要素の関連性です。

```mermaid
erDiagram
    DATA_JSON ||--|| STATUS : "持つ"
    DATA_JSON ||--o{ PROFILE : "持つ"
    DATA_JSON ||--o{ MEMORY : "持つ"
    DATA_JSON ||--o{ EVENT : "持つ"

    DATA_JSON {
        string first_meet "出会った日 (例: 2026-01-22)"
    }
    STATUS {
        string user1_name "ユーザー1の名前"
        string user1_mood "ユーザー1の気分"
        string user2_name "ユーザー2の名前"
        string user2_mood "ユーザー2の気分"
    }
    PROFILE {
        string name "【キー】名前"
        string birthday "誕生日"
        string job "職業"
        string hobby "趣味"
        string mbti "MBTI"
        string food "好きな食べ物"
        string shampoo "シャンプー"
        string youtube "好きなYouTube"
        string song_url "今の曲URL"
        string ng "地雷"
        string reconcile "仲直り方法"
    }
    MEMORY {
        string date "投稿日"
        string title "タイトル"
        string img "Base64エンコードされた画像"
    }
    EVENT {
        string description "※現在未実装"
    }
```

**【解説】**
このER図は、アプリの全データが保存されている `data.json` 内の構造を示しています。
ルートとなるJSONの直下に「出会った日（`first_meet`）」があり、さらに `status`（それぞれのユーザーの気分や名前）、`profiles`（ユーザーごとの詳細なプロフィール情報）、`memories`（アルバム機能の画像とタイトル）、`events`（現在は未実装）のリストや辞書がぶら下がっている形になっています。本来のリレーショナルデータベースのテーブルに見立てて視覚化しています。

## 2. シーケンス図（データの読み書きの流れ）
ユーザーがプロフィール画面で情報を入力し、保存する際の流れです。

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant Browser as ブラウザ (UI)
    participant App as Streamlit (app.py)
    participant FileSys as data.json

    User->>Browser: プロフィール情報を入力
    User->>Browser: 「保存」ボタンをクリック
    Browser->>App: イベント送信
    App->>App: data["profiles"] の値を更新
    App->>FileSys: save_data(data) を呼び出し
    FileSys-->>App: JSONファイルに書き込み完了
    App->>App: st.rerun() を実行（強制リロード）
    App->>FileSys: load_data() を再度呼び出し
    FileSys-->>App: 最新のJSONデータを返却
    App-->>Browser: 新しいデータで画面を再描画
```

**【解説】**
ユーザーが「プロフィールを保存する」などのアクションを起こした時の、アプリ裏側の処理の流れを表しています。
ブラウザから入力データが送られると、Streamlit側でPythonの辞書データを更新し、そのまま `data.json` ファイルを上書き保存します。その後、Streamlit特有の `st.rerun()` 関数が呼ばれることで、自動的に画面全体が最新のデータで再描画され、ユーザーの画面に変更が反映されるという一連のサイクルです。

## 3. コンポーネント図（システム構成）
このアプリを構成する主要な要素と、データ通信の構成です。

```mermaid
flowchart TD
    subgraph Client [クライアント層]
        Browser[Webブラウザ]
    end

    subgraph Server [Streamlit サーバー層]
        direction TB
        UI[Streamlit UIコンポーネント\nst.tabs, st.text_input]
        Logic[アプリロジック\napply_custom_style 等]
        FileIO[データ入出力\nload_data, save_data]
        ImgHelper[画像処理\nimage_to_base64]
    end

    subgraph Storage [データ永続化層]
        JSON[(data.json)]
    end

    Browser <-->|HTTP / WebSocket| UI
    UI <--> Logic
    Logic --> ImgHelper
    Logic <--> FileIO
    FileIO <-->|JSON読み書き| JSON
```

**【解説】**
システムがどのような技術や要素で成り立っているかを示す図です。
このアプリは大きく分けて「ユーザーが操作するブラウザ」「PythonとStreamlitで動くサーバー」「データが保存されるJSONファイル」の3層構造になっています。ユーザーがUIを操作すると、アプリのロジックが走り、必要に応じて画像処理モジュール（Pillow）を呼び出したり、ファイル入出力モジュールを通して JSON ファイルからデータを読み書きします。

## 4. 状態遷移図（画面遷移とアクション）
起動からの画面遷移と、データ保存に伴う再描画の状態変化です。

```mermaid
stateDiagram-v2
    [*] --> アプリ起動
    アプリ起動 --> データ読み込み : load_data()

    state アプリ画面 {
        データ読み込み --> ホームタブ : デフォルト表示
        ホームタブ --> プロフタブ : タブ切り替え
        ホームタブ --> 相性タブ : タブ切り替え
        ホームタブ --> アルバムタブ : タブ切り替え
        ホームタブ --> 予定タブ : タブ切り替え
        ホームタブ --> 設定タブ : タブ切り替え
    }

    state データ更新処理 {
        ホームタブ --> データ保存 : 気分更新
        プロフタブ --> データ保存 : プロフ保存
        アルバムタブ --> データ保存 : 画像保存
        設定タブ --> データ保存 : 出会った日設定
    }

    データ保存 --> データ読み込み : st.rerun()による再描画
```

**【解説】**
アプリを起動してから、ユーザーがどのような画面を移動（遷移）できるかと、データの状態変化を表しています。
起動するとまずJSONからデータが読み込まれ、「ホームタブ」が表示されます。そこから上部のタブをクリックすることで各画面に移動できます。どの画面にいても、データを更新するボタン（気分更新、プロフ保存など）を押すと「データ更新処理」が走り、最終的に再描画されて元のタブの最新状態に戻る、というステート（状態）のループを示しています。
