import random
from PIL import Image, ImageDraw
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="ダンジョン・ローグアタック", page_icon="⚔️", layout="centered"
)

st.title("⚔️ ダンジョン・ローグアタック (安定版)")
st.caption(
    "ボタン操作でキャラクターを移動させ、敵の攻撃をかわしながら討伐しよう！"
)

# --- ゲーム状態（セッションステート）の初期化 ---
if "initialized" not in st.session_state:
  st.session_state.player_hp = 100
  st.session_state.boss_hp = 100
  st.session_state.player_x = 250
  st.session_state.player_y = 220
  st.session_state.turn = 1
  st.session_state.logs = [
      "ダンジョンの奥深くで強敵が現れた！行動を選べ。"
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
        draw.rectangle([x0, y0, x0 + scale, y1 := y0 + scale], fill=color_map[char])


# --- ゲーム画面の描画関数 ---
def render_game_frame():
  image = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 17, 26))
  draw = ImageDraw.Draw(image)

  # 背景グリッド
  for x in range(0, WIDTH, 40):
    draw.line([(x, 0), (x, HEIGHT)], fill=(28, 33, 48), width=1)
  for y in range(0, HEIGHT, 40):
    draw.line([(0, y), (WIDTH, y)], fill=(28, 33, 48), width=1)

  # ボス描画
  draw_dot_sprite(
      draw, BOSS_DOTS, start_x=235, start_y=30, scale=3, color_map={"2": (255, 85, 85)}
  )

  # プレイヤー描画
  draw_dot_sprite(
      draw,
      PLAYER_DOTS,
      start_x=st.session_state.player_x - 18,
      start_y=st.session_state.player_y - 12,
      scale=3,
      color_map={"1": (64, 165, 255), "2": (46, 204, 113)},
  )

  # HPバー（プレイヤー）
  draw.rectangle([20, 20, 140, 32], fill=(40, 40, 40))
  p_w = max(0, int(120 * (st.session_state.player_hp / 100)))
  draw.rectangle([20, 20, 20 + p_w, 32], fill=(46, 204, 113))

  # HPバー（ボス）
  draw.rectangle([360, 20, 480, 32], fill=(40, 40, 40))
  b_w = max(0, int(120 * (st.session_state.boss_hp / 100)))
  draw.rectangle([360, 20, 360 + b_w, 32], fill=(231, 76, 60))

  return image


# --- レイアウト配置 ---
col_game, col_ctrl = st.columns([3, 2])

with col_game:
  st.subheader("🎮 バトルフィールド")
  game_img = render_game_frame()
  # 画像を常に確実に再描画して表示
  st.image(game_img, use_container_width=True)

with col_ctrl:
  st.subheader(f"⚡ ターン {st.session_state.turn}: アクション選択")

  is_game_over = (
      st.session_state.player_hp <= 0 or st.session_state.boss_hp <= 0
  )

  if not is_game_over:
    # 移動ボタン
    st.text("【移動】位置を変えて攻撃を避ける")
    c1, c2, c3 = st.columns(3)
    with c2:
      if st.button("⬆️ 前進"):
        st.session_state.player_y = max(100, st.session_state.player_y - 20)
        st.session_state.logs.insert(
            0, f"ターン {st.session_state.turn}: 前方に移動した！"
        )
        st.session_state.turn += 1
        st.rerun()
    with c1:
      if st.button("⬅️ 左回避"):
        st.session_state.player_x = max(50, st.session_state.player_x - 35)
        st.session_state.logs.insert(
            0, f"ターン {st.session_state.turn}: 左へ身をかわした！"
        )
        st.session_state.turn += 1
        st.rerun()
    with c3:
      if st.button("➡️ 右回避"):
        st.session_state.player_x = min(450, st.session_state.player_x + 35)
        st.session_state.logs.insert(
            0, f"ターン {st.session_state.turn}: 右へ身をかわした！"
        )
        st.session_state.turn += 1
        st.rerun()

    st.markdown("---")

    # 攻撃アクション
    if st.button("🔥 必殺剣 (ボスにダメージ)", use_container_width=True):
      dmg = random.randint(18, 28)
      st.session_state.boss_hp -= dmg
      st.session_state.logs.insert(
          0,
          f"ターン {st.session_state.turn}: プレイヤーの攻撃！ {dmg}のダメージを与えた。",
      )

      if st.session_state.boss_hp > 0:
        edmg = random.randint(10, 20)
        st.session_state.player_hp -= edmg
        st.session_state.logs.insert(
            0, f"  └ ボスの反撃！ {edmg}のダメージを受けた。"
        )

      st.session_state.turn += 1
      st.rerun()

  else:
    if st.session_state.player_hp <= 0:
      st.error("💀 力尽きました... ゲームオーバー")
    else:
      st.success("🎉 ボスを討伐しました！ 勝利！")

  if st.button("🔄 ゲームリセット", use_container_width=True):
    for key in list(st.session_state.keys()):
      del st.session_state[key]
    st.rerun()

# --- ログ表示 ---
st.markdown("---")
st.subheader("📜 バトルログ")
for log in st.session_state.logs[:4]:
  st.text(log)
