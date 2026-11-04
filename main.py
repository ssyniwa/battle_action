import streamlit as st
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(
    page_title="ダンジョン・ローグアタック：リアルタイム弾幕アクション",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ ダンジョン・ローグアタック：全10ステージ討伐の旅（究極ボス覚醒・バリア＆分身強化版）")
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
if "enemy_hp" not in st.session_state:
    st.session_state.enemy_hp = None

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
enemy_max_hp = 90 + (current_stage * 45)

if st.session_state.enemy_hp is None:
    st.session_state.enemy_hp = enemy_max_hp

active_p = st.session_state.players[st.session_state.active_player_idx]

player_img_base64 = get_image_base64(active_p["file"])
enemy_img_path = f"assets/enemy{current_stage}.jpg"
enemy_img_base64 = get_image_base64(enemy_img_path)

all_dead = all(p["hp"] <= 0 for p in st.session_state.players)

# --- UI コントロール・ステータス表示 ---
col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 2])

with col1:
    st.markdown(f"### 📍 Stage {current_stage}/10")
    st.write(f"**{current_enemy_name}** (HP: {st.session_state.enemy_hp} / {enemy_max_hp})")
    st.markdown(f"⭐ 成長Lv: **{st.session_state.attack_level}**")

with col2:
    st.markdown(f"### 🕹️ 出撃中")
    attack_desc = {"laser": "レーザー光線", "orb": "魔法弾", "slash": "剣撃"}[active_p['style']]
    status_p = "💀 死亡" if active_p["hp"] <= 0 else f"{active_p['hp']} / {active_p['maxHp']}"
    st.markdown(f"<span style='color:{active_p['color']}; font-weight:bold;'>{active_p['name']}</span> ({attack_desc})", unsafe_allow_html=True)
    st.write(f"HP: {status_p}")

with col3:
    st.markdown("### 👥 パーティ生存状況")
    status_list = []
    for i, p in enumerate(st.session_state.players):
        status = "🟢 生存" if p["hp"] > 0 else "💀 死亡"
        prefix = "👉 " if i == st.session_state.active_player_idx else ""
        status_list.append(f"{prefix}{p['name']}: {status} ({max(0, p['hp'])}HP)")
    st.write(" | ".join(status_list))

with col4:
    st.markdown("### 🎮 バトル制御")
    if all_dead:
        st.error("💀 全員死亡（GAME OVER）")
    elif not st.session_state.game_started:
        if st.button("🔥 戦闘開始", use_container_width=True, type="primary"):
            if active_p["hp"] > 0:
                st.session_state.game_started = True
                st.rerun()
            else:
                st.error("現在のキャラは死亡しています！生存している他のキャラを選択してください。")
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
        btn_label = f"選ぶ: {p['name']} [{style_name}] ({p['hp']}HP)" if p["hp"] > 0 else f"💀 {p['name']} (死亡)"
        disabled = (p["hp"] <= 0)
        if st.button(btn_label, disabled=disabled, use_container_width=True):
            st.session_state.active_player_idx = i
            st.session_state.game_started = False
            st.rerun()

st.markdown("---")

if all_dead:
    st.error("💀 参戦可能なパーティメンバーが全員死亡しました。GAME OVERです！「ゲームリセット」ボタンで最初からやり直してください。")
