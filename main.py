# 進行ボタン等のコントロールエリア
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
        # 現在のキャラのHPを0（または敗北扱い）にして次の生存キャラを探す
        st.session_state.players[st.session_state.active_player_idx]["hp"] = 0
        
        # 生存している次のキャラクターを探す
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
