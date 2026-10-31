import os
import random
from PIL import Image, ImageDraw
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="ダンジョン・ローグアタック：3人パーティ戦",
    page_icon="⚔️",
    layout="centered",
)

st.title("⚔️ ダンジョン・ローグアタック：パーティ戦 (全10ステージ)")
st.caption(
    "3人の仲間を順に操作して魔王軍を打ち破り、第10ステージの深部を目指せ！"
)

# --- ゲーム状態（セッションステート）の初期化 ---
if "initialized" not in st.session_state:
  st.session_state.stage = 1
  # プレイヤー3体のパーティ定義
  st.session_state.players = [
      {
          "name": "戦士アレル",
          "hp": 100,
          "max_hp": 100,
          "x": 150,
          "y": 220,
          "image": "assets/player1.png",
      },
      {
          "name": "魔術師ミリア",
          "hp": 70,
          "max_hp": 70,
          "x": 250,
          "y": 220,
          "image": "assets/player2.png",
      },
      {
          "name": "聖騎士レオン",
          "hp": 120,
          "max_hp": 120,
          "x": 350,
          "y": 220,
          "image": "assets/player3.png",
      },
  ]
  st.session_state.current_player_idx = 0  # 現在行動するプレイヤーのインデックス (0, 1, 2)

  # ステージに応じた敵の初期化
  st.session_state.enemy_hp = 80 + (st.session_state.stage * 20)
  st.session_state.enemy_max_hp = st.session_state.enemy_hp
  st.session_state.enemy_x = 250
  st.session_state.enemy_y = 80
  st.session_state.enemy_intent = "line"
  st.session_state.logs = [
      "第1ステージ開始：暗いダンジョンに魔物が現れた！"
  ]
  st.session_state.initialized = True

WIDTH, HEIGHT = 500, 300


