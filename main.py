import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(
    page_title="ダンジョン・ローグアタック：リアルタイム弾幕アクション",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ ダンジョン・ローグアタック：全10ステージ討伐の旅（強化弾幕＆キャラ別固有攻撃版）")
st.markdown("---")

# --- セッションステートの初期化 ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "stage" not in st.session_state:
    st.session_state.stage = 1
if "players" not in st.session_state:
    st.session_state.players = [
        {"name": "戦士アレル", "hp": 100, "maxHp": 100, "color": "#ff4444", "file": "assets/player1.jpg", "style": "laser"},
        {"name": "魔術師ミリア", "hp": 70, "maxHp": 70, "color": "#4488ff", "file": "assets/player2.jpg", "style": "orb"},
        {"name": "聖騎士レオン", "hp": 120, "maxHp": 120, "color": "#ffcc00", "file": "assets/player3.jpg", "style": "slash"}
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

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return "data:image/jpeg;base64," + base64.b64encode(data).decode("utf-8")
    return ""

current_stage = st.session_state.stage
current_enemy_name = ENEMY_NAMES.get(current_stage, "強敵")
active_p = st.session_state.players[st.session_state.active_player_idx]

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
    attack_desc = {"laser": "レーザー光線", "orb": "魔法弾", "slash": "剣撃"}[active_p['style']]
    st.markdown(f"<span style='color:{active_p['color']}; font-weight:bold;'>{active_p['name']}</span> ({attack_desc})", unsafe_allow_html=True)
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

st.markdown("#### 👥 出撃キャラクターの手動選択・交代")
char_cols = st.columns(len(st.session_state.players))
for i, p in enumerate(st.session_state.players):
    with char_cols[i]:
        style_name = {"laser": "レーザー", "orb": "魔法弾", "slash": "剣撃"}[p['style']]
        btn_label = f"選ぶ: {p['name']} [{style_name}] ({p['hp']}HP)" if p["hp"] > 0 else f"{p['name']} (戦闘不能)"
        disabled = (p["hp"] <= 0)
        if st.button(btn_label, disabled=disabled, use_container_width=True):
            st.session_state.active_player_idx = i
            st.session_state.game_started = False
            st.rerun()

st.markdown("---")
st.markdown("""
**【戦闘ガイド】**
* **操作方法**: 左右矢印キー（または A/Dキー）で自機移動 ｜ **Zキー**でキャラクター固有攻撃発射！
* **キャラ別攻撃スタイル**:
  * 🔴 **戦士アレル**: 直線を貫く高速の **「レーザー光線」**
  * 🔵 **魔術師ミリア**: 追尾または広範囲に広がる **「魔法弾」**
  * 🟡 **聖騎士レオン**: 敵を切り裂くワイドな衝撃波の **「剣撃」**
* **ステージ強化**: ステージが進むにつれて、敵のHP増加だけでなく、**弾数増加・全方位放射弾・スパイラル弾・レーザー弾幕**へと敵の攻撃が激化します！
""")

if not st.session_state.game_started:
    st.info("👆 上の **「戦闘開始」** ボタンを押すとバトルがスタートします！")
else:
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
                name: "PLAYER_NAME", color: "PLAYER_COLOR", style: "PLAYER_STYLE" 
            };
            
            let enemy = { 
                x: 550, y: 90, size: 90, 
                hp: 90 + (stage * 45), maxHp: 90 + (stage * 45),
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
                    shootPlayerAttack();
                    e.preventDefault();
                }
            });
            window.addEventListener("keyup", (e) => {
                keys[e.code] = false;
            });

            // キャラクターごとの攻撃スタイル発射関数
            function shootPlayerAttack() {
                if (player.style === "laser") {
                    // 戦士アレル：高速レーザー光線（細長く鋭い光線）
                    playerBullets.push({
                        x: player.x,
                        y: player.y - 30,
                        vx: 0,
                        vy: -18,
                        width: 6,
                        height: 30,
                        type: "laser",
                        damage: 22
                    });
                } else if (player.style === "orb") {
                    // 魔術師ミリア：魔法弾（左右に少し広がる2発の魔弾）
                    playerBullets.push({
                        x: player.x - 12,
                        y: player.y - 25,
                        vx: -0.5,
                        vy: -12,
                        size: 8,
                        type: "orb",
                        damage: 14
                    });
                    playerBullets.push({
                        x: player.x + 12,
                        y: player.y - 25,
                        vx: 0.5,
                        vy: -12,
                        size: 8,
                        type: "orb",
                        damage: 14
                    });
                } else if (player.style === "slash") {
                    // 聖騎士レオン：剣撃（ワイドな三日月状の衝撃波）
                    playerBullets.push({
                        x: player.x,
                        y: player.y - 30,
                        vx: 0,
                        vy: -10,
                        width: 36,
                        height: 14,
                        type: "slash",
                        damage: 28
                    });
                }
            }

            // ステージごとに強化・進化する敵の弾幕パターン
            function spawnEnemyBullets() {
                let freq = Math.max(10, 42 - (stage * 3));
                
                if (frameCount % freq === 0) {
                    if (stage <= 2) {
                        // ステージ1〜2：シンプルな直線・小規模な弾
                        let count = 3 + stage;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI / (count + 1)) * (i + 1);
                            bullets.push({
                                x: enemy.x, y: enemy.y + 40,
                                vx: Math.cos(angle) * 2.5,
                                vy: Math.sin(angle) * 2.5 + 1.5,
                                size: 8, color: "#ff4444", shape: "circle"
                            });
                        }
                    } else if (stage <= 5) {
                        // ステージ3〜5：扇状弾幕 ＋ スパイラル弾
                        let count = 6 + stage;
                        let offset = (frameCount * 0.1) % Math.PI;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI / (count - 1)) * i;
                            let speed = 3.0 + (stage * 0.2);
                            bullets.push({
                                x: enemy.x, y: enemy.y + 40,
                                vx: Math.cos(angle + offset) * speed,
                                vy: Math.abs(Math.sin(angle + offset)) * speed + 1.0,
                                size: 9, color: "#ff8833", shape: "star"
                            });
                        }
                    } else if (stage <= 8) {
                        // ステージ6〜8：全方位放射弾幕 ＋ 高速ニードル弾
                        let count = 10 + stage;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI * 2 / count) * i;
                            let speed = 3.5 + (stage * 0.25);
                            bullets.push({
                                x: enemy.x, y: enemy.y + 40,
                                vx: Math.cos(angle) * speed,
                                vy: Math.sin(angle) * speed + 1.5,
                                size: 8, color: "#ff33cc", shape: "needle"
                            });
                        }
                    } else {
                        // ステージ9〜10（魔王など）：超高密度クロス弾幕 ＆ 追尾型ダークエネルギー弾
                        let count = 16;
                        let wave = Math.sin(frameCount * 0.1) * 2.0;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI / count) * i + wave;
                            let speed = 4.2 + (stage * 0.2);
                            bullets.push({
                                x: enemy.x, y: enemy.y + 40,
                                vx: Math.cos(angle) * speed,
                                vy: Math.sin(angle) * speed + 2.0,
                                size: 10, color: "#9900ff", shape: "plasma"
                            });
                        }
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

                // 敵の移動（ステージが進むほど素早くトリッキーに動く）
                let moveSpeedFactor = 0.05 + (stage * 0.008);
                let moveWidthFactor = 200 + (stage * 15);
                enemy.moveTimer += moveSpeedFactor;
                enemy.x = 550 + Math.sin(enemy.moveTimer) * moveWidthFactor;

                spawnEnemyBullets();

                // 敵の弾の移動と当たり判定
                for (let i = bullets.length - 1; i >= 0; i--) {
                    let b = bullets[i];
                    b.x += b.vx;
                    b.y += b.vy;

                    let dist = Math.hypot(b.x - player.x, b.y - player.y);
                    if (dist < (player.size / 2 + b.size - 6)) {
                        player.hp -= (8 + stage * 2);
                        bullets.splice(i, 1);
                        if (player.hp <= 0) {
                            isGameOver = true;
                        }
                        continue;
                    }

                    if (b.y > canvas.height || b.x < 0 || b.x > canvas.width || b.y < 0) {
                        bullets.splice(i, 1);
                    }
                }

                // 味方の攻撃弾の移動と敵への当たり判定
                for (let i = playerBullets.length - 1; i >= 0; i--) {
                    let pb = playerBullets[i];
                    pb.x += pb.vx;
                    pb.y += pb.vy;

                    // 当たり判定 (レーザー、魔法弾、剣撃のサイズ別)
                    let hitRadius = pb.type === "slash" ? 25 : (pb.type === "laser" ? 12 : 10);
                    let dist = Math.hypot(pb.x - enemy.x, pb.y - enemy.y);
                    
                    if (dist < (enemy.size / 2 + hitRadius)) {
                        enemy.hp -= pb.damage;
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

                // 背景グリッド
                ctx.strokeStyle = "#1c2130";
                ctx.lineWidth = 1;
                for (let x = 0; x < canvas.width; x += 50) {
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
                }
                for (let y = 0; y < canvas.height; y += 50) {
                    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
                }

                // 敵画像
                if (enemyLoaded) {
                    ctx.drawImage(enemyImg, enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size);
                } else {
                    ctx.fillStyle = "#e74c3c";
                    ctx.beginPath(); ctx.arc(enemy.x, enemy.y, enemy.size/2, 0, Math.PI*2); ctx.fill();
                }

                // 敵名・HPバー
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 14px sans-serif";
                ctx.fillText(`Stage ${stage}: ${enemy.name}`, enemy.x, enemy.y - 58);

                ctx.fillStyle = "#333";
                ctx.fillRect(enemy.x - 70, enemy.y - 48, 140, 10);
                ctx.fillStyle = "#e74c3c";
                ctx.fillRect(enemy.x - 70, enemy.y - 48, 140 * (Math.max(0, enemy.hp) / enemy.maxHp), 10);

                // 自機画像
                if (playerLoaded) {
                    ctx.drawImage(playerImg, player.x - player.size/2, player.y - player.size/2, player.size, player.size);
                } else {
                    ctx.fillStyle = player.color;
                    ctx.beginPath(); ctx.arc(player.x, player.y, player.size/2, 0, Math.PI*2); ctx.fill();
                }

                // 自機名・HPバー
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px sans-serif";
                ctx.fillText(`${player.name} (${player.style === 'laser' ? 'レーザー' : player.style === 'orb' ? '魔法弾' : '剣撃'})`, player.x, player.y + 46);

                ctx.fillStyle = "#333";
                ctx.fillRect(player.x - 45, player.y + 53, 90, 9);
                ctx.fillStyle = "#2ecc71";
                ctx.fillRect(player.x - 45, player.y + 53, 90 * (Math.max(0, player.hp) / player.maxHp), 9);

                // 敵の弾の描画（形状や色が変わる）
                for (let b of bullets) {
                    ctx.fillStyle = b.color;
                    ctx.beginPath();
                    if (b.shape === "needle") {
                        ctx.arc(b.x, b.y, b.size * 0.7, 0, Math.PI * 2);
                    } else if (b.shape === "plasma") {
                        ctx.arc(b.x, b.y, b.size * 1.2, 0, Math.PI * 2);
                    } else {
                        ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
                    }
                    ctx.fill();
                }

                // キャラクター固有の攻撃エフェクト描画
                for (let pb of playerBullets) {
                    if (pb.type === "laser") {
                        // 戦士アレル：レーザー光線（縦長の光るビーム）
                        ctx.fillStyle = "#ff2222";
                        ctx.shadowBlur = 15;
                        ctx.shadowColor = "#ff0000";
                        ctx.fillRect(pb.x - pb.width/2, pb.y - pb.height/2, pb.width, pb.height);
                        ctx.shadowBlur = 0;
                    } else if (pb.type === "orb") {
                        // 魔術師ミリア：青く光る魔法弾
                        ctx.fillStyle = "#00ccff";
                        ctx.shadowBlur = 12;
                        ctx.shadowColor = "#00ffff";
                        ctx.beginPath();
                        ctx.arc(pb.x, pb.y, pb.size, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.shadowBlur = 0;
                    } else if (pb.type === "slash") {
                        // 聖騎士レオン：黄金の三日月剣撃
                        ctx.fillStyle = "#ffdd00";
                        ctx.shadowBlur = 18;
                        ctx.shadowColor = "#ffff00";
                        ctx.beginPath();
                        ctx.ellipse(pb.x, pb.y, pb.width/2, pb.height/2, 0, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.shadowBlur = 0;
                    }
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

    game_html = game_html_template\
        .replace("PLAYER_IMG_B64", player_img_base64)\
        .replace("ENEMY_IMG_B64", enemy_img_base64)\
        .replace("STAGE_NUM", str(current_stage))\
        .replace("PLAYER_HP", str(active_p['hp']))\
        .replace("PLAYER_MAXHP", str(active_p['maxHp']))\
        .replace("PLAYER_NAME", active_p['name'])\
        .replace("PLAYER_COLOR", active_p['color'])\
        .replace("PLAYER_STYLE", active_p['style'])\
        .replace("ENEMY_NAME", current_enemy_name)

    components.html(game_html, height=500)

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
