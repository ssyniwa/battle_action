import streamlit as st
import streamlit.components.v1 as components

# ページの設定（ワイド画面）
st.set_page_config(
    page_title="ダンジョン・ローグアタック：リアルタイム弾幕アクション版",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ ダンジョン・ローグアタック：全10ステージ討伐の旅（リアルタイムアクション版）")
st.markdown("---")

if "game_state" not in st.session_state:
    st.session_state.stage = 1
    st.session_state.players = [
        {"name": "戦士アレル", "hp": 100, "maxHp": 100, "image": "app/static/player1.jpg", "color": "#ff4444"},
        {"name": "魔術師ミリア", "hp": 70, "maxHp": 70, "image": "app/static/player2.jpg", "color": "#4488ff"},
        {"name": "聖騎士レオン", "hp": 120, "maxHp": 120, "image": "app/static/player3.jpg", "color": "#ffcc00"}
    ]
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

current_stage = st.session_state.stage
current_enemy_name = ENEMY_NAMES.get(current_stage, "強敵")
active_p = st.session_state.players[st.session_state.active_player_idx]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"### 📍 現在のステージ: **Stage {current_stage}/10**")
    st.write(f"討伐対象: **{current_enemy_name}**")
with col2:
    st.markdown(f"### 🕹️ 出撃中キャラ: **{active_p['name']}**")
    st.write(f"HP: {active_p['hp']} / {active_p['maxHp']}")
with col3:
    st.markdown("### 👥 パーティ生存状況")
    status_str = " | ".join([f"{p['name']}: {'生存' if p['hp'] > 0 else '戦闘不能'}" for p in st.session_state.players])
    st.write(status_str)
