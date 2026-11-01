import os
import random
from PIL import Image, ImageDraw
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="ダンジョン・ローグアタック：特大ビジュアル版",
    page_icon="⚔️",
    layout="centered",
)

st.title("⚔️ ダンジョン・ローグアタック：全10ステージ討伐の旅")
st.caption("3人の仲間を率い、立ちはだかる10体の強敵を撃破せよ！画面・キャラ特大拡大版")

# --- ゲーム状態（セッションステート）の初期化 ---
if "initialized" not in st.session_state:
  st.session_state.stage = 1
  # プレイヤー3体のパーティ定義（JPG対応）
  st.session_state.players = [
      {
          "name": "戦士アレル",
          "hp": 100,
          "max_hp": 100,
          "x": 180,
          "y": 240,
          "image": "assets/player1.jpg",
      },
      {
          "name": "魔術師ミリア",
          "hp": 70,
          "max_hp": 70,
          "x": 300,
          "y": 240,
          "image": "assets/player2.jpg",
      },
      {
          "name": "聖騎士レオン",
          "hp": 120,
          "max_hp": 120,
          "x": 420,
          "y": 240,
          "image": "assets/player3.jpg",
      },
  ]
  st.session_state.current_player_idx = 0  # 現在行動するプレイヤーのインデックス

  # ステージに応じた敵の初期化
  st.session_state.enemy_hp = 70 + (st.session_state.stage * 25)
  st.session_state.enemy_max_hp = st.session_state.enemy_hp
  st.session_state.enemy_x = 300
  st.session_state.enemy_y = 90
  st.session_state.enemy_intent = "line"
  st.session_state.logs = [
      "第1ステージ開始：スライムが現れた！仲間と共に戦え。"
  ]
  st.session_state.initialized = True

# フィールドのベース解像度を少し拡大 (600x350)
WIDTH, HEIGHT = 600, 350

# ステージごとの敵の名前リスト（全10種類）
ENEMY_NAMES = {
    1: "ぷにぷにスライム",
    2: "牙をむくゴブリン",
    3: "うろこ竜の幼体",
    4: "怪異のスケルトン",
    5: "闇夜のダークナイト",
    6: "猛毒の大蜘蛛",
    7: "炎をまとうキマイラ",
    8: "冷酷なヴァンパイア",
    9: "古のレッドドラゴン",
    10: "魔界の君主・魔王",
}