# --- 画像を安全に読み込んで配置・リサイズするヘルパー関数 ---
def paste_image_safely(bg_image, img_path, pos, size=(40, 40), fallback_color=(64, 165, 255)):
  """指定されたパスの画像を読み込み、背景に貼り付ける。見つからない場合は四角形を描画。"""
  try:
    if os.path.exists(img_path):
      img = Image.open(img_path).convert("RGBA")
      img = img.resize(size, Image.Resampling.LANCZOS)
      # 中央揃えで貼り付け
      bg_image.paste(
          img, (pos[0] - size[0] // 2, pos[1] - size[1] // 2), img
      )
      return
  except Exception:
    pass

  # 画像が無い場合のフォールバック（色付きの丸または四角）
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
  if log_msg:
    st.session_state.logs.insert(0, f"【{current_p['name']}】 {log_msg}")

  # 1. 敵の移動処理
  if current_p["x"] < st.session_state.enemy_x:
    st.session_state.enemy_x -= random.choice([0, 15, 25])
  else:
    st.session_state.enemy_x += random.choice([0, 15, 25])
  st.session_state.enemy_x = max(80, min(420, st.session_state.enemy_x))

  # 2. 攻撃予告の判定（現在行動中のキャラに直撃するか）
  hit = False
  if st.session_state.enemy_intent == "line":
    if abs(current_p["x"] - st.session_state.enemy_x) < 25:
      hit = True
  elif st.session_state.enemy_intent == "area":
    if 180 < current_p["x"] < 320:
      hit = True

  if hit:
    edmg = random.randint(10, 20)
    current_p["hp"] -= edmg
    st.session_state.logs.insert(
        0, f"  ⚠️ 敵の攻撃が {current_p['name']} に直撃！ {edmg} のダメージ！"
    )
  else:
    st.session_state.logs.insert(
        0, f"  ✨ {current_p['name']} はうまく回避した！"
    )

  # 3. 敵の次の攻撃予告を決定
  st.session_state.enemy_intent = random.choice(["line", "area"])

  # 4. 生存している次のプレイヤーに手番を回す
  alive_indices = [
      i for i, p in enumerate(st.session_state.players) if p["hp"] > 0
  ]

  if st.session_state.enemy_hp <= 0:
    # 敵撃破！次ステージへ
    if st.session_state.stage >= 10:
      st.session_state.game_cleared = True
    else:
      st.session_state.stage += 1
      st.session_state.logs.insert(
          0,
          f"🎉 ステージ {st.session_state.stage - 1} クリア！次のステージへ進む。",
      )
      # ステージが進むにつれて敵のHPが増加
      st.session_state.enemy_max_hp = 80 + (st.session_state.stage * 20)
      st.session_state.enemy_hp = st.session_state.enemy_max_hp
  elif not alive_indices:
    # パーティ全滅
    st.session_state.game_over = True
  else:
    # 次のメンバーへ順番交代
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
  for x in range(0, WIDTH, 40):
    draw.line([(x, 0), (x, HEIGHT)], fill=(28, 33, 48), width=1)
  for y in range(0, HEIGHT, 40):
    draw.line([(0, y), (WIDTH, y)], fill=(28, 33, 48), width=1)

  # 1. 敵の攻撃予告エリア
  if st.session_state.enemy_intent == "line":
    draw.rectangle(
        [
            st.session_state.enemy_x - 15,
            st.session_state.enemy_y + 25,
            st.session_state.enemy_x + 15,
            HEIGHT - 20,
        ],
        outline=(255, 80, 80),
        fill=(80, 20, 20),
    )
  elif st.session_state.enemy_intent == "area":
    draw.rectangle(
        [180, 150, 320, HEIGHT - 20], outline=(255, 100, 50), fill=(90, 40, 20)
    )

  # 2. 敵の画像描画
  paste_image_safely(
      image,
      "assets/enemy.png",
      (st.session_state.enemy_x, st.session_state.enemy_y),
      size=(48, 48),
      fallback_color=(231, 76, 60),
  )

  # 3. 生存しているプレイヤー全員の描画（行動中のキャラは少し明るく/大きく）
  for idx, p in enumerate(st.session_state.players):
    if p["hp"] > 0:
      is_current = idx == st.session_state.current_player_idx
      size = (44, 44) if is_current else (36, 36)
      colors = [(64, 165, 255), (46, 204, 113), (241, 196, 15)]
      paste_image_safely(
          image, p["image"], (p["x"], p["y"]), size=size, fallback_color=colors[idx]
      )

  # 4. ステータス表示（敵HPとステージ）
  draw.rectangle([320, 15, 480, 32], fill=(40, 40, 40))
  e_w = max(
      0,
      int(
          160
          * (st.session_state.enemy_hp / max(1, st.session_state.enemy_max_hp))
      ),
  )
  draw.rectangle([320, 15, 320 + e_w, 32], fill=(231, 76, 60))

  return image


# --- レイアウト配置 ---
col_game, col_ctrl = st.columns([3, 2])

with col_game:
  st.subheader(
      f"🎮 ステージ {st.session_state.get('stage', 1)} / 10 (敵HP:"
      f" {st.session_state.get('enemy_hp', 100)})"
  )
  game_img = render_game_frame()
  st.image(game_img, use_container_width=True)

with col_ctrl:
  # ゲームクリア・ゲームオーバー判定
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
        current_p["y"] = max(120, current_p["y"] - 15)
        process_turn("move", "前に踏み込んだ！")
    with c1:
      if st.button("⬅️ 左"):
        current_p["x"] = max(50, current_p["x"] - 35)
        process_turn("move", "左へ回避した！")
    with c3:
      if st.button("➡️ 右"):
        current_p["x"] = min(450, current_p["x"] + 35)
        process_turn("move", "右へ回避した！")

    st.markdown("---")

    if st.button("🔥 スキル攻撃", use_container_width=True):
      dmg = random.randint(18, 30)
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
