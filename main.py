import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(
    page_title="ダンジョン・ローグアタック：リアルタイム弾幕アクション",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ ダンジョン・ローグアタック：全10ステージ討伐の旅（戦略的AI・成長システム搭載版）")
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
if "attack_level" not in st.session_state:
    st.session_state.attack_level = 1

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
    st.markdown(f"⭐ 成長Lv: **{st.session_state.attack_level}**")

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
**【戦略AI戦術線ガイド】**
* **敵の戦略的AI移動**: 
  * 🧠 **遮蔽物回避回り込み**: プレイヤーが前壁（防壁）の陰に隠れていると、敵は攻撃を通すため**左右の隙間へ回り込もうと移動**します！
  * 🧠 **自弾回避行動**: 味方の弾が近づくと、横スライドやステップで緊急回避を試みます！
  * 🧠 **間合い管理**: プレイヤーとの距離や射角を常に判定し、有利な位置関係を維持します。
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
            let attackLevel = ATTACK_LEVEL;
            let player = { 
                x: 550, y: 410, size: 55, speed: 7, 
                hp: PLAYER_HP, maxHp: PLAYER_MAXHP, 
                name: "PLAYER_NAME", color: "PLAYER_COLOR", style: "PLAYER_STYLE" 
            };
            
            let enemy = { 
                x: 550, y: 80, size: 90, 
                hp: 90 + (stage * 45), maxHp: 90 + (stage * 45),
                name: "ENEMY_NAME",
                targetX: 550,
                targetY: 80,
                baseY: 80,
                speed: 2.5 + (stage * 0.3)
            };
            
            let obstacles = [
                { x: 480, y: 380, w: 20, h: 90, hp: 999, maxHp: 999, indestructible: true },
                { x: 620, y: 380, w: 20, h: 90, hp: 999, maxHp: 999, indestructible: true },
                { x: 550, y: 330, w: 140, h: 20, hp: 999, maxHp: 999, indestructible: true },
                { x: 250, y: 230, w: 100, h: 20, hp: 120, maxHp: 120 },
                { x: 850, y: 230, w: 100, h: 20, hp: 120, maxHp: 120 }
            ];
            
            let bullets = [];
            let playerBullets = [];
            
            let keys = {};
            let frameCount = 0;
            let isGameOver = false;
            let isCleared = false;
            let enemyActive = false;

            window.addEventListener("keydown", (e) => {
                keys[e.code] = true;
                if (!enemyActive) {
                    if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "KeyA", "KeyD", "KeyW", "KeyS", "KeyZ", "KeyY"].includes(e.code)) {
                        enemyActive = true;
                    }
                }
                if ((e.code === "KeyZ" || e.code === "KeyY") && !isGameOver && !isCleared) {
                    shootPlayerAttack();
                    e.preventDefault();
                }
            });
            window.addEventListener("keyup", (e) => {
                keys[e.code] = false;
            });

            function shootPlayerAttack() {
                let numStreams = Math.min(5, 1 + Math.floor((attackLevel - 1) / 2));
                let dmgBonus = (attackLevel - 1) * 4;

                if (player.style === "laser") {
                    for (let i = 0; i < numStreams; i++) {
                        let offsetX = (i - Math.floor(numStreams / 2)) * 14;
                        playerBullets.push({
                            x: player.x + offsetX,
                            y: player.y - 30,
                            vx: 0,
                            vy: -18,
                            width: 6 + Math.floor(attackLevel),
                            height: 30,
                            type: "laser",
                            damage: 22 + dmgBonus
                        });
                    }
                } else if (player.style === "orb") {
                    let totalOrbs = 2 + (attackLevel - 1);
                    for (let i = 0; i < totalOrbs; i++) {
                        let angleOffset = (i - (totalOrbs - 1) / 2) * 0.15;
                        playerBullets.push({
                            x: player.x + (i - 1) * 10,
                            y: player.y - 25,
                            vx: angleOffset * 5,
                            vy: -12,
                            size: 8,
                            type: "orb",
                            damage: 14 + dmgBonus
                        });
                    }
                } else if (player.style === "slash") {
                    for (let i = 0; i < numStreams; i++) {
                        let offsetX = (i - Math.floor(numStreams / 2)) * 18;
                        playerBullets.push({
                            x: player.x + offsetX,
                            y: player.y - 30,
                            vx: 0,
                            vy: -10,
                            width: 36,
                            height: 14,
                            type: "slash",
                            damage: 28 + dmgBonus
                        });
                    }
                }
            }

            // 戦略的AI移動ロジック
            function updateStrategicEnemyMovement() {
                if (!enemyActive) return;

                // 1. プレイヤーが前壁（X: 480〜620付近）に隠れているか判定
                let isBehindCover = (player.x >= 470 && player.x <= 630 && player.y > 330);

                if (isBehindCover) {
                    // 戦略1：前壁で遮られている場合、前壁の外側（左右の射角）へアクティブに移動し、回り込んで攻撃を狙う
                    if (frameCount % 60 < 30) {
                        enemy.targetX = 380; // 左側の隙間方向
                    } else {
                        enemy.targetX = 720; // 右側の隙間方向
                    }
                    enemy.targetY = enemy.baseY + Math.sin(frameCount * 0.05) * 20;
                } else {
                    // 戦略2：前壁の外にプレイヤーがいる場合、プレイヤーのX軸を精密追跡して直接狙い撃つ
                    enemy.targetX = player.x;
                    enemy.targetY = enemy.baseY + Math.cos(frameCount * 0.04) * 25;
                }

                // 戦略3：近づいてくる味方の弾を感知して回避移動（弾が近くにある場合横にスライド）
                for (let pb of playerBullets) {
                    let distToEnemy = Math.hypot(pb.x - enemy.x, pb.y - enemy.y);
                    if (distToEnemy < 120 && pb.y > enemy.y) {
                        // 弾から逃れる方向に目標位置を修正
                        let dodgeDir = (pb.x > enemy.x) ? -1 : 1;
                        enemy.targetX += dodgeDir * 60;
                        break;
                    }
                }

                // キャンバス端の制限
                enemy.targetX = Math.max(120, Math.min(canvas.width - 120, enemy.targetX));

                // スムーズな目標位置への補間（ステージが上がるほど追従スピードアップ）
                let lerpSpeed = 0.03 + (stage * 0.008);
                enemy.x += (enemy.targetX - enemy.x) * lerpSpeed;
                enemy.y += (enemy.targetY - enemy.y) * lerpSpeed;

                // 弾幕発射パターン
                let freq = Math.max(8, 38 - (stage * 3));
                if (frameCount % freq === 0) {
                    if (stage === 1) {
                        for (let i = -1; i <= 1; i++) {
                            bullets.push({ x: enemy.x, y: enemy.y + 40, vx: i * 1.5, vy: 3.2, size: 8, color: "#4ade80" });
                        }
                    } else if (stage === 2) {
                        let count = 5;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI / (count - 1)) * i;
                            bullets.push({ x: enemy.x, y: enemy.y + 40, vx: Math.cos(angle) * 3.2, vy: Math.sin(angle) * 3.2 + 1.0, size: 8, color: "#fb923c" });
                        }
                    } else if (stage === 3) {
                        // プレイヤー狙撃弾
                        let angleToPlayer = Math.atan2(player.y - enemy.y, player.x - enemy.x);
                        for (let i = -1; i <= 1; i++) {
                            let a = angleToPlayer + i * 0.15;
                            bullets.push({ x: enemy.x, y: enemy.y + 40, vx: Math.cos(a) * 4.5, vy: Math.sin(a) * 4.5, size: 8, color: "#f43f5e" });
                        }
                    } else if (stage <= 6) {
                        let count = 8;
                        let offset = frameCount * 0.12;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI * 2 / count) * i + offset;
                            bullets.push({ x: enemy.x, y: enemy.y + 40, vx: Math.cos(angle) * 3.4, vy: Math.sin(angle) * 3.4, size: 8, color: "#a855f7" });
                        }
                    } else {
                        let count = 14;
                        let wave = Math.sin(frameCount * 0.1) * 2.5;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI / count) * i + wave;
                            bullets.push({ x: enemy.x, y: enemy.y + 40, vx: Math.cos(angle) * 4.2, vy: Math.sin(angle) * 4.2 + 1.5, size: 10, color: "#e879f9" });
                        }
                    }
                }
            }

            function update() {
                if (isGameOver || isCleared) return;

                let nextX = player.x;
                let nextY = player.y;
                if ((keys["ArrowLeft"] || keys["KeyA"]) && player.x > player.size / 2) nextX -= player.speed;
                if ((keys["ArrowRight"] || keys["KeyD"]) && player.x < canvas.width - player.size / 2) nextX += player.speed;
                if ((keys["ArrowUp"] || keys["KeyW"]) && player.y > player.size / 2) nextY -= player.speed;
                if ((keys["ArrowDown"] || keys["KeyS"]) && player.y < canvas.height - player.size / 2) nextY += player.speed;

                let canMoveX = true;
                let canMoveY = true;
                for (let obs of obstacles) {
                    if (obs.hp > 0) {
                        let oLeft = obs.x - obs.w / 2;
                        let oRight = obs.x + obs.w / 2;
                        let oTop = obs.y - obs.h / 2;
                        let oBottom = obs.y + obs.h / 2;
                        if (player.y + player.size/2 > oTop && player.y - player.size/2 < oBottom) {
                            if (nextX + player.size/2 > oLeft && nextX - player.size/2 < oRight) canMoveX = false;
                        }
                        if (player.x + player.size/2 > oLeft && player.x - player.size/2 < oRight) {
                            if (nextY + player.size/2 > oTop && nextY - player.size/2 < oBottom) canMoveY = false;
                        }
                    }
                }
                if (canMoveX) player.x = nextX;
                if (canMoveY) player.y = nextY;

                updateStrategicEnemyMovement();

                // 敵の弾の移動と判定
                for (let i = bullets.length - 1; i >= 0; i--) {
                    let b = bullets[i];
                    b.x += b.vx;
                    b.y += b.vy;

                    let hitObstacle = false;
                    for (let obs of obstacles) {
                        if (obs.hp > 0) {
                            let oLeft = obs.x - obs.w / 2;
                            let oRight = obs.x + obs.w / 2;
                            let oTop = obs.y - obs.h / 2;
                            let oBottom = obs.y + obs.h / 2;
                            if (b.x >= oLeft && b.x <= oRight && b.y >= oTop && b.y <= oBottom) {
                                hitObstacle = true;
                                if (!obs.indestructible) obs.hp -= 3;
                                break;
                            }
                        }
                    }
                    if (hitObstacle) {
                        bullets.splice(i, 1);
                        continue;
                    }

                    let dist = Math.hypot(b.x - player.x, b.y - player.y);
                    if (dist < (player.size / 2 + b.size - 6)) {
                        player.hp -= (8 + stage * 1.5);
                        bullets.splice(i, 1);
                        if (player.hp <= 0) isGameOver = true;
                        continue;
                    }

                    if (b.y > canvas.height || b.x < 0 || b.x > canvas.width || b.y < 0) {
                        bullets.splice(i, 1);
                    }
                }

                // プレイヤー攻撃弾の移動と判定
                for (let i = playerBullets.length - 1; i >= 0; i--) {
                    let pb = playerBullets[i];
                    pb.x += pb.vx;
                    pb.y += pb.vy;

                    let hitObs = false;
                    for (let obs of obstacles) {
                        if (obs.hp > 0) {
                            let oLeft = obs.x - obs.w / 2;
                            let oRight = obs.x + obs.w / 2;
                            let oTop = obs.y - obs.h / 2;
                            let oBottom = obs.y + obs.h / 2;
                            if (pb.x >= oLeft && pb.x <= oRight && pb.y >= oTop && pb.y <= oBottom) {
                                hitObs = true;
                                break;
                            }
                        }
                    }
                    if (hitObs) {
                        playerBullets.splice(i, 1);
                        continue;
                    }

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

                ctx.strokeStyle = "#1c2130";
                ctx.lineWidth = 1;
                for (let x = 0; x < canvas.width; x += 50) {
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
                }
                for (let y = 0; y < canvas.height; y += 50) {
                    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
                }

                // 障害物描画
                for (let obs of obstacles) {
                    if (obs.hp > 0) {
                        if (obs.indestructible) {
                            ctx.fillStyle = "#2b6cb0";
                            ctx.strokeStyle = "#63b3ed";
                        } else {
                            ctx.fillStyle = "#4a5568";
                            ctx.strokeStyle = "#718096";
                        }
                        ctx.lineWidth = 2;
                        let rx = obs.x - obs.w / 2;
                        let ry = obs.y - obs.h / 2;
                        ctx.fillRect(rx, ry, obs.w, obs.h);
                        ctx.strokeRect(rx, ry, obs.w, obs.h);

                        if (!obs.indestructible) {
                            ctx.fillStyle = "#222";
                            ctx.fillRect(rx, ry - 10, obs.w, 5);
                            ctx.fillStyle = "#38bdf8";
                            ctx.fillRect(rx, ry - 10, obs.w * (obs.hp / obs.maxHp), 5);
                        }
                    }
                }

                // 敵画像
                if (enemyLoaded) {
                    ctx.drawImage(enemyImg, enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size);
                } else {
                    ctx.fillStyle = "#e74c3c";
                    ctx.beginPath(); ctx.arc(enemy.x, enemy.y, enemy.size/2, 0, Math.PI*2); ctx.fill();
                }

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 14px sans-serif";
                ctx.fillText(`Stage ${stage}: ${enemy.name} (成長Lv:${attackLevel})`, enemy.x, enemy.y - 58);

                ctx.fillStyle = "#333";
                ctx.fillRect(enemy.x - 70, enemy.y - 48, 140, 10);
                ctx.fillStyle = "#e74c3c";
                ctx.fillRect(enemy.x - 70, enemy.y - 48, 140 * (Math.max(0, enemy.hp) / enemy.maxHp), 10);

                if (!enemyActive) {
                    ctx.fillStyle = "#ffff00";
                    ctx.font = "bold 18px sans-serif";
                    ctx.fillText("READY... (移動キーまたはZキーで戦闘開始)", canvas.width / 2, enemy.y + 80);
                }

                // 自機画像
                if (playerLoaded) {
                    ctx.drawImage(playerImg, player.x - player.size/2, player.y - player.size/2, player.size, player.size);
                } else {
                    ctx.fillStyle = player.color;
                    ctx.beginPath(); ctx.arc(player.x, player.y, player.size/2, 0, Math.PI*2); ctx.fill();
                }

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px sans-serif";
                ctx.fillText(`${player.name} (${player.style === 'laser' ? 'レーザー' : player.style === 'orb' ? '魔法弾' : '剣撃'})`, player.x, player.y + 46);

                ctx.fillStyle = "#333";
                ctx.fillRect(player.x - 45, player.y + 53, 90, 9);
                ctx.fillStyle = "#2ecc71";
                ctx.fillRect(player.x - 45, player.y + 53, 90 * (Math.max(0, player.hp) / player.maxHp), 9);

                // 弾描画
                for (let b of bullets) {
                    ctx.fillStyle = b.color;
                    ctx.beginPath();
                    ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
                    ctx.fill();
                }

                for (let pb of playerBullets) {
                    if (pb.type === "laser") {
                        ctx.fillStyle = "#ff2222";
                        ctx.fillRect(pb.x - pb.width/2, pb.y - pb.height/2, pb.width, pb.height);
                    } else if (pb.type === "orb") {
                        ctx.fillStyle = "#00ccff";
                        ctx.beginPath(); ctx.arc(pb.x, pb.y, pb.size, 0, Math.PI * 2); ctx.fill();
                    } else if (pb.type === "slash") {
                        ctx.fillStyle = "#ffdd00";
                        ctx.beginPath(); ctx.ellipse(pb.x, pb.y, pb.width/2, pb.height/2, 0, 0, Math.PI * 2); ctx.fill();
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

    game_html = game_html_template        .replace("PLAYER_IMG_B64", player_img_base64)        .replace("ENEMY_IMG_B64", enemy_img_base64)        .replace("STAGE_NUM", str(current_stage))        .replace("ATTACK_LEVEL", str(st.session_state.attack_level))        .replace("PLAYER_HP", str(active_p['hp']))        .replace("PLAYER_MAXHP", str(active_p['maxHp']))        .replace("PLAYER_NAME", active_p['name'])        .replace("PLAYER_COLOR", active_p['color'])        .replace("PLAYER_STYLE", active_p['style'])        .replace("ENEMY_NAME", current_enemy_name)

    components.html(game_html, height=500)

st.markdown("---")
ctrl_col1, ctrl_col2 = st.columns(2)

with ctrl_col1:
    if st.button("⚔️ 次のステージへ進む（ステージ進行・成長Lvアップ）", use_container_width=True, type="primary"):
        if current_stage < 10:
            st.session_state.stage += 1
            st.session_state.attack_level += 1
            st.session_state.game_started = False
            st.success(f"Stage {st.session_state.stage} に進みます！攻撃力がアップしました（成長Lv: {st.session_state.attack_level}）。「戦闘開始」を押してください。")
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
