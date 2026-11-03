import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(
    page_title="ダンジョン・ローグアタック：リアルタイム弾幕アクション",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ ダンジョン・ローグアタック：全10ステージ討伐の旅")
st.markdown("---")

# --- セッションステートの初期化 ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "stage" not in st.session_state:
    st.session_state.stage = 1
if "players" not in st.session_state:
    st.session_state.players = [
        {"name": "戦士アレル", "hp": 100, "maxHp": 100, "color": "#ff4444", "file": "assets/player1.jpg"},
        {"name": "魔術師ミリア", "hp": 70, "maxHp": 70, "color": "#4488ff", "file": "assets/player2.jpg"},
        {"name": "聖騎士レオン", "hp": 120, "maxHp": 120, "color": "#ffcc00", "file": "assets/player3.jpg"}
    ]
if "active_player_idx" not in st.session_state:
    st.session_state.active_player_idx = 0

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
    10: "魔界の君主・魔王"
}

# ローカル画像ファイルをBase64データURIに変換するヘルパー関数
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return "data:image/jpeg;base64," + base64.b64encode(data).decode("utf-8")
    return ""

current_stage = st.session_state.stage
current_enemy_name = ENEMY_NAMES.get(current_stage, "強敵")
active_p = st.session_state.players[st.session_state.active_player_idx]

# 画像パスの取得
player_img_base64 = get_image_base64(active_p["file"])
enemy_img_path = f"assets/enemy{current_stage}.jpg"
enemy_img_base64 = get_image_base64(enemy_img_path)

# --- UI コントロール・ステータス表示 ---
col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 2])

with col1:
    st.markdown(f"### 📍 Stage {current_stage}/10")
    st.write(f"**{current_enemy_name}**")

with col2:
    st.markdown(f"### 🕹️ 出撃中")
    st.markdown(f"<span style='color:{active_p['color']}; font-weight:bold;'>{active_p['name']}</span>", unsafe_allow_html=True)
    st.write(f"HP: {active_p['hp']} / {active_p['maxHp']}")

with col3:
    st.markdown("### 👥 パーティ生存状況")
    status_list = []
    for i, p in enumerate(st.session_state.players):
        status = "🟢 生存" if p["hp"] > 0 else "🔴 戦闘不能"
        prefix = "👉 " if i == st.session_state.active_player_idx else ""
        status_list.append(f"{prefix}{p['name']}: {status} ({p['hp']}HP)")
    st.write(" | ".join(status_list))

with col4:
    st.markdown("### 🎮 バトル制御")
    if not st.session_state.game_started:
        if st.button("🔥 戦闘開始", use_container_width=True, type="primary"):
            if active_p["hp"] > 0:
                st.session_state.game_started = True
                st.rerun()
            else:
                st.error("現在のキャラクターは戦闘不能です！別のキャラに交代してください。")
    else:
        if st.button("⏸️ 中断 / 一時停止", use_container_width=True):
            st.session_state.game_started = False
            st.rerun()

