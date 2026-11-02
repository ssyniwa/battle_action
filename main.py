import os
import random
from PIL import Image, ImageDraw
import streamlit as st

# ページの設定（ワイド画面）
st.set_page_config(
    page_title="ダンジョン・ローグアタック：戦略スキル版",
    page_icon="⚔️",
    layout="wide",
)

st.title(
    "⚔️ ダンジョン・ローグアタック：全10ステージ討伐の旅（戦略スキル版）"
)
st.caption(
    "魔術師は遠距離から、戦士と騎士は近距離で戦闘！騎士は移動力抜群！回復や防御スキルを駆使せよ！"
)

# --- ゲーム状態（セッションステート）の初期化 ---
if "initialized" not in st.session_state:
  st.session_state.stage = 1
  # プレイヤー3体のパーティ定義（配置・移動範囲・スキルを最適化）
  st.session_state.players = [
      {
          "name": "戦士アレル",
          "hp": 100,
          "max_hp": 100,
          "x": 400,
          "y": 500,
          "min_x": 200,
          "max_x": 600,
          "move_step": 70,  # 通常の移動量
          "image": "assets/player1.jpg",
          "color": (255, 60, 60),  # 赤
          "action_name": "猛撃の剣気",
          "sub_skill": "ガードスタンス",  # 防御スキル
      },
      {
          "name": "魔術師ミリア",
          "hp": 70,
          "max_hp": 70,
          "x": 600,
          "y": 600,  # 敵から一番遠い後方に配置
          "min_x": 300,
          "max_x": 900,
          "move_step": 70,
          "image": "assets/player2.jpg",
          "color": (60, 150, 255),  # 青
          "action_name": "魔力ブラスト",
          "sub_skill": "ヒール魔法",  # 回復スキル
      },
      {
          "name": "聖騎士レオン",
          "hp": 120,
          "max_hp": 120,
          "x": 800,
          "y": 480,
          "min_x": 150,
          "max_x": 1050,
          "move_step": 120,  # ★ 騎士は移動距離を多めに設定！
          "image": "assets/player3.jpg",
          "color": (255, 220, 50),  # 黄
          "action_name": "ホーリーライト",
          "sub_skill": "聖域の守護",  # 全体防御・軽減スキル
      },
  ]
  st.session_state.current_player_idx = 0  # 現在行動するプレイヤーのインデックス

  # ステージに応じた敵の初期化
  st.session_state.enemy_hp = 70 + (st.session_state.stage * 25)
  st.session_state.enemy_max_hp = st.session_state.enemy_hp
  st.session_state.enemy_x = 600
  st.session_state.enemy_y = 180
  st.session_state.enemy_intent = "line"

  # アニメーション用の状態管理
  st.session_state.anim_type = "none"
  st.session_state.anim_step = 0
  st.session_state.anim_color = (255, 255, 255)
  st.session_state.anim_player_idx = 0

  st.session_state.logs = [
      "第1ステージ開始：魔術師は後方から、戦士と騎士は前線で敵に立ち向かえ！"
  ]
  st.session_state.initialized = True

WIDTH, HEIGHT = 1200, 700

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


