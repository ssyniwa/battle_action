# battle_action
# ⚔️ ダンジョン・ローグアタック (Dungeon Rogue Attack)

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Canvas-E34F26?style=for-the-badge&logo=html5&logoColor=white)

PythonとStreamlit、およびHTML5 Canvas/JavaScriptを組み合わせて開発された、全10ステージ構成の**リアルタイム反射弾幕アクションゲーム**です。

---

## 🌟 ゲームの概要・特徴

- **全10ステージの討伐旅**: ステージが進むごとに敵の攻撃パターンやAIの戦術が激化。
- **反射弾幕＆要塞物理**: プレイヤーと敵の攻撃弾が障害物（壁）に当たると**リアルタイムに物理反射**します。遮蔽物を利用した立ち回りが勝利の鍵です。
- **3人のパーティ＆交代UI制御**: HPがゼロになったキャラクターは「死亡」状態となり、生存している仲間に引き継いで戦うパーティ交代システムを搭載。

---

## 💻 技術スタック・アーキテクチャ

| 役割 | 使用技術 / ライブラリ |
| :--- | :--- |
| **バックエンド / 状態管理** | Python 3.x, Streamlit (`st.session_state`) |
| **フロントエンド / 描画** | HTML5 Canvas, JavaScript (ES6) |
| **コンポーネント連携** | `streamlit.components.v1.html` |
| **レイアウト / UI** | Streamlit標準コンポーネント (`st.columns`, `st.button` 等) |

### 💡 技術的なこだわり・実装ポイント

1. **Streamlit × 60fps リアルタイム描画**
   - Python側で状態（HP・ステージ・成長Lv）を保持しつつ、`streamlit.components.v1` を介して埋め込んだ JavaScript の `requestAnimationFrame` により、ブラウザ上で滑らかな60fpsのアクションを描画しています。

2. **壁反射・衝突判定（AABB）**
   - 矩形障害物と弾幕のめり込み判定・ベクトル反転計算を行い、直線的な弾幕に予測不能な反射軌道を生み出しています。

3. **厳密なUIステート管理 (`must_swap` フラグ)**
   - 出撃キャラが戦闘不能（HP 0）になった際、個別の手動選択ボタンをロックするロジックをPython側で制御。必ず「交代ボタン」を経由させることで、状態の不整合や不正な選択を防ぎます。

---

## 🚀 動作方法（ローカル環境）

### 1. リポジトリのクローン
```bash
git clone [https://github.com/your-username/dungeon-rogue-attack.git](https://github.com/your-username/dungeon-rogue-attack.git)
cd dungeon-rogue-attack
```
### 2. 依存ライブラリのインストール
```bash
pip install streamlit
```
### 3. アプリの起動
```bash
streamlit run main.py
```
起動後、ブラウザで http://localhost:8501 が自動的に開きます。

## 🕹️ 操作方法
- 移動: 矢印キー (← ↑ ↓ →) または A / W / S / D

- 攻撃: Z キー または Y キー

- 戦闘開始: アプリ画面上の 「🔥 戦闘開始」 ボタンをクリック、または移動/攻撃キーを押す

## 📂 プロジェクト構成
```bash
.
├── assets/                  # プレイヤー・エネミー画像素材
│   ├── player1.jpg
│   ├── player2.jpg
│   ├── player3.jpg
│   └── enemy1.jpg〜enemy10.jpg
├── main.py                  # メインアプリケーション（Streamlit & HTML/JS）
└── README.md                # 本ドキュメント
```
## 📝 ライセンス
MIT License
