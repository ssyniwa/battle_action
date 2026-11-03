import streamlit as st
import streamlit.components.v1 as components

# ページの設定（ワイド画面）
st.set_page_config(
    page_title="ダンジョン・ローグアタック：リアルタイム弾幕アクション版",
    page_icon="⚔️",
    layout="wide",
)

st.title("⚔️ ダンジョン・ローグアタック：リアルタイム弾幕アクション版")
st.caption(
    "【操作方法】 左右矢印キー（または A/Dキー）で移動 ｜ スペースキーで攻撃弾を発射！"
    " 飛来する弾を避けて敵を討伐せよ！"
)

# --- HTML / JavaScript によるリアルタイム・キャンバスゲームの実装 ---
# Streamlitのコンポーネントとしてブラウザ上で完全に滑らかな60fpsのアクションゲームを動かします
game_html = """
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
    <canvas id="gameCanvas" width="1000" height="550"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // 画像の読み込み（プレイヤーと敵）
        const playerImg = new Image();
        playerImg.src = "app/static/player1.jpg"; // Streamlitの静的ファイルルート、または相対パス
        // フォールバック用にロード失敗時の色を設定
        let playerLoaded = false;
        playerImg.onload = () => { playerLoaded = true; };

        const enemyImg = new Image();
        enemyImg.src = "app/static/enemy1.jpg";
        let enemyLoaded = false;
        enemyImg.onload = () => { enemyLoaded = true; };

        // ゲームステート
        let player = { x: 500, y: 450, size: 60, speed: 6, hp: 100, maxHp: 100 };
        let enemy = { x: 500, y: 100, size: 90, hp: 200, maxHp: 200 };
        
        let bullets = [];      // 敵からの弾幕
        let playerBullets = []; // 味方からの攻撃弾
        
        let keys = {};
        let frameCount = 0;
        let isGameOver = false;
        let isCleared = false;

        // キー入力リスナー
        window.addEventListener("keydown", (e) => {
            keys[e.code] = true;
            if (e.code === "Space" && !isGameOver && !isCleared) {
                shootPlayerBullet();
                e.preventDefault(); // スパースキーによるスクロール防止
            }
        });
        window.addEventListener("keyup", (e) => {
            keys[e.code] = false;
        });

        function shootPlayerBullet() {
            // 味方から敵へ向かう青いエネルギー弾
            playerBullets.push({
                x: player.x,
                y: player.y - 30,
                vx: 0,
                vy: -10,
                size: 10
            });
        }

        function spawnEnemyBullets() {
            // 敵からの弾幕生成（ステージが進んだ雰囲気を再現）
            if (frameCount % 45 === 0) {
                // プレイヤーめがけて、あるいは放射状に弾を発射
                let count = 5;
                for (let i = 0; i < count; i++) {
                    let angle = (Math.PI / (count + 1)) * (i + 1);
                    bullets.push({
                        x: enemy.x,
                        y: enemy.y + 40,
                        vx: Math.cos(angle) * 3 + (Math.random() - 0.5) * 2,
                        vy: Math.sin(angle) * 3 + 2,
                        size: 10
                    });
                }
            }
        }

        function update() {
            if (isGameOver || isCleared) return;

            // プレイヤーの移動（左右キー または A/D）
            if ((keys["ArrowLeft"] || keys["KeyA"]) && player.x > player.size / 2) {
                player.x -= player.speed;
            }
            if ((keys["ArrowRight"] || keys["KeyD"]) && player.x < canvas.width - player.size / 2) {
                player.x += player.speed;
            }

            // 弾幕生成
            spawnEnemyBullets();

            // 敵の弾の移動と当たり判定
            for (let i = bullets.length - 1; i >= 0; i--) {
                let b = bullets[i];
                b.x += b.vx;
                b.y += b.vy;

                // プレイヤーとの当たり判定
                let dist = Math.hypot(b.x - player.x, b.y - player.y);
                if (dist < (player.size / 2 + b.size)) {
                    player.hp -= 10;
                    bullets.splice(i, 1);
                    if (player.hp <= 0) {
                        isGameOver = true;
                    }
                    continue;
                }

                // 画面外削除
                if (b.y > canvas.height || b.x < 0 || b.x > canvas.width) {
                    bullets.splice(i, 1);
                }
            }

            // プレイヤーの攻撃弾の移動と敵への当たり判定
            for (let i = playerBullets.length - 1; i >= 0; i--) {
                let pb = playerBullets[i];
                pb.x += pb.vx;
                pb.y += pb.vy;

                // 敵との当たり判定
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
            // 背景クリア
            ctx.fillStyle = "#0f111a";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // グリッド線
            ctx.strokeStyle = "#1c2130";
            ctx.lineWidth = 1;
            for (let x = 0; x < canvas.width; x += 50) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += 50) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }

            // 敵の描画
            if (enemyLoaded) {
                ctx.drawImage(enemyImg, enemy.x - enemy.size/2, enemy.y - enemy.size/2, enemy.size, enemy.size);
            } else {
                ctx.fillStyle = "#e74c3c";
                ctx.beginPath(); ctx.arc(enemy.x, enemy.y, enemy.size/2, 0, Math.PI*2); ctx.fill();
            }

            // 敵HPバー
            ctx.fillStyle = "#333";
            ctx.fillRect(enemy.x - 60, enemy.y - 65, 120, 12);
            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(enemy.x - 60, enemy.y - 65, 120 * (Math.max(0, enemy.hp) / enemy.maxHp), 12);

            // プレイヤー（自機）の描画
            if (playerLoaded) {
                ctx.drawImage(playerImg, player.x - player.size/2, player.y - player.size/2, player.size, player.size);
            } else {
                ctx.fillStyle = "#3498db";
                ctx.beginPath(); ctx.arc(player.x, player.y, player.size/2, 0, Math.PI*2); ctx.fill();
            }

            // プレイヤーHPバー
            ctx.fillStyle = "#333";
            ctx.fillRect(player.x - 40, player.y + 40, 80, 10);
            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(player.x - 40, player.y + 40, 80 * (Math.max(0, player.hp) / player.maxHp), 10);

            // 敵からの弾 (赤)
            ctx.fillStyle = "#ff3333";
            for (let b of bullets) {
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
                ctx.fill();
            }

            // プレイヤーの攻撃弾 (青)
            ctx.fillStyle = "#33ccff";
            for (let pb of playerBullets) {
                ctx.beginPath();
                ctx.arc(pb.x, pb.y, pb.size, 0, Math.PI * 2);
                ctx.fill();
            }

            // ゲームオーバー / クリア表示
            if (isGameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#ff3333";
                ctx.font = "bold 40px sans-serif";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);
                ctx.font = "20px sans-serif";
                ctx.fillStyle = "#fff";
                ctx.fillText("ページを再読み込みしてリトライしてください", canvas.width / 2, canvas.height / 2 + 30);
            } else if (isCleared) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#2ecc71";
                ctx.font = "bold 40px sans-serif";
                ctx.fillText("STAGE CLEAR!!", canvas.width / 2, canvas.height / 2 - 20);
                ctx.font = "20px sans-serif";
                ctx.fillStyle = "#fff";
                ctx.fillText("敵を完全に討伐しました！", canvas.width / 2, canvas.height / 2 + 30);
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

# Streamlit上にHTMLコンポーネントとして描画（高さ580px）
components.html(game_html, height=580)

# リセット用ボタン
if st.button("🔄 ゲームをリセット"):
  st.rerun()