# --- 画像を安全に読み込み、滑らか（BICUBIC）にリサイズして配置するヘルパー関数 ---
def paste_image_safely(
    bg_image, img_path, pos, size=(160, 160), fallback_color=(64, 165, 255)
):
  try:
    if os.path.exists(img_path):
      img = Image.open(img_path).convert("RGB")
      img = img.resize(size, Image.Resampling.BICUBIC)
      bg_image.paste(img, (pos[0] - size[0] // 2, pos[1] - size[1] // 2))
      return
  except Exception:
    pass

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


# --- ターン進行＆スキル・アニメーションの処理関数 ---
def process_turn(action_type, log_msg):
  acting_idx = st.session_state.current_player_idx
  current_p = st.session_state.players[acting_idx]
  current_enemy_name = ENEMY_NAMES.get(st.session_state.stage, "敵")

  # アクションに応じたアニメーション設定
  if action_type == "attack":
    st.session_state.anim_type = "player_attack"
    st.session_state.anim_color = current_p["color"]
    st.session_state.anim_player_idx = acting_idx
  elif action_type == "heal":
    st.session_state.anim_type = "player_heal"
    st.session_state.anim_color = (50, 255, 100)  # 緑色の回復エフェクト
    st.session_state.anim_player_idx = acting_idx
  elif action_type == "buff":
    st.session_state.anim_type = "player_buff"
    st.session_state.anim_color = (255, 255, 100)  # 黄色の防御エフェクト
    st.session_state.anim_player_idx = acting_idx
  else:
    st.session_state.anim_type = "enemy_attack"
    st.session_state.anim_color = (255, 50, 50)

  if st.session_state.anim_step < 3:
    st.session_state.anim_step += 1
  else:
    st.session_state.anim_step = 1

  if log_msg:
    st.session_state.logs.insert(0, f"【{current_p['name']}】 {log_msg}")

  # 敵の移動処理
  move_range = min(70, 30 + (st.session_state.stage * 4))
  if current_p["x"] < st.session_state.enemy_x:
    st.session_state.enemy_x -= random.choice([0, move_range // 2, move_range])
  else:
    st.session_state.enemy_x += random.choice([0, move_range // 2, move_range])
  st.session_state.enemy_x = max(250, min(950, st.session_state.enemy_x))

  # --- 攻撃範囲の判定 ---
  hit = False
  intent = st.session_state.enemy_intent

  if intent == "line":
    if abs(current_p["x"] - st.session_state.enemy_x) < 70:
      hit = True
  elif intent == "wide_blast":
    if abs(current_p["x"] - st.session_state.enemy_x) < 180:
      hit = True
  elif intent == "cross_laser":
    if (
        abs(current_p["x"] - st.session_state.enemy_x) < 50
        or 450 < current_p["y"] < 550
    ):
      hit = True
  elif intent == "all_range":
    hit = True

  if hit:
    edmg = random.randint(
        12 + (st.session_state.stage * 3), 22 + (st.session_state.stage * 4)
    )
    # 防御スキル発動中の場合は被ダメージを軽減
    if action_type == "buff":
      edmg = int(edmg * 0.4)
      st.session_state.logs.insert(
          0, f"  🛡️ 防御スキルによりダメージを大幅に軽減した！"
      )

    current_p["hp"] -= edmg
    st.session_state.logs.insert(
        0,
        f"  ⚠️ {current_enemy_name}の攻撃が {current_p['name']}"
        f" に直撃！ {edmg} のダメージ！",
    )
  else:
    st.session_state.logs.insert(
        0, f"  ✨ {current_p['name']} は飛来する攻撃を華麗にかわした！"
    )

  # --- 次の攻撃パターンの抽選 ---
  stage = st.session_state.stage
  if stage <= 2:
    available_intents = ["line"]
  elif stage <= 5:
    available_intents = ["line", "wide_blast"]
  elif stage <= 8:
    available_intents = ["line", "wide_blast", "cross_laser"]
  else:
    available_intents = ["line", "wide_blast", "cross_laser", "all_range"]

  st.session_state.enemy_intent = random.choice(available_intents)

  # ステージクリア・全滅・次キャラ交代の判定
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
      st.session_state.enemy_max_hp = 70 + (st.session_state.stage * 35)
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


# --- 高画質ゲーム画面の描画関数 ---
def render_game_frame():
  image = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 17, 26))
  draw = ImageDraw.Draw(image)

  # 背景グリッド
  for x in range(0, WIDTH, 100):
    draw.line([(x, 0), (x, HEIGHT)], fill=(28, 33, 48), width=2)
  for y in range(0, HEIGHT, 100):
    draw.line([(0, y), (WIDTH, y)], fill=(28, 33, 48), width=2)

  # 1. 敵の攻撃予告エリアの描画
  intent = st.session_state.enemy_intent
  if intent == "line":
    draw.rectangle(
        [
            st.session_state.enemy_x - 60,
            st.session_state.enemy_y + 70,
            st.session_state.enemy_x + 60,
            HEIGHT - 40,
        ],
        outline=(255, 80, 80),
        fill=(80, 20, 20),
    )
  elif intent == "wide_blast":
    draw.rectangle(
        [
            st.session_state.enemy_x - 180,
            st.session_state.enemy_y + 70,
            st.session_state.enemy_x + 180,
            HEIGHT - 40,
        ],
        outline=(255, 50, 50),
        fill=(110, 20, 20),
    )
  elif intent == "cross_laser":
    draw.rectangle(
        [
            st.session_state.enemy_x - 50,
            st.session_state.enemy_y + 70,
            st.session_state.enemy_x + 50,
            HEIGHT - 40,
        ],
        outline=(255, 0, 255),
        fill=(100, 20, 100),
    )
    draw.rectangle(
        [150, 440, 1050, 560], outline=(255, 0, 255), fill=(100, 20, 100)
    )
  elif intent == "all_range":
    draw.rectangle(
        [50, 150, 1150, 650], outline=(255, 255, 0), fill=(150, 50, 0)
    )

  current_stage = st.session_state.get("stage", 1)
  enemy_img_path = f"assets/enemy{current_stage}.jpg"

  # 2. 敵の画像描画
  paste_image_safely(
      image,
      enemy_img_path,
      (st.session_state.enemy_x, st.session_state.enemy_y),
      size=(192, 192),
      fallback_color=(231, 76, 60),
  )

  # 3. プレイヤーの画像描画
  for idx, p in enumerate(st.session_state.players):
    if p["hp"] > 0:
      is_current = idx == st.session_state.current_player_idx
      size = (180, 180) if is_current else (140, 140)
      colors = [(64, 165, 255), (46, 204, 113), (241, 196, 15)]
      paste_image_safely(
          image, p["image"], (p["x"], p["y"]), size=size, fallback_color=colors[idx]
      )

  # 4. アニメーション弾道・スキルの描画
  anim_type = st.session_state.get("anim_type", "none")
  anim_step = st.session_state.get("anim_step", 0)
  anim_color = st.session_state.get("anim_color", (255, 255, 255))
  anim_p_idx = st.session_state.get("anim_player_idx", 0)

  if anim_type != "none" and anim_step > 0:
    acting_p = st.session_state.players[anim_p_idx]
    ex, ey = st.session_state.enemy_x, st.session_state.enemy_y
    px, py = acting_p["x"], acting_p["y"]

    progress_ratio = anim_step / 3.0

    if anim_type == "enemy_attack":
      bx = int(ex + (px - ex) * progress_ratio)
      by = int(ey + (py - ey) * progress_ratio)
      draw.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=(255, 50, 50))
    elif anim_type == "player_attack":
      bx = int(px + (ex - px) * progress_ratio)
      by = int(py + (ey - py) * progress_ratio)
      draw.ellipse([bx - 20, by - 20, bx + 20, by + 20], fill=anim_color)
      draw.text(
          (bx + 25, by - 10),
          f"{acting_p['action_name']}",
          fill=anim_color,
      )
    elif anim_type == "player_heal":
      # 回復の緑エフェクト
      draw.ellipse(
          [px - 50, py - 50, px + 50, py + 50], outline=(50, 255, 100), width=6
      )
      draw.text(
          (px - 30, py - 70), "✨ HP RECOVER", fill=(50, 255, 100)
      )
    elif anim_type == "player_buff":
      # 防御の黄エフェクト
      draw.rectangle(
          [px - 60, py - 60, px + 60, py + 60],
          outline=(255, 255, 100),
          width=6,
      )
      draw.text(
          (px - 30, py - 70), "🛡️ GUARD UP", fill=(255, 255, 100)
      )

  # 5. HPバーの描画
  draw.rectangle([800, 40, 1140, 76], fill=(40, 40, 40))
  e_w = max(
      0,
      int(
          340
          * (
              st.session_state.get("enemy_hp", 100)
              / max(1, st.session_state.get("enemy_max_hp", 100))
          )
      ),
  )
  draw.rectangle([800, 40, 800 + e_w, 76], fill=(231, 76, 60))

  return image


# --- ワイド画面用レイアウト配置 ---
col_game, col_ctrl = st.columns([7, 3])

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
    step = current_p["move_step"]  # キャラごとの移動距離（騎士は大きい）

    st.markdown(
        f"### 👥 手番: <span style='color:rgb{current_p['color']}'>"
        f"{current_p['name']}</span>",
        unsafe_allow_html=True,
    )
    st.progress(max(0.0, current_p["hp"] / current_p["max_hp"]))
    st.text(f"HP: {current_p['hp']} / {current_p['max_hp']}")

    st.markdown("---")
    st.text(f"【移動】エリア内移動 (移動力: {step})")
    c1, c2, c3 = st.columns(3)
    with c2:
      if st.button("⬆️ 前進", use_container_width=True):
        current_p["y"] = max(260, current_p["y"] - 30)
        process_turn("move", "前に踏み込み、攻撃を回避した！")
    with c1:
      if st.button("⬅️ 左", use_container_width=True):
        current_p["x"] = max(current_p["min_x"], current_p["x"] - step)
        process_turn("move", f"エリア内で左へ大きく回避した！")
    with c3:
      if st.button("➡️ 右", use_container_width=True):
        current_p["x"] = min(current_p["max_x"], current_p["x"] + step)
        process_turn("move", f"エリア内で右へ大きく回避した！")

    st.markdown("---")
    st.text("【スキル選択】")

    # 1. 攻撃スキルボタン
    if st.button(
        f"🔥 {current_p['action_name']} (攻撃)", use_container_width=True
    ):
      dmg = random.randint(25, 40)
      st.session_state.enemy_hp -= dmg
      process_turn(
          "attack",
          f"{current_p['action_name']}を放ち、敵に {dmg} のダメージを与えた！",
      )

    # 2. 回復または防御スキルボタン（キャラごとに分岐）
    if current_p["name"] == "魔術師ミリア":
      if st.button("💚 ヒール魔法 (味方回復)", use_container_width=True):
        heal_val = random.randint(25, 40)
        # 最もHPが減っている味方を回復
        target = min(
            st.session_state.players,
            key=lambda p: p["hp"] / max(1, p["max_hp"]),
        )
        target["hp"] = min(target["max_hp"], target["hp"] + heal_val)
        process_turn(
            "heal", f"ヒール魔法で {target['name']} のHPを {heal_val} 回復した！"
        )
    elif current_p["name"] == "戦士アレル":
      if st.button("🛡️ ガードスタンス (防御)", use_container_width=True):
        process_turn(
            "buff",
            "ガードスタンスを展開し、次の敵からのダメージを大幅に軽減する！",
        )
    elif current_p["name"] == "聖騎士レオン":
      if st.button("✨ 聖域の守護 (全体守備)", use_container_width=True):
        # 騎士は自分とパーティのHPを少し回復しつつ防御
        current_p["hp"] = min(
            current_p["max_hp"], current_p["hp"] + 20
        )
        process_turn(
            "buff",
            "聖域の守護を発動！自身のHPを回復し、鉄壁の守りを固めた！",
        )

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
