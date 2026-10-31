import random
from PIL import Image, ImageDraw
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="ダンジョン・ローグアタック", page_icon="⚔️", layout="centered"
)

st.title("⚔️ ダンジョン・ローグアタック (Streamlit版)")
st.caption("Pillowで描画エンジンを構築した、クラウド対応のハイブリッド型RPGアクション！")

# --- セッションステート（ゲーム状態）の初期化 ---
if "player_hp" not in st.session_state:
  st.session_state.player_hp = 100
  st.session_state.enemy_hp = 100
  st.session_state.turn = 1
  st.session_state.player_x = 80
  st.session_state.enemy_x = 380
  st.session_state.logs = ["暗いダンジョンに足を踏み入れた... 敵が現れた！"]

WIDTH, HEIGHT = 500, 300


# --- ゲーム画面を描画する関数 (Pillow処理) ---
def render_game_frame():
  # 背景画像を作成（ダンジョンの床・壁風の色）
  image = Image.new("RGB", (WIDTH, HEIGHT), color=(20, 24, 33))
  draw = ImageDraw.Draw(image)

  # グリッド線の描画
  for x in range(0, WIDTH, 50):
    draw.line([(x, 0), (x, HEIGHT)], fill=(35, 40, 55), width=1)
  for y in range(0, HEIGHT, 50):
    draw.line([(0, y), (WIDTH, y)], fill=(35, 40, 55), width=1)

  # プレイヤーキャラ（青い四角）
  p_x = st.session_state.player_x
  p_y = HEIGHT // 2 - 25
  draw.rectangle(
      [p_x, p_y, p_x + 40, p_y + 50], fill=(64, 165, 255), outline=None
  )
  # プレイヤーの目
  draw.rectangle([p_x + 25, p_y + 10, p_x + 33, p_y + 18], fill=(255, 255, 255))

  # モンスターキャラ（赤い四角）
  e_x = st.session_state.enemy_x
  e_y = HEIGHT // 2 - 25
  draw.rectangle(
      [e_x, e_y, e_x + 40, e_y + 50], fill=(255, 85, 85), outline=None
  )
  # モンスターの目
  draw.rectangle([e_x + 8, e_y + 10, e_x + 16, e_y + 18], fill=(255, 255, 255))

  # HPバーの背景
  draw.rectangle([30, 20, 180, 36], fill=(60, 60, 60))
  draw.rectangle([320, 20, 470, 36], fill=(60, 60, 60))

  # HPバー（プレイヤー：緑）
  p_hp_width = max(0, int(150 * (st.session_state.player_hp / 100)))
  if p_hp_width > 0:
    draw.rectangle([30, 20, 30 + p_hp_width, 36], fill=(46, 204, 113))

  # HPバー（モンスター：赤）
  e_hp_width = max(0, int(150 * (st.session_state.enemy_hp / 100)))
  if e_hp_width > 0:
    draw.rectangle([320, 20, 320 + e_hp_width, 36], fill=(231, 76, 60))

  return image


# --- レイアウト構築 ---
col_game, col_ctrl = st.columns([3, 2])

with col_game:
  st.subheader("🎮 バトルフィールド")
  # Pillowで作った画像をそのままStreamlitで表示
  game_image = render_game_frame()
  st.image(game_image, use_container_width=True)

with col_ctrl:
  st.subheader("⚡ アクション選択")

  is_game_over = (
      st.session_state.player_hp <= 0 or st.session_state.enemy_hp <= 0
  )

  if not is_game_over:
    if st.button("⚔️ 通常攻撃 (強撃)", use_container_width=True):
      dmg = random.randint(15, 25)
      st.session_state.enemy_hp -= dmg
      st.session_state.logs.insert(
          0,
          f"ターン {st.session_state.turn}: プレイヤーの攻撃！ {dmg}のダメージ。",
      )

      if st.session_state.enemy_hp > 0:
        edmg = random.randint(10, 20)
        st.session_state.player_hp -= edmg
        st.session_state.logs.insert(
            0, f"  └ モンスターの反撃！ {edmg}のダメージを受けた。"
        )
      st.session_state.turn += 1
      st.rerun()

    if st.button("🛡️ 回避 & 接近", use_container_width=True):
      st.session_state.player_x = min(
          st.session_state.enemy_x - 45, st.session_state.player_x + 30
      )
      st.session_state.logs.insert(
          0,
          f"ターン {st.session_state.turn}: 前方に踏み込み、被ダメージを抑えた！",
      )
      st.session_state.turn += 1
      st.rerun()

    if st.button("🧪 ポーション使用 (回復)", use_container_width=True):
      st.session_state.player_hp = min(100, st.session_state.player_hp + 35)
      st.session_state.logs.insert(
          0, f"ターン {st.session_state.turn}: ポーションでHPが35回復した！"
      )
      st.session_state.turn += 1
      st.rerun()
  else:
    if st.session_state.player_hp <= 0:
      st.error("💀 ゲームオーバー... 敗北しました。")
    else:
      st.success("🎉 討伐成功！ ダンジョンをクリアした！")

  if st.button("🔄 ゲームリセット", use_container_width=True):
    st.session_state.player_hp = 100
    st.session_state.enemy_hp = 100
    st.session_state.turn = 1
    st.session_state.player_x = 80
    st.session_state.logs = ["新しい冒険が始まった。"]
    st.rerun()

# --- ログ表示セクション ---
st.markdown("---")
st.subheader("📜 冒険の記録 (ログ)")
for log in st.session_state.logs[:4]:
  st.text(log)
