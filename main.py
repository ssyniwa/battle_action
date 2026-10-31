import random
from PIL import Image, ImageDraw
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="ダンジョン・ローグアタック：タクティカル戦",
    page_icon="⚔️",
    layout="centered",
)

st.title("⚔️ ダンジョン・ローグアタック：タクティカル戦")
st.caption("敵も移動し、攻撃予告（赤ゾーン）が表示されます。予測して回避せよ！")

# --- ゲーム状態（セッションステート）の初期化 ---
if "initialized" not in st.session_state:
  st.session_state.player_hp = 100
  st.session_state.boss_hp = 100
  st.session_state.player_x = 250
  st.session_state.player_y = 220
  st.session_state.boss_x = 250
  st.session_state.boss_y = 80
  st.session_state.boss_intent = (
      "attack_line"  # ボスの予告攻撃の種類 ('attack_line', 'attack_wide')
  )
  st.session_state.turn = 1
  st.session_state.logs = [
      "ダンジョンの奥深くで魔王が現れた！攻撃予告を避けて反撃せよ。"
  ]
  st.session_state.initialized = True

WIDTH, HEIGHT = 500, 300

# --- ドット絵のパターン定義 ---
PLAYER_DOTS = [
    "....1111....",
    "...111111...",
    "..1.1111.1..",
    "..1.1111.1..",
    "....1111....",
    "...11..11...",
    "..1.2..2.1..",
    ".1..2..2..1.",
]

BOSS_DOTS = [
    "....2222....",
    "...222222...",
    "..2.2222.2..",
    "..22222222..",
    "....2222....",
    "...2....2...",
    "..2......2..",
    ".2........2.",
]


def draw_dot_sprite(draw, dot_pattern, start_x, start_y, scale=3, color_map=None):
  if color_map is None:
    color_map = {"1": (64, 165, 255), "2": (231, 76, 60)}
  for r_idx, row in enumerate(dot_pattern):
    for c_idx, char in enumerate(row):
      if char in color_map:
        x0 = start_x + (c_idx * scale)
        y0 = start_y + (r_idx * scale)
        draw.rectangle([x0, y0, x0 + scale, y0 + scale], fill=color_map[char])


# --- ゲーム画面の描画関数 ---
def render_game_frame():
  image = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 17, 26))
  draw = ImageDraw.Draw(image)

  # 背景グリッド
  for x in range(0, WIDTH, 40):
    draw.line([(x, 0), (x, HEIGHT)], fill=(28, 33, 48), width=1)
  for y in range(0, HEIGHT, 40):
    draw.line([(0, y), (WIDTH, y)], fill=(28, 33, 48), width=1)

  # --- 1. ボスの攻撃予告（赤く光るエリア）の描画 ---
  if st.session_state.boss_intent == "line":
    # ボスの直下から下に向かう直線状の攻撃予告
    draw.rectangle(
        [
            st.session_state.boss_x - 15,
            st.session_state.boss_y + 25,
            st.session_state.boss_x + 15,
            HEIGHT - 20,
        ],
        outline=(255, 80, 80),
        fill=(80, 20, 20),
    )
  elif st.session_state.boss_intent == "area":
    # プレイヤーの周辺を狙った広範囲攻撃予告
    target_x = st.session_state.player_x
    draw.rectangle(
        [target_x - 50, 150, target_x + 50, HEIGHT - 20],
        outline=(255, 100, 50),
        fill=(90, 40, 20),
    )

  # --- 2. ボス（敵）の描画 ---
  draw_dot_sprite(
      draw,
      BOSS_DOTS,
      start_x=st.session_state.boss_x - 18,
      start_y=st.session_state.boss_y - 12,
      scale=3,
      color_map={"2": (255, 85, 85)},
  )

  # --- 3. プレイヤーの描画 ---
  draw_dot_sprite(
      draw,
      PLAYER_DOTS,
      start_x=st.session_state.player_x - 18,
      start_y=st.session_state.player_y - 12,
      scale=3,
      color_map={"1": (64, 165, 255), "2": (46, 204, 113)},
  )

  # --- 4. ステータスバー（HP） ---
  draw.rectangle([20, 20, 140, 32], fill=(40, 40, 40))
  p_w = max(0, int(120 * (st.session_state.player_hp / 100)))
  draw.rectangle([20, 20, 20 + p_w, 32], fill=(46, 204, 113))

  draw.rectangle([360, 20, 480, 32], fill=(40, 40, 40))
  b_w = max(0, int(120 * (st.session_state.boss_hp / 100)))
  draw.rectangle([360, 20, 360 + b_w, 32], fill=(231, 76, 60))

  return image