elif not st.session_state.game_started:
    st.info("👆 上の **「戦闘開始」** ボタンを押すとバトルがスタートします！（ボスはさらに強力なプロテクトバリアや幻影分身を展開します！）")
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
                hp: ENEMY_CURRENT_HP, maxHp: ENEMY_MAX_HP,
                name: "ENEMY_NAME",
                targetX: 550,
                targetY: 80,
                baseY: 80,
                aiState: "WAIT",
                dodgeCooldown: 0,
                specialTimer: 0,
                isEnraged: false,
                hasBarrier: false,
                barrierTimer: 0,
                clones: [] // 幻影分身
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
            let specialEffects = [];
            
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
                            x: player.x + offsetX, y: player.y - 30,
                            vx: 0, vy: -18,
                            width: 6 + Math.floor(attackLevel), height: 30,
                            type: "laser", damage: 22 + dmgBonus
                        });
                    }
                } else if (player.style === "orb") {
                    let totalOrbs = 2 + (attackLevel - 1);
                    for (let i = 0; i < totalOrbs; i++) {
                        let angleOffset = (i - (totalOrbs - 1) / 2) * 0.15;
                        playerBullets.push({
                            x: player.x + (i - 1) * 10, y: player.y - 25,
                            vx: angleOffset * 5, vy: -12,
                            size: 8, type: "orb", damage: 14 + dmgBonus
                        });
                    }
                } else if (player.style === "slash") {
                    for (let i = 0; i < numStreams; i++) {
                        let offsetX = (i - Math.floor(numStreams / 2)) * 18;
                        playerBullets.push({
                            x: player.x + offsetX, y: player.y - 30,
                            vx: 0, vy: -10,
                            width: 36, height: 14,
                            type: "slash", damage: 28 + dmgBonus
                        });
                    }
                }

                let homingChance = 0.35 + (attackLevel * 0.05);
                if (Math.random() < homingChance) {
                    playerBullets.push({
                        x: player.x, y: player.y - 30,
                        vx: (Math.random() - 0.5) * 4, vy: -8,
                        size: 9, type: "homing", speed: 7.5, damage: 18 + dmgBonus
                    });
                }
            }

            function triggerBossMechanics() {
                if (!enemyActive) return;

                // 狂暴化判定（HPが50%以下で覚醒）
                if (enemy.hp <= enemy.maxHp * 0.5) {
                    enemy.isEnraged = true;
                }

                // プロテクトバリアの自動展開（ステージ4以上で一定間隔でバリアを展開しダメージをガード）
                if (stage >= 4) {
                    enemy.barrierTimer++;
                    if (enemy.barrierTimer % 350 === 180) {
                        enemy.hasBarrier = true;
                        enemy.aiState = "🛡️ プロテクトバリア展開";
                    } else if (enemy.barrierTimer % 350 === 300) {
                        enemy.hasBarrier = false;
                    }
                }

                // 幻影分身（ステージ7以上で左右に出現しフェイク弾幕を放つ）
                if (stage >= 7) {
                    if (enemy.specialTimer % 300 === 0) {
                        enemy.clones = [
                            { x: enemy.x - 180, y: enemy.y, size: enemy.size * 0.8 },
                            { x: enemy.x + 180, y: enemy.y, size: enemy.size * 0.8 }
                        ];
                    } else if (enemy.specialTimer % 300 === 120) {
                        enemy.clones = []; // 分身消滅
                    }
                }

                if (stage < 6) return;
                enemy.specialTimer++;

                // 重力場・ワームホールの生成
                if (enemy.specialTimer % 240 === 0) {
                    specialEffects.push({
                        x: 550, y: 240,
                        radius: 130,
                        duration: 150,
                        type: "gravity",
                        color: "rgba(147, 51, 234, 0.35)"
                    });
                }

                if (stage === 6 && enemy.specialTimer % 180 === 0) {
                    enemy.aiState = "SKILL: 猛毒スプレッド";
                    for (let i = 0; i < 3; i++) {
                        specialEffects.push({
                            x: 200 + i * 350, y: 350,
                            radius: 50, duration: 180,
                            type: "poison", color: "rgba(34, 197, 94, 0.4)"
                        });
                    }
                } else if (stage === 7 && enemy.specialTimer % 140 === 0) {
                    enemy.aiState = "SKILL: 炎獄フレア";
                    let count = 14;
                    for (let i = 0; i < count; i++) {
                        let angle = (Math.PI * 2 / count) * i;
                        bullets.push({
                            x: enemy.x, y: enemy.y,
                            vx: Math.cos(angle) * 3.5, vy: Math.sin(angle) * 3.5,
                            size: 10, color: "#ff6600"
                        });
                    }
                } else if (stage === 8 && enemy.specialTimer % 180 === 0) {
                    enemy.aiState = "SKILL: 吸血コウモリ";
                    for (let i = -1; i <= 1; i++) {
                        bullets.push({
                            x: enemy.x + i * 40, y: enemy.y + 30,
                            vx: i * 2.2, vy: 4.5,
                            size: 8, color: "#ec4899", isVampireBat: true
                        });
                    }
                } else if (stage === 9 && enemy.specialTimer % 200 === 0) {
                    enemy.aiState = "SKILL: 竜王メテオ";
                    specialEffects.push({
                        x: player.x, y: 0, targetY: player.y,
                        radius: 70, duration: 55,
                        type: "meteor", color: "rgba(239, 68, 68, 0.6)"
                    });
                } else if (stage === 10 && enemy.specialTimer % 120 === 0) {
                    enemy.aiState = "SKILL: 魔王の次元崩壊";
                    enemy.x = 200 + Math.random() * 700;
                    let count = 18;
                    let speedMult = enemy.isEnraged ? 1.5 : 1.1;
                    for (let i = 0; i < count; i++) {
                        let angle = (Math.PI / count) * i;
                        bullets.push({
                            x: enemy.x, y: enemy.y,
                            vx: Math.cos(angle) * 5.2 * speedMult, vy: Math.sin(angle) * 5.2 * speedMult + 1.2,
                            size: 10, color: "#8b5cf6"
                        });
                    }
                }
            }

            function updateAdvancedTacticalAI() {
                if (!enemyActive) return;

                if (enemy.dodgeCooldown > 0) enemy.dodgeCooldown--;

                if (!enemy.hasBarrier) {
                    enemy.aiState = enemy.isEnraged ? "🔥 ENRAGED (狂暴化)" : "STRAFE (戦術機動)";
                }
                
                triggerBossMechanics();

                for (let pb of playerBullets) {
                    let distX = Math.abs(pb.x - enemy.x);
                    let distY = enemy.y - pb.y;
                    if (distX < 65 && distY > 0 && distY < 250 && enemy.dodgeCooldown === 0) {
                        enemy.aiState = "DODGE (回避ステップ)";
                        let escapeDir = (pb.x > enemy.x) ? -1 : 1;
                        enemy.targetX = enemy.x + escapeDir * 150;
                        enemy.dodgeCooldown = 22;
                        break;
                    }
                }

                if (enemy.dodgeCooldown === 0) {
                    let timeFactor = frameCount * (enemy.isEnraged ? 0.09 : 0.06);
                    let offsetTargetX = player.x + Math.sin(timeFactor) * 240;
                    
                    let isInsideBunker = (player.x >= 450 && player.x <= 650 && player.y >= 330);
                    if (isInsideBunker) {
                        enemy.aiState = "FLANK (基地狙撃)";
                        offsetTargetX = (Math.floor(frameCount / 90) % 2 === 0) ? 280 : 820;
                    }

                    if (stage >= 5 && frameCount % 280 > 220) {
                        enemy.aiState = "DIVE (急襲)";
                        enemy.targetY = 210;
                    } else {
                        enemy.targetY = enemy.baseY + Math.cos(timeFactor * 1.5) * 25;
                    }

                    enemy.targetX = offsetTargetX;
                }

                enemy.targetX = Math.max(100, Math.min(canvas.width - 100, enemy.targetX));

                let responseSpeed = (0.09 + (stage * 0.015)) * (enemy.isEnraged ? 1.4 : 1.0);
                enemy.x += (enemy.targetX - enemy.x) * responseSpeed;
                enemy.y += (enemy.targetY - enemy.y) * responseSpeed;

                // 弾幕発射頻度と弾数強化
                let freq = Math.max(5, (32 - (stage * 3)) / (enemy.isEnraged ? 1.7 : 1.0));
                if (frameCount % Math.floor(freq) === 0) {
                    if (stage <= 2) {
                        for (let i = -1; i <= 1; i++) {
                            bullets.push({ x: enemy.x, y: enemy.y + 40, vx: i * 2.5, vy: 4.0, size: 8, color: "#4ade80" });
                        }
                    } else if (stage <= 5) {
                        let count = enemy.isEnraged ? 12 : 8;
                        let offset = frameCount * 0.18;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI / (count - 1)) * i + offset * 0.2;
                            bullets.push({ x: enemy.x, y: enemy.y + 40, vx: Math.cos(angle) * 4.2, vy: Math.sin(angle) * 4.2 + 1.4, size: 8, color: "#a855f7" });
                        }
                    } else {
                        let count = enemy.isEnraged ? 20 : 16;
                        let wave = Math.sin(frameCount * 0.12) * 3.5;
                        for (let i = 0; i < count; i++) {
                            let angle = (Math.PI / count) * i + wave;
                            bullets.push({ x: enemy.x, y: enemy.y + 40, vx: Math.cos(angle) * 5.2, vy: Math.sin(angle) * 5.2 + 1.6, size: 9, color: "#f43f5e" });
                        }
                        // 分身からもフェイク弾発射
                        for (let clone of enemy.clones) {
                            bullets.push({ x: clone.x, y: clone.y + 40, vx: (Math.random()-0.5)*3, vy: 3.5, size: 7, color: "#cbd5e1" });
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

                updateAdvancedTacticalAI();

                // 特殊エフェクト
                for (let i = specialEffects.length - 1; i >= 0; i--) {
                    let eff = specialEffects[i];
                    eff.duration--;
                    if (eff.type === "poison") {
                        let dist = Math.hypot(player.x - eff.x, player.y - eff.y);
                        if (dist < eff.radius + player.size/2) {
                            player.hp -= 0.35;
                            if (player.hp <= 0) {
                                player.hp = 0;
                                isGameOver = true;
                            }
                        }
                    } else if (eff.type === "meteor") {
                        if (eff.duration === 1) {
                            let dist = Math.hypot(player.x - eff.x, player.y - eff.targetY);
                            if (dist < eff.radius + player.size/2) {
                                player.hp -= 28;
                                if (player.hp <= 0) {
                                    player.hp = 0;
                                    isGameOver = true;
                                }
                            }
                        }
                    } else if (eff.type === "gravity") {
                        let pullAngle = Math.atan2(enemy.y - player.y, enemy.x - player.x);
                        player.x += Math.cos(pullAngle) * 2.2;
                        player.y += Math.sin(pullAngle) * 2.2;
                    }
                    if (eff.duration <= 0) {
                        specialEffects.splice(i, 1);
                    }
                }

                // 敵弾判定
                for (let i = bullets.length - 1; i >= 0; i--) {
                    let b = bullets[i];
                    b.x += b.vx;
                    b.y += b.vy;

                    if (b.isVampireBat) {
                        let angle = Math.atan2(player.y - b.y, player.x - b.x);
                        b.vx += Math.cos(angle) * 0.25;
                        b.vy += Math.sin(angle) * 0.25;
                        let spd = Math.hypot(b.vx, b.vy);
                        if (spd > 5.2) { b.vx = (b.vx/spd)*5.2; b.vy = (b.vy/spd)*5.2; }
                    }

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
                        player.hp -= (9 + stage * 1.6);
                        bullets.splice(i, 1);
                        if (player.hp <= 0) {
                            player.hp = 0;
                            isGameOver = true;
                        }
                        continue;
                    }

                    if (b.y > canvas.height || b.x < 0 || b.x > canvas.width || b.y < 0) {
                        bullets.splice(i, 1);
                    }
                }

                // プレイヤー攻撃弾判定
                for (let i = playerBullets.length - 1; i >= 0; i--) {
                    let pb = playerBullets[i];
                    
                    if (pb.type === "homing") {
                        let angle = Math.atan2(enemy.y - pb.y, enemy.x - pb.x);
                        pb.vx += Math.cos(angle) * 0.7;
                        pb.vy += Math.sin(angle) * 0.7;
                        let spd = Math.hypot(pb.vx, pb.vy);
                        if (spd > pb.speed) {
                            pb.vx = (pb.vx / spd) * pb.speed;
                            pb.vy = (pb.vy / spd) * pb.speed;
                        }
                    }

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
                        // バリア展開中はダメージ無効
                        if (enemy.hasBarrier) {
                            // バリアに弾が弾かれたエフェクト等
                        } else {
                            enemy.hp -= pb.damage;
                        }
                        playerBullets.splice(i, 1);
                        if (enemy.hp <= 0) {
                            enemy.hp = 0;
                            isCleared = true;
                        }
                        continue;
                    }

                    if (pb.y < 0 || pb.y > canvas.height || pb.x < 0 || pb.x > canvas.width) {
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

                // 特殊エフェクト
                for (let eff of specialEffects) {
                    ctx.fillStyle = eff.color;
                    ctx.beginPath();
                    if (eff.type === "poison") {
                        ctx.arc(eff.x, eff.y, eff.radius, 0, Math.PI * 2);
                    } else if (eff.type === "meteor") {
                        ctx.arc(eff.x, eff.targetY, eff.radius * (1 - eff.duration / 55), 0, Math.PI * 2);
                    } else if (eff.type === "gravity") {
                        ctx.arc(eff.x, eff.y, eff.radius + Math.sin(frameCount * 0.1) * 10, 0, Math.PI * 2);
                        ctx.strokeStyle = "rgba(168, 85, 247, 0.6)";
                        ctx.lineWidth = 2;
                        ctx.stroke();
                    }
                    ctx.fill();
                }

                // 障害物
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

                // 幻影分身描画
                for (let clone of enemy.clones) {
                    ctx.fillStyle = "rgba(255, 255, 255, 0.35)";
                    ctx.beginPath(); ctx.arc(clone.x, clone.y, clone.size/2, 0, Math.PI*2); ctx.fill();
                }

                // 敵（狂暴化＆バリアエフェクト）
                if (enemy.isEnraged) {
                    ctx.shadowBlur = 25;
                    ctx.shadowColor = "#ff2222";
                }
                if (enemyLoaded) {
                    ctx.drawImage(enemyImg, enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size);
                } else {
                    ctx.fillStyle = enemy.isEnraged ? "#ff2222" : "#e74c3c";
                    ctx.beginPath(); ctx.arc(enemy.x, enemy.y, enemy.size/2, 0, Math.PI*2); ctx.fill();
                }

                // プロテクトバリアのシールド描画
                if (enemy.hasBarrier) {
                    ctx.strokeStyle = "#00ffff";
                    ctx.lineWidth = 4;
                    ctx.beginPath();
                    ctx.arc(enemy.x, enemy.y, enemy.size * 0.7, 0, Math.PI * 2);
                    ctx.stroke();
                }
                ctx.shadowBlur = 0;

                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 14px sans-serif";
                let statusText = enemy.isEnraged ? "🔥 【狂暴化覚醒】" : `[${enemy.aiState || 'WAIT'}]`;
                ctx.fillText(`Stage ${stage}: ${enemy.name} ${statusText}`, enemy.x, enemy.y - 58);

                ctx.fillStyle = "#333";
                ctx.fillRect(enemy.x - 70, enemy.y - 48, 140, 10);
                ctx.fillStyle = enemy.isEnraged ? "#ff2222" : "#e74c3c";
                ctx.fillRect(enemy.x - 70, enemy.y - 48, 140 * (Math.max(0, enemy.hp) / enemy.maxHp), 10);

                if (!enemyActive) {
                    ctx.fillStyle = "#ffff00";
                    ctx.font = "bold 18px sans-serif";
                    ctx.fillText("READY... (移動キーまたはZキーで戦闘開始)", canvas.width / 2, enemy.y + 80);
                }

                // プレイヤー
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

                // 弾
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
                    } else if (pb.type === "homing") {
                        ctx.fillStyle = "#22d3ee";
                        ctx.beginPath(); ctx.arc(pb.x, pb.y, pb.size, 0, Math.PI * 2); ctx.fill();
                        ctx.strokeStyle = "#fff";
                        ctx.lineWidth = 1.5;
                        ctx.stroke();
                    }
                }

                if (isGameOver) {
                    ctx.fillStyle = "rgba(0, 0, 0, 0.88)";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = "#ff3333";
                    ctx.font = "bold 38px sans-serif";
                    ctx.fillText(`${player.name} が死亡しました！`, canvas.width / 2, canvas.height / 2 - 20);
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

    game_html = game_html_template        .replace("PLAYER_IMG_B64", player_img_base64)        .replace("ENEMY_IMG_B64", enemy_img_base64)        .replace("STAGE_NUM", str(current_stage))        .replace("ATTACK_LEVEL", str(st.session_state.attack_level))        .replace("PLAYER_HP", str(active_p['hp']))        .replace("PLAYER_MAXHP", str(active_p['maxHp']))        .replace("PLAYER_NAME", active_p['name'])        .replace("PLAYER_COLOR", active_p['color'])        .replace("PLAYER_STYLE", active_p['style'])        .replace("ENEMY_NAME", current_enemy_name)        .replace("ENEMY_CURRENT_HP", str(st.session_state.enemy_hp))        .replace("ENEMY_MAX_HP", str(enemy_max_hp))

    components.html(game_html, height=500)

st.markdown("---")
ctrl_col1, ctrl_col2 = st.columns(2)

with ctrl_col1:
    if st.button("⚔️ 次のステージへ進む（ステージ進行・成長Lvアップ）", use_container_width=True, type="primary"):
        if current_stage < 10:
            st.session_state.stage += 1
            st.session_state.attack_level += 1
            st.session_state.game_started = False
            st.session_state.enemy_hp = None
            st.success(f"Stage {st.session_state.stage} に進みます！攻撃力がアップしました（成長Lv: {st.session_state.attack_level}）。「戦闘開始」を押してください。")
            st.rerun()
        else:
            st.success("🎉 全10ステージ完全踏破！魔王を討伐しました！")

with ctrl_col2:
    if st.button("👥 倒れたキャラを「死亡」扱いにして次の仲間と交代", use_container_width=True):
        st.session_state.players[st.session_state.active_player_idx]["hp"] = 0
        st.session_state.game_started = False
        
        next_idx = None
        for i, p in enumerate(st.session_state.players):
            if p["hp"] > 0:
                next_idx = i
                break
        
        if next_idx is not None:
            st.session_state.active_player_idx = next_idx
            st.session_state.players[next_idx]["hp"] = st.session_state.players[next_idx]["maxHp"]
            st.success(f"💀 前の仲間が死亡しました... 代わりに **{st.session_state.players[next_idx]['name']}** がHP100%で出撃します！（敵のダメージはそのまま引き継がれます）")
            st.rerun()
        else:
            st.error("💀 パーティメンバー3人が全員死亡（全滅）しました... GAME OVER！ゲームリセットしてください。")