# --- 画像を安全に読み込んで配置・リサイズするヘルパー関数 ---
def paste_image_safely(
    bg_image, img_path, pos, size=(80, 80), fallback_color=(64, 165, 255)
):
  """指定されたパスのJPG画像を読み込み、さらに大きくリサイズして背景に貼り付ける。"""
  try:
    if os.path.exists(img_path):
      img = Image.open(img_path).convert("RGB")
      img = img.resize(size, Image.Resampling.LANCZOS)
      bg_image.paste(img, (pos[0] - size[0] // 2, pos[1] - size[1] // 2))
      return
  except Exception:
    pass

  # 画像が無い場合のフォールバック描画
  draw = ImageDraw.Draw(bg_image)
  draw.rectangle(
      [
          pos[0] - size[0] // 2,
          pos[1] - size[1] // 2,
          pos[0] + size[0] // 2,
          pos[1] + size[1] // 2,
      ],
      fill=fallback_color,
  )


# --- ターン進行＆パーティ行動の処理関数 ---
def process_turn(action_type, log_msg):
  current_p = st.session_state.players[st.session_state.current_player_idx]
  current_enemy_name = ENEMY_NAMES.get(st.session_state.stage, "敵")

  if log_msg:
    st.session_state.logs.insert(0, f"【{current_p['name']}】 {log_msg}")

  # 1. 敵の移動処理
  if current_p["x"] < st.session_state.enemy_x:
    st.session_state.enemy_x -= random.choice([0, 20, 35])
  else:
    st.session_state.enemy_x += random.choice([0, 20, 35])
  st.session_state.enemy_x = max(100, min(500, st.session_state.enemy_x))

  # 2. 攻撃予告の判定
  hit = False
  if st.session_state.enemy_intent == "line":
    if abs(current_p["x"] - st.session_state.enemy_x) < 35:
      hit = True
  elif st.session_state.enemy_intent == "area":
    if 200 < current_p["x"] < 400:
      hit = True

  if hit:
    edmg = random.randint(10 + st.session_state.stage, 18 + st.session_state.stage)
    current_p["hp"] -= edmg
    st.session_state.logs.insert(
        0,
        f"  ⚠️ {current_enemy_name}の攻撃が {current_p['name']}"
        f" に直撃！ {edmg} のダメージ！",
    )
  else:
    st.session_state.logs.insert(
        0, f"  ✨ {current_p['name']} は攻撃をうまく回避した！"
    )

  # 3. 次の攻撃予告を決定
  st.session_state.enemy_intent = random.choice(["line", "area"])

  # 4. ステージクリア・全滅・次キャラ交代の判定
  alive_indices = [
      i for i, p in enumerate(st.session_state.players) if p["hp"] > 0
  ]

  if st.session_state.enemy_hp <= 0:
    if st.session_state.stage >= 10:
      st.session_state.game_cleared = True
    else:
      prev_stage = st.session_state.stage
      st.session_state.stage += 1
      st.session_state.logs.insert(
          0,
          f"🎉 ステージ {prev_stage} クリア！次に出現した強敵は"
          f"「{ENEMY_NAMES[st.session_state.stage]}」だ！",
      )
      st.session_state.enemy_max_hp = 70 + (st.session_state.stage * 25)
      st.session_state.enemy_hp = st.session_state.enemy_max_hp
  elif not alive_indices:
    st.session_state.game_over = True
  else:
    current_idx = st.session_state.current_player_idx
    while True:
      current_idx = (current_idx + 1) % len(st.session_state.players)
      if st.session_state.players[current_idx]["hp"] > 0:
        st.session_state.current_player_idx = current_idx
        break

  st.rerun()


# --- ゲーム画面の描画関数 ---
def render_game_frame():
  image = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 17, 26))
  draw = ImageDraw.Draw(image)

  # 背景グリッド
  for x in range(0, WIDTH, 50):
    draw.line([(x, 0), (x, HEIGHT)], fill=(28, 33, 48), width=1)
  for y in range(0, HEIGHT, 50):
    draw.line([(0, y), (WIDTH, y)], fill=(28, 33, 48), width=1)

  # 1. 敵の攻撃予告エリア
  if st.session_state.enemy_intent == "line":
    draw.rectangle(
        [
            st.session_state.enemy_x - 30,
            st.session_state.enemy_y + 35,
            st.session_state.enemy_x + 30,
            HEIGHT - 20,
        ],
        outline=(255, 80, 80),
        fill=(80, 20, 20),
    )
  elif st.session_state.enemy_intent == "area":
    draw.rectangle(
        [200, 150, 400, HEIGHT - 20], outline=(255, 100, 50), fill=(90, 40, 20)
    )

  # 2. ステージに応じた敵の画像描画（さらに大きく：96x96）[cite: 2]
  current_stage = st.session_state.get("stage", 1)
  enemy_img_path = f"assets/enemy{current_stage}.jpg"

  paste_image_safely(
      image,
      enemy_img_path,
      (st.session_state.enemy_x, st.session_state.enemy_y),
      size=(96, 96),
      fallback_color=(231, 76, 60),
  )

  # 3. 生存しているプレイヤー全員の描画（さらに大きく：行動中は90x90、他は70x70）[cite: 2]
  for idx, p in enumerate(st.session_state.players):
    if p["hp"] > 0:
      is_current = idx == st.session_state.current_player_idx
      size = (90, 90) if is_current else (70, 70)
      colors = [(64, 165, 255), (46, 204, 113), (241, 196, 15)]
      paste_image_safely(
          image, p["image"], (p["x"], p["y"]), size=size, fallback_color=colors[idx]
      )

  # 4. 敵のHPバー描画
  draw.rectangle([400, 20, 570, 38], fill=(40, 40, 40))
  e_w = max(
      0,
      int(
          170
          * (
              st.session_state.get("enemy_hp", 100)
              / max(1, st.session_state.get("enemy_max_hp", 100))
          )
      ),
  )
  draw.rectangle([400, 20, 400 + e_w, 38], fill=(231, 76, 60))

  # ★ 画面全体の拡大率を「3倍」に設定し、圧倒的に見やすくする[cite: 2]
  scale_factor = 3
  image = image.resize(
      (WIDTH * scale_factor, HEIGHT * scale_factor), Image.Resampling.NEAREST
  )

  return image


# --- レイアウト配置 ---
col_game, col_ctrl = st.columns([3, 2])

with col_game:
  current_stage = st.session_state.get("stage", 1)
  enemy_name = ENEMY_NAMES.get(current_stage, "敵")
  st.subheader(f"🎮 Stage {current_stage}/10 : {enemy_name}")
  game_img = render_game_frame()
  st.image(game_img, use_container_width=True)

with col_ctrl:
  is_cleared = st.session_state.get("game_cleared", False)
  is_game_over = st.session_state.get("game_over", False)

  if not is_cleared and not is_game_over:
    current_p = st.session_state.players[st.session_state.current_player_idx]

    st.markdown(f"### 👥 手番: **{current_p['name']}**")
    st.progress(max(0.0, current_p["hp"] / current_p["max_hp"]))
    st.text(f"HP: {current_p['hp']} / {current_p['max_hp']}")

    st.markdown("---")
    st.text("【移動】位置を変えて攻撃を避ける")
    c1, c2, c3 = st.columns(3)
    with c2:
      if st.button("⬆️ 前進"):
        current_p["y"] = max(130, current_p["y"] - 20)
        process_turn("move", "前に踏み込んだ！")
    with c1:
      if st.button("⬅️ 左"):
        current_p["x"] = max(60, current_p["x"] - 45)
        process_turn("move", "左へ回避した！")
    with c3:
      if st.button("➡️ 右"):
        current_p["x"] = min(540, current_p["x"] + 45)
        process_turn("move", "右へ回避した！")

    st.markdown("---")

    if st.button("🔥 スキル攻撃", use_container_width=True):
      dmg = random.randint(20, 32)
      st.session_state.enemy_hp -= dmg
      process_turn("attack", f"強力なスキル攻撃で {dmg} のダメージを与えた！")

  else:
    if is_cleared:
      st.success("🎉 全10ステージ踏破！魔王を完全に討伐した！")
    elif is_game_over:
      st.error("💀 パーティが全滅しました... ゲームオーバー")

  if st.button("🔄 ゲームリセット", use_container_width=True):
    for key in list(st.session_state.keys()):
      del st.session_state[key]
    st.rerun()

# --- ログ表示 ---
st.markdown("---")
st.subheader("📜 バトルログ")
for log in st.session_state.logs[:4]:
  st.text(log)
