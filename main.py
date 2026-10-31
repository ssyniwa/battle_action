import numpy as np
import pygame
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="ダンジョン・ローグアタック", page_icon="⚔️", layout="centered"
)

st.title("⚔️ ダンジョン・ローグアタック (Pygame × Streamlit)")
st.caption(
    "Pygameの描画エンジンとStreamlitのボタン操作を融合させたハイブリッド型RPGアクション！"
)

# Pygameの初期化（ウィンドウは開かず、内部サーフェスのみ使用）
pygame.init()
WIDTH, HEIGHT = 500, 300
surface = pygame.Surface((WIDTH, HEIGHT))

# --- セッションステート（ゲーム状態）の初期化 ---
if "player_hp" not in st.session_state:
  st.session_state.player_hp = 100
  st.session_state.enemy_hp = 100
  st.session_state.turn = 1
  st.session_state.player_x = 80
  st.session_state.enemy_x = 380
  st.session_state.logs = ["暗いダンジョンに足を踏み入れた... 敵が現れた！"]


# --- ゲーム画面を描画する関数 (Pygame処理) ---
def render_game_frame():
  # 背景（ダンジョンの床・壁風）
  surface.fill((20, 24, 33))

  # グリッド線の描画
  for x in range(0, WIDTH, 50):
    pygame.draw.line(surface, (35, 40, 55), (x, 0), (x, HEIGHT), 1)
  for y in range(0, HEIGHT, 50):
    pygame.draw.line(surface, (35, 40, 55), (0, y), (WIDTH, y), 1)

  # プレイヤーキャラ（青い四角 / またはサークル）
  pygame.draw.rect(
      surface,
      (64, 165, 255),
      (st.session_state.player_x, HEIGHT // 2 - 25, 40, 50),
      border_radius=8,
  )
  # プレイヤーの目・装飾
  pygame.draw.rect(
      surface,
      (255, 255, 255),
      (st.session_state.player_x + 25, HEIGHT // 2 - 15, 8, 8),
  )

  # モンスターキャラ（赤い四角）
  pygame.draw.rect(
      surface,
      (255, 85, 85),
      (st.session_state.enemy_x, HEIGHT // 2 - 25, 40, 50),
      border_radius=8,
  )
  pygame.draw.rect(
      surface,
      (255, 255, 255), (st.session_state.enemy_x + 8, HEIGHT // 2 - 15, 8, 8)
  )

  # HPバーの背景
  pygame.draw.rect(surface, (60, 60, 60), (30, 20, 150, 16), border_radius=4)
  pygame.draw.rect(surface, (60, 60, 60), (320, 20, 150, 16), border_radius=4)

  # HPバー（プレイヤー：緑）
  p_hp_width = max(0, int(150 * (st.session_state.player_hp / 100)))
  pygame.draw.rect(surface, (46, 204, 113), (30, 20, p_hp_width, 16), border_radius=4)

  # HPバー（モンスター：赤）
  e_hp_width = max(0, int(150 * (st.session_state.enemy_hp / 100)))
  pygame.draw.rect(surface, (231, 76, 60), (320, 20, e_hp_width, 16), border_radius=4)

  # --- PygameのSurfaceをStreamlit用にNumPy配列に変換 ---
  # Pygameの配列形状 (Width, Height, 3) を Streamlit (Height, Width, 3) に転置する
  raw_array = pygame.surfarray.array3d(surface)
  return np.transpose(raw_array, (1, 0, 2))


# --- レイアウト構築 ---
col_game, col_ctrl = st.columns([3, 2])

with col_game:
  st.subheader("🎮 バトルフィールド")
  # Pygameで描画したフレームを画像として表示
  game_frame = render_game_frame()
  st.image(game_frame, use_container_width=True)

with col_ctrl:
  st.subheader("⚡ アクション選択")

  # ゲームオーバー・クリア判定
  is_game_over = (
      st.session_state.player_hp <= 0 or st.session_state.enemy_hp <= 0
  )

  if not is_game_over:
    if st.button("⚔️ 通常攻撃 (強撃)", use_container_width=True):
      dmg_to_enemy = np.randint(15, 25) if hasattr(np, "randint") else 20
      st.session_state.enemy_hp -= 20
      st.session_state.logs.insert(
          0, f"ターン {st.session_state.turn}: プレイヤーの攻撃！ 20のダメージ。"
      )

      if st.session_state.enemy_hp > 0:
        st.session_state.player_hp -= 15
        st.session_state.logs.insert(
            0, f"  └ モンスターの反撃！ 15のダメージを受けた。"
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