# --- レイアウト配置 ---
col_game, col_ctrl = st.columns([3, 2])

with col_game:
  st.subheader("🎮 バトルフィールド")
  game_img = render_game_frame()
  st.image(game_img, use_container_width=True)

with col_ctrl:
  st.subheader(f"⚡ ターン {st.session_state.turn}: アクション選択")

  is_game_over = (
      st.session_state.player_hp <= 0 or st.session_state.boss_hp <= 0
  )

  if not is_game_over:
    st.text("【移動】攻撃予告エリア（赤）から逃げろ！")
    c1, c2, c3 = st.columns(3)
    with c2:
      if st.button("⬆️ 前進"):
        st.session_state.player_y = max(120, st.session_state.player_y - 15)
        process_turn("move", "前に踏み込んだ！")
    with c1:
      if st.button("⬅️ 左回避"):
        st.session_state.player_x = max(50, st.session_state.player_x - 40)
        process_turn("move", "左へ素早く回避した！")
    with c3:
      if st.button("➡️ 右回避"):
        st.session_state.player_x = min(450, st.session_state.player_x + 40)
        process_turn("move", "右へ素早く回避した！")

    st.markdown("---")

    if st.button("🔥 必殺剣 (攻撃)", use_container_width=True):
      dmg = random.randint(18, 28)
      st.session_state.boss_hp -= dmg
      st.session_state.logs.insert(
          0,
          f"ターン {st.session_state.turn}: プレイヤーの攻撃！ 魔王に {dmg}"
          " のダメージ。",
      )
      process_turn("attack", "")

  else:
    if st.session_state.player_hp <= 0:
      st.error("💀 魔王の攻撃に倒れました... ゲームオーバー")
    else:
      st.success("🎉 魔王を討伐しました！ 勝利！")

  if st.button("🔄 ゲームリセット", use_container_width=True):
    for key in list(st.session_state.keys()):
      del st.session_state[key]
    st.rerun()


# --- ターン進行＆敵の行動を処理する共通関数 ---
def process_turn(action_type, log_msg):
  if log_msg:
    st.session_state.logs.insert(
        0, f"ターン {st.session_state.turn}: {log_msg}"
    )

  # 1. 敵（ボス）の移動処理（プレイヤーを少し追いかけるように動く）
  if st.session_state.player_x < st.session_state.boss_x:
    st.session_state.boss_x -= random.choice([0, 20, 35])
  else:
    st.session_state.boss_x += random.choice([0, 20, 35])
  st.session_state.boss_x = max(80, min(420, st.session_state.boss_x))

  # 2. 前のターンに予告された攻撃の判定（赤ゾーンにプレイヤーがいたら被弾）
  hit = False
  if st.session_state.boss_intent == "line":
    # 直線上の予告ゾーン（ボスのX座標±20以内）
    if abs(st.session_state.player_x - st.session_state.boss_x) < 25:
      hit = True
  elif st.session_state.boss_intent == "area":
    # 広範囲エリア（画面中央付近など）
    if 180 < st.session_state.player_x < 320:
      hit = True

  if hit:
    edmg = random.randint(15, 25)
    st.session_state.player_hp -= edmg
    st.session_state.logs.insert(
        0, f"  ⚠️ 魔王の攻撃が直撃！ {edmg} のダメージを受けた！"
    )
  else:
    st.session_state.logs.insert(0, "  ✨ プレイヤーはうまく攻撃を回避した！")

  # 3. 次のターンの攻撃予告をランダムに決定
  st.session_state.boss_intent = random.choice(["line", "area"])

  st.session_state.turn += 1
  st.rerun()


# --- ログ表示 ---
st.markdown("---")
st.subheader("📜 バトルログ")
for log in st.session_state.logs[:4]:
  st.
