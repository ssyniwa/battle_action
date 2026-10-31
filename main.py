import random
from PIL import Image, ImageDraw
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ページの設定
st.set_page_config(
    page_title="ダンジョン・ローグアタック：弾幕サバイバル",
    page_icon="🎯",
    layout="centered",
)

st.title("🎯 ダンジョン・ローグアタック：弾幕サバイバル")
st.caption(
    "リアルタイムに迫りくる弾幕を避けながら、スキルを駆使してボスを討伐せよ！"
)

# 0.1秒（100ミリ秒）ごとに自動リフレッシュ（リアルタイム動作用）
count = st_autorefresh(interval=100, limit=None, key="datank_loop")

# --- ゲーム状態（セッションステート）の初期化 ---
if "initialized" not in st.session_state:
  st.session_state.player_hp = 100
  st.session_state.boss_hp = 100
  st.session_state.player_x = 250
  st.session_state.player_y = 220
  st.session_state.bullets = (
      []
  )  # 弾幕リスト: [{'x': int, 'y': int, 'vx': float, 'vy': float}]
  st.session_state.score = 0
  st.session_state.game_over = False
  st.session_state.win = False
  st.session_state.initialized = True

WIDTH, HEIGHT = 500, 300

# --- ドット絵のパターン定義（16x16ピクセル等を簡易表現） ---
# 1: プレイヤー（青系ドット）, 2: ボス（赤系ドット）
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
  """ドット絵のパターンを指定座標に拡大描画する関数"""
  if color_map is None:
    color_map = {"1": (64, 165, 255), "2": (231, 76, 60)}

  for r_idx, row in enumerate(dot_pattern):
    for c_idx, char in enumerate(row):
      if char in color_map:
        x0 = start_x + (c_idx * scale)
        y0 = start_y + (r_idx * scale)
        x1 = x0 + scale
        y1 = y0 + scale
        draw.rectangle([x0, y0, x1, y1], fill=color_map[char])


# --- 弾幕の生成と更新（リアルタイム処理） ---
if not st.session_state.game_over and not st.session_state.win:
  # 一定確率でボスから新しい弾を発射
  if random.random() < 0.4:
    b_x, b_y = 250, 50  # ボスの位置付近から発射
    # プレイヤーに向かうベクトルを計算
    angle = random.uniform(0.5, 2.5)  # 下方向へのランダムな角度
    speed = random.randint(4, 7)
    vx = speed * random.choice([-0.8, -0.4, 0, 0.4, 0.8])
    vy = speed
    st.session_state.bullets.append({"x": b_x, "y": b_y, "vx": vx, "vy": vy})

  # 弾の位置を更新
  new_bullets = []
  for b in st.session_state.bullets:
    b["x"] += b["vx"]
    b["y"] += b["vy"]

    # 画面内にある弾だけ保持
    if 0 <= b["x"] <= WIDTH and 0 <= b["y"] <= HEIGHT:
      # プレイヤーとの当たり判定（簡易的に中心距離で判定）
      dist = ((b["x"] - st.session_state.player_x) ** 2 + (b["y"] - st.session_state.player_y) ** 2) ** 0.5
      if dist < 18:
        st.session_state.player_hp -= 5  # 被弾ダメージ
        if st.session_state.player_hp <= 0:
          st.session_state.game_over = True
      else:
        new_bullets.append(b)
  st.session_state.bullets = new_bullets

  # スコア（生存時間・回避ボーナス）を加算
  st.session_state.score += 1


# --- ゲーム画面の描画関数 ---
def render_game_frame():
  image = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 17, 26))
  draw = ImageDraw.Draw(image)

  # ダンジョンの背景グリッド
  for x in range(0, WIDTH, 40):
    draw.line([(x, 0), (x, HEIGHT)], fill=(28, 33, 48), width=1)
  for y in range(0, HEIGHT, 40):
    draw.line([(0, y), (WIDTH, y)], fill=(28, 33, 48), width=1)

  # ボス（中央上部）の描画（ドット絵）
  draw_dot_sprite(
      draw, BOSS_DOTS, start_x=235, start_y=30, scale=3, color_map={"2": (255, 85, 85)}
  )

  # プレイヤー（操作キャラ）の描画（ドット絵）
  draw_dot_sprite(
      draw,
      PLAYER_DOTS,
      start_x=st.session_state.player_x - 18,
      start_y=st.session_state.player_y - 12,
      scale=3,
      color_map={"1": (64, 165, 255), "2": (46, 204, 113)},
  )

  # 弾幕（敵の攻撃弾）の描画
  for b in st.session_state.bullets:
    bx, by = int(b["x"]), int(b["y"])
    draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 200, 50))

  # ステータスバー（HP）
  # プレイヤーHPバー
  draw.rectangle([20, 20, 140, 32], fill=(40, 40, 40))
  p_w = max(0, int(120 * (st.session_state.player_hp / 100)))
  draw.rectangle([20, 20, 20 + p_w, 32], fill=(46, 204, 113))

  # ボスHPバー
  draw.rectangle([360, 20, 480, 32], fill=(40, 40, 40))
  b_w = max(0, int(120 * (st.session_state.boss_hp / 100)))
  draw.rectangle([360, 20, 360 + b_w, 32], fill=(231, 76, 60))

  return image


# --- レイアウト配置 ---
col_game, col_ctrl = st.columns([3, 2])

with col_game:
  st.subheader(f"🎮 バトルフィールド (スコア: {st.session_state.score})")
  game_img = render_game_frame()
  st.image(game_img, use_container_width=True)

with col_ctrl:
  st.subheader("⚡ 移動・アクション")

  if not st.session_state.game_over and not st.session_state.win:
    # 十字移動ボタン（弾を避けるための操作）
    c1, c2, c3 = st.columns(3)
    with c2:
      if st.button("⬆️ 上"):
        st.session_state.player_y = max(100, st.session_state.player_y - 25)
    with c1:
      if st.button("⬅️ 左"):
        st.session_state.player_x = max(30, st.session_state.player_x - 30)
    with c3:
      if st.button("➡️ 右"):
        st.session_state.player_x = min(470, st.session_state.player_x + 30)
    c4, c5, c6 = st.columns(3)
    with c5:
      if st.button("⬇️ 下"):
        st.session_state.player_y = min(270, st.session_state.player_y + 25)

    st.markdown("---")

    # 攻撃アクションボタン
    if st.button("🔥 スペルカード (ボスに大ダメージ)", use_container_width=True):
      dmg = random.randint(15, 25)
      st.session_state.boss_hp -= dmg
      if st.session_state.boss_hp <= 0:
        st.session_state.win = True
      st.rerun()

  else:
    if st.session_state.game_over:
      st.error("💀 弾幕に倒れました... ゲームオーバー")
    elif st.session_state.win:
      st.success("🎉 ボスを撃破しました！ クリアおめでとう！")

  if st.button("🔄 ゲームリセット", use_container_width=True):
    st.session_state.player_hp = 100
    st.session_state.boss_hp = 100
    st.session_state.player_x = 250
    st.session_state.player_y = 220
    st.session_state.bullets = []
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.win = False
    st.rerun()