with col5:
    st.markdown("### ⚙️ その他")
    if st.button("🔄 ゲームリセット", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("---")

# キャラクター手動切り替え選択肢
st.markdown("#### 👥 出撃キャラクターの手動選択・交代")
char_cols = st.columns(len(st.session_state.players))
for i, p in enumerate(st.session_state.players):
    with char_cols[i]:
        btn_label = f"選ぶ: {p['name']} ({p['hp']}HP)" if p["hp"] > 0 else f"{p['name']} (戦闘不能)"
        disabled = (p["hp"] <= 0)
        if st.button(btn_label, disabled=disabled, use_container_width=True):
            st.session_state.active_player_idx = i
            st.session_state.game_started = False
            st.rerun()

st.markdown("---")
st.caption("【操作方法】 左右矢印キー（または A/Dキー）で自機を移動 ｜ **Zキー**で攻撃弾を発射！ ｜ 敵も自機も滑らかに移動します！")

if not st.session_state.game_started:
    st.info("👆 上の **「戦闘開始」** ボタンを押すとバトルがスタートします！")
else:
    # --- HTML5 Canvas ＆ JavaScript によるリアルタイム・バトルゲーム ---
    game_html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {
                background-color: #0f111a;
                color: white;
                text-align: center;
                font-family: sans-serif;
                margin: 0;
                padding: 0;
            }
            canvas {
                background: #151824;
                border: 2px solid #28313c;
                box-shadow: 0 0 25px rgba(0,0,0,0.9);
                display: block;
                margin: 0 auto;
            }
        </style>
    </head>
    <body>
        <canvas id="gameCanvas" width="1100" height="480"></canvas>
        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            // 画像の読み込み（Base64）
            const playerImg = new Image();
            playerImg.src = "PLAYER_IMG_B64";
            let playerLoaded = false;
            playerImg.onload = () => { playerLoaded = true; };

            const enemyImg = new Image();
            enemyImg.src = "ENEMY_IMG_B64";
            let enemyLoaded = false;
            enemyImg.onload = () => { enemyLoaded = true; };

            let stage = STAGE_NUM;
            let player = { 
                x: 550, y: 390, size: 60, speed: 7, 
                hp: PLAYER_HP, maxHp: PLAYER_MAXHP, 
                name: "PLAYER_NAME", color: "PLAYER_COLOR" 
            };
            
            let enemy = { 
                x: 550, y: 90, size: 90, 
                hp: 80 + (stage * 35), maxHp: 80 + (stage * 35),
                name: "ENEMY_NAME",
                moveTimer: 0
            };
            
            let bullets = [];
            let playerBullets = [];
            
            let keys = {};
            let frameCount = 0;
            let isGameOver = false;
            let isCleared = false;

            window.addEventListener("keydown", (e) => {
                keys[e.code] = true;
                if ((e.code === "KeyZ" || e.code === "KeyY") && !isGameOver && !isCleared) {
                    shootPlayerBullet();
                    e.preventDefault();
                }
            });
            window.addEventListener("keyup", (e) => {
                keys[e.code] = false;
            });

            function shootPlayerBullet() {
                playerBullets.push({
                    x: player.x,
                    y: player.y - 30,
                    vx: 0,
                    vy: -13,
                    size: 8
                });
            }

            function spawnEnemyBullets() {
                let freq = Math.max(12, 40 - (stage * 3));
                if (frameCount % freq === 0) {
                    let count = 4 + Math.floor(stage / 2);
                    for (let i = 0; i < count; i++) {
                        let angle = (Math.PI / (count + 1)) * (i + 1);
                        let speed = 3.0 + (stage * 0.35);
                        bullets.push({
                            x: enemy.x,
                            y: enemy.y + 40,
                            vx: Math.cos(angle) * speed + (Math.random() - 0.5) * 1.5,
                            vy: Math.sin(angle) * speed + 1.5,
                            size: 8
                        });
                    }
                }
            }

            function update() {
                if (isGameOver || isCleared) return;

                if ((keys["ArrowLeft"] || keys["KeyA"]) && player.x > player.size / 2) {
                    player.x -= player.speed;
                }
                if ((keys["ArrowRight"] || keys["KeyD"]) && player.x < canvas.width - player.size / 2) {
                    player.x += player.speed;
                }

                # 敵キャラのダイナミックな移動アニメーション
                enemy.moveTimer += 0.05 + (stage * 0.006);
                enemy.x = 550 + Math.sin(enemy.moveTimer) * (220 + stage * 12);

                spawnEnemyBullets();

                for (let i = bullets.length - 1; i >= 0; i--) {
                    let b = bullets[i];
                    b.x += b.vx;
                    b.y += b.vy;

                    let dist = Math.hypot(b.x - player.x, b.y - player.y);
                    if (dist < (player.size / 2 + b.size - 8)) {
                        player.hp -= (10 + stage * 2);
                        bullets.splice(i, 1);
                        if (player.hp <= 0) {
                            isGameOver = true;
                        }
                        continue;
                    }

                    if (b.y > canvas.height || b.x < 0 || b.x > canvas.width) {
                        bullets.splice(i, 1);
                    }
                }

                for (let i = playerBullets.length - 1; i >= 0; i--) {
                    let pb = playerBullets[i];
                    pb.x += pb.vx;
                    pb.y += pb.vy;

                    let dist = Math.hypot(pb.x - enemy.x, pb.y - enemy.y);
                    if (dist < (enemy.size / 2 + pb.size)) {
                        enemy.hp -= 15;
                        playerBullets.splice(i, 1);
                        if (enemy.hp <= 0) {
                            isCleared = true;
                        }
                        continue;
                    }

                    if (pb.y < 0) {
                        playerBullets.splice(i, 1);
                    }
                }

                frameCount++;
            }

            function draw() {
                ctx.fillStyle = "#0f111a";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.strokeStyle = "#1c2130";
                ctx.lineWidth = 1;
                for (let x = 0; x < canvas.width; x += 50) {
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
                }
                for (let y = 0; y < canvas.height; y += 50) {
                    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
                }

                # 敵画像の描画（動くアニメーション）
                if (enemyLoaded) {
                    ctx.drawImage(enemyImg, enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size);
                } else {
                    ctx.fillStyle = "#e74c3c";
                    ctx.beginPath(); ctx.arc(enemy.x, enemy.y, enemy.size/2, 0, Math.PI*2); ctx.fill();
                }

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 14px sans-serif";
                ctx.fillText(`Stage STAGE_NUM: ${enemy.name}`, enemy.x, enemy.y - 58);

                ctx.fillStyle = "#333";
                ctx.fillRect(enemy.x - 65, enemy.y - 48, 130, 10);
                ctx.fillStyle = "#e74c3c";
                ctx.fillRect(enemy.x - 65, enemy.y - 48, 130 * (Math.max(0, enemy.hp) / enemy.maxHp), 10);

                # 自機画像の描画（動くアニメーション）
                if (playerLoaded) {
                    ctx.drawImage(playerImg, player.x - player.size/2, player.y - player.size/2, player.size, player.size);
                } else {
                    ctx.fillStyle = player.color;
                    ctx.beginPath(); ctx.arc(player.x, player.y, player.size/2, 0, Math.PI*2); ctx.fill();
                }

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px sans-serif";
                ctx.fillText(player.name, player.x, player.y + 46);

                ctx.fillStyle = "#333";
                ctx.fillRect(player.x - 40, player.y + 53, 80, 9);
                ctx.fillStyle = "#2ecc71";
                ctx.fillRect(player.x - 40, player.y + 53, 80 * (Math.max(0, player.hp) / player.maxHp), 9);

                ctx.fillStyle = "#ff3355";
                for (let b of bullets) {
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
                    ctx.fill();
                }

                ctx.fillStyle = "#33eeff";
                for (let pb of playerBullets) {
                    ctx.beginPath();
                    ctx.arc(pb.x, pb.y, pb.size, 0, Math.PI * 2);
                    ctx.fill();
                }

                if (isGameOver) {
                    ctx.fillStyle = "rgba(0, 0, 0, 0.88)";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = "#ff3333";
                    ctx.font = "bold 38px sans-serif";
                    ctx.fillText(`${player.name} が倒れました！`, canvas.width / 2, canvas.height / 2 - 20);
                    ctx.font = "18px sans-serif";
                    ctx.fillStyle = "#fff";
                    ctx.fillText("上の「中断」ボタンを押して仲間と交代してください", canvas.width / 2, canvas.height / 2 + 25);
                } else if (isCleared) {
                    ctx.fillStyle = "rgba(0, 0, 0, 0.88)";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = "#2ecc71";
                    ctx.font = "bold 38px sans-serif";
                    ctx.fillText("STAGE CLEAR!!", canvas.width / 2, canvas.height / 2 - 20);
                    ctx.font = "18px sans-serif";
                    ctx.fillStyle = "#fff";
                    ctx.fillText("下のボタンを押して次のステージへ進んでください", canvas.width / 2, canvas.height / 2 + 25);
                }
            }

            function loop() {
                update();
                draw();
                requestAnimationFrame(loop);
            }

            loop();
        </script>
    </body>
    </html>
    """

    game_html = game_html_template        .replace("PLAYER_IMG_B64", player_img_base64)        .replace("ENEMY_IMG_B64", enemy_img_base64)        .replace("STAGE_NUM", str(current_stage))        .replace("PLAYER_HP", str(active_p['hp']))        .replace("PLAYER_MAXHP", str(active_p['maxHp']))        .replace("PLAYER_NAME", active_p['name'])        .replace("PLAYER_COLOR", active_p['color'])        .replace("ENEMY_NAME", current_enemy_name)

    components.html(game_html, height=500)

# --- ステージクリア / キャラクター交代ボタンの制御セクション ---
st.markdown("---")
ctrl_col1, ctrl_col2 = st.columns(2)

with ctrl_col1:
    if st.button("⚔️ 次のステージへ進む（ステージ進行）", use_container_width=True, type="primary"):
        if current_stage < 10:
            st.session_state.stage += 1
            st.session_state.game_started = False
            st.success(f"ステージ {st.session_state.stage} に進みます！「戦闘開始」を押してください。")
            st.rerun()
        else:
            st.success("🎉 全10ステージ完全踏破！魔王を討伐しました！")

with ctrl_col2:
    if st.button("👥 倒れたキャラを控えにして次の仲間と交代", use_container_width=True):
        st.session_state.players[st.session_state.active_player_idx]["hp"] = 0
        st.session_state.game_started = False
        
        next_idx = None
        for i, p in enumerate(st.session_state.players):
            if p["hp"] > 0:
                next_idx = i
                break
        
        if next_idx is not None:
            st.session_state.active_player_idx = next_idx
            st.success(f"生存している **{st.session_state.players[next_idx]['name']}** に交代しました！")
            st.rerun()
        else:
            st.error("💀 パーティメンバーが全員戦闘不能（全滅）になりました... ゲームリセットしてください。")