with col4:
    if st.button("🔄 ゲームリセット", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("---")
st.caption("【操作方法】 左右矢印キー（または A/Dキー）で移動 ｜ **Zキー**で攻撃弾を発射！ ｜ 敵も自機もダイナミックに動きます！")

# JavaScriptコードテンプレート（普通の文字列として定義し、プレースホルダーを置き換える）
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
            box-shadow: 0 0 20px rgba(0,0,0,0.8);
            display: block;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="1100" height="520"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        const playerImg = new Image();
        playerImg.src = "PLAYER_IMAGE_PLACEHOLDER";
        let playerLoaded = false;
        playerImg.onload = () => { playerLoaded = true; };

        const enemyImg = new Image();
        enemyImg.src = "app/static/enemySTAGE_PLACEHOLDER.jpg";
        let enemyLoaded = false;
        enemyImg.onload = () => { enemyLoaded = true; };

        let stage = STAGE_PLACEHOLDER;
        let player = { 
            x: 550, y: 430, size: 65, speed: 7, 
            hp: PLAYER_HP_PLACEHOLDER, maxHp: PLAYER_MAXHP_PLACEHOLDER, 
            name: "PLAYER_NAME_PLACEHOLDER", color: "PLAYER_COLOR_PLACEHOLDER" 
        };
        
        let enemy = { 
            x: 550, y: 110, size: 100, 
            hp: 60 + (stage * 30), maxHp: 60 + (stage * 30),
            name: "ENEMY_NAME_PLACEHOLDER",
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
                y: player.y - 35,
                vx: 0,
                vy: -12,
                size: 9
            });
        }

        function spawnEnemyBullets() {
            let freq = Math.max(15, 45 - (stage * 3));
            if (frameCount % freq === 0) {
                let count = 4 + Math.floor(stage / 2);
                for (let i = 0; i < count; i++) {
                    let angle = (Math.PI / (count + 1)) * (i + 1);
                    let speed = 2.5 + (stage * 0.3);
                    bullets.push({
                        x: enemy.x,
                        y: enemy.y + 50,
                        vx: Math.cos(angle) * speed + (Math.random() - 0.5) * 1.5,
                        vy: Math.sin(angle) * speed + 1.5,
                        size: 9
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

            enemy.moveTimer += 0.04 + (stage * 0.005);
            enemy.x = 550 + Math.sin(enemy.moveTimer) * (200 + stage * 15);

            spawnEnemyBullets();

            for (let i = bullets.length - 1; i >= 0; i--) {
                let b = bullets[i];
                b.x += b.vx;
                b.y += b.vy;

                let dist = Math.hypot(b.x - player.x, b.y - player.y);
                if (dist < (player.size / 2 + b.size - 10)) {
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
            for (let x = 0; x < canvas.width; x += 55) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += 55) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }

            if (enemyLoaded) {
                ctx.drawImage(enemyImg, enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size);
            } else {
                ctx.fillStyle = "#e74c3c";
                ctx.beginPath(); ctx.arc(enemy.x, enemy.y, enemy.size/2, 0, Math.PI*2); ctx.fill();
            }

            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 15px sans-serif";
            ctx.fillText(`Stage STAGE_PLACEHOLDER: ${enemy.name}`, enemy.x, enemy.y - 70);

            ctx.fillStyle = "#333";
            ctx.fillRect(enemy.x - 70, enemy.y - 55, 140, 12);
            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(enemy.x - 70, enemy.y - 55, 140 * (Math.max(0, enemy.hp) / enemy.maxHp), 12);

            if (playerLoaded) {
                ctx.drawImage(playerImg, player.x - player.size/2, player.y - player.size/2, player.size, player.size);
            } else {
                ctx.fillStyle = player.color;
                ctx.beginPath(); ctx.arc(player.x, player.y, player.size/2, 0, Math.PI*2); ctx.fill();
            }

            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 14px sans-serif";
            ctx.fillText(player.name, player.x, player.y + 52);

            ctx.fillStyle = "#333";
            ctx.fillRect(player.x - 45, player.y + 60, 90, 10);
            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(player.x - 45, player.y + 60, 90 * (Math.max(0, player.hp) / player.maxHp), 10);

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
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#ff3333";
                ctx.font = "bold 42px sans-serif";
                ctx.fillText(`${player.name} が倒れた！`, canvas.width / 2, canvas.height / 2 - 25);
                ctx.font = "20px sans-serif";
                ctx.fillStyle = "#fff";
                ctx.fillText("下のボタンから次の仲間と交代してください", canvas.width / 2, canvas.height / 2 + 25);
            } else if (isCleared) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#2ecc71";
                ctx.font = "bold 42px sans-serif";
                ctx.fillText("STAGE CLEAR!!", canvas.width / 2, canvas.height / 2 - 25);
                ctx.font = "20px sans-serif";
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
    .replace("PLAYER_IMAGE_PLACEHOLDER", active_p['image'])\
    .replace("STAGE_PLACEHOLDER", str(current_stage))\
    .replace("PLAYER_HP_PLACEHOLDER", str(active_p['hp']))\
    .replace("PLAYER_MAXHP_PLACEHOLDER", str(active_p['maxHp']))\
    .replace("PLAYER_NAME_PLACEHOLDER", active_p['name'])\
    .replace("PLAYER_COLOR_PLACEHOLDER", active_p['color'])\
    .replace("ENEMY_NAME_PLACEHOLDER", current_enemy_name)

components.html(game_html, height=540)

col_l, col_r = st.columns(2)

with col_l:
    if st.button("⚔️ 次のステージへ進む（クリア後）", use_container_width=True):
        if current_stage < 10:
            st.session_state.stage += 1
            st.success(f"ステージ {st.session_state.stage} に進みます！")
            st.rerun()
        else:
            st.success("🎉 全10ステージ完全踏破！おめでとうございます！")

with col_r:
    if st.button("👥 倒れたキャラを交代してリトライ / 次の仲間へ", use_container_width=True):
        st.session_state.players[st.session_state.active_player_idx]["hp"] = 0
        
        next_idx = None
        for i, p in enumerate(st.session_state.players):
            if p["hp"] > 0:
                next_idx = i
                break
        
        if next_idx is not None:
            st.session_state.active_player_idx = next_idx
            st.success(f"仲間が倒れたため、**{st.session_state.players[next_idx]['name']}** に交代します！")
            st.rerun()
        else:
            st.error("💀 パーティメンバーが全員倒れました... 全滅です。ゲームをリセットしてください。")
