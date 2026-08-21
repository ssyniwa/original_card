import random
import streamlit as st
import itertools
# 属性と表示設定
ATTRIBUTES = {
    "fire": {"color": "red", "icon": "🔥"},
    "water": {"color": "blue", "icon": "💧"},
    "thunder": {"color": "orange", "icon": "⚡"},
    "wind": {"color": "green", "icon": "🌪️"},
}


# カードクラス
class Card:

  def __init__(self, suit, value):
    self.suit = suit  # 属性 (火、水、雷、風)
    self.value = value  # 数字 (1〜13)

  def __str__(self):
    return (
        f"{ATTRIBUTES[self.suit]['icon']} {self.suit}の{self.value}"
    )


# デッキの作成
def create_deck():
  deck = []
  for suit in ATTRIBUTES.keys():
    for value in range(1, 14):
      deck.append(Card(suit, value))
  random.shuffle(deck)
  return deck


# 初期化
if "initialized" not in st.session_state:
  st.session_state.player_hp = 1000
  st.session_state.ai_hp = 1000
  st.session_state.deck = create_deck()
  st.session_state.player_hand = [
      st.session_state.deck.pop() for _ in range(5)
  ]
  st.session_state.ai_hand = [st.session_state.deck.pop() for _ in range(5)]
  st.session_state.log = [
      "ゲーム開始！カードを選んで攻撃またはコンボを狙おう。"
  ]
  st.session_state.initialized = True
  # 追記：AIの直前行動を記録する場所
  st.session_state.ai_last_card = None

# 役判定関数
def evaluate_hand(cards):
    if not cards:
        return "選択なし", 0

    suits = [c.suit for c in cards]
    values = sorted([c.value for c in cards])

    is_same_suit = len(set(suits)) == 1
    # 数字のカウント
    val_counts = {v: values.count(v) for v in set(values)}
    max_count = max(val_counts.values())
    
    # 連番チェック
    is_sequential = all(values[i] + 1 == values[i+1] for i in range(len(values)-1))
    
    base_power = sum(values)

    # 1. ストレートフラッシュ (3枚以上で連番かつ同属性)
    if len(cards) >= 3 and is_same_suit and is_sequential:
        return "🌟 ストレートフラッシュ", base_power * 4.0
    
    # 2. フォーカード
    if max_count == 4:
        return "🍀 フォーカード", base_power * 3.5
        
    # 3. スリーカード
    if max_count == 3:
        return "🔥 スリーカード", base_power * 2.5
        
    # 4. フラッシュ (同属性)
    if len(cards) >= 2 and is_same_suit:
        return "🌊 フラッシュ", base_power * 2.0
        
    # 5. ペア
    if max_count == 2:
        return "✨ ペア", base_power * 1.5

    return "通常攻撃", base_power
def get_ai_best_move(hand):
    """手札から最強かつ正確なコンボを探すAI"""
    if not hand:
        return [], 0
        
    best_move = [hand[0]]
    _, max_damage = evaluate_hand(best_move)
    
    # 1枚から手札の最大枚数までのすべての組み合わせを検証
    for r in range(1, len(hand) + 1):
        for combo in itertools.combinations(hand, r):
            combo_list = list(combo)
            hand_name, damage = evaluate_hand(combo_list)
            
            # 「通常攻撃」よりも役（コンボ）が成立しているものを優先しつつ、
            # ダメージがより高い組み合わせを採用する
            if hand_name != "通常攻撃":
                # コンボの場合は少し優先度を上げる、または純粋にダメージ比較
                if damage > max_damage:
                    max_damage = damage
                    best_move = combo_list
            else:
                # 通常攻撃（1枚の場合など）の比較
                if damage > max_damage and r == 1:
                    max_damage = damage
                    best_move = combo_list
                    
    # 万が一の保険：もしbest_moveが空なら手札の最初の1枚にする
    if not best_move:
        best_move = [hand[0]]
        _, max_damage = evaluate_hand(best_move)
        
    return best_move, max_damage

# 画面レイアウト
st.title("🃏 属性トランプ・AIカードバトル")



# ゲーム終了判定
if st.session_state.player_hp <= 0:
  st.error("敗北しました...！AIの勝利です。")
  if st.button("もう一度プレイ"):
    for key in list(st.session_state.keys()):
      del st.session_state[key]
    st.rerun()
elif st.session_state.ai_hp <= 0:
  st.success("おめでとうございます！あなたの勝利です！")
  if st.button("もう一度プレイ"):
    for key in list(st.session_state.keys()):
      del st.session_state[key]
    st.rerun()
else:
  # 1. 対面バトルエリア（AIの場）
  st.subheader("🤖 AIの場")
  # ai_last_card がリストかどうか判定して表示
  if st.session_state.ai_last_card:
      ai_cards = st.session_state.ai_last_card
      
      # 役の判定結果を再計算して表示（ログだけだと分かりにくいため）
      hand_name, _ = evaluate_hand(ai_cards)
      
      
      # カードを並べて表示するためのカラム作成
      ai_cols = st.columns(len(ai_cards))
      for i, card in enumerate(ai_cards):
          with ai_cols[i]:
              st.image(f"images/{card.suit}_{card.value}.jpg", width=120)
              st.caption(f"{ATTRIBUTES[card.suit]['icon']} {card.value}")
  else:
      st.write("AIはまだカードを出していません。")
  
  st.markdown("---")
  
  # 2. HP表示
  col_h1, col_h2 = st.columns(2)
  with col_h1:
      st.metric("プレイヤー HP", f"{st.session_state.player_hp}/1000")
  with col_h2:
      st.metric("AI 相手 HP", f"{st.session_state.ai_hp}/1000")
  
  st.markdown("---")
  
  # 3. プレイヤーの手札選択（プレイヤーの場）
  st.subheader("👤 あなたの手札")
  selected_indices = []
  
  # ★安全策：手札が空でないことを保証する（0枚なら1以上のカラムにする）
  num_player_cols = max(1, len(st.session_state.player_hand))
  cols = st.columns(num_player_cols)
  
  for i, card in enumerate(st.session_state.player_hand):
      with cols[i]:
          st.image(f"images/{card.suit}_{card.value}.jpg", width=120)
          st.caption(f"{ATTRIBUTES[card.suit]['icon']} {card.value}")
          if st.checkbox("選択", key=f"card_{i}"):
              selected_indices.append(i)
  
  # --- 攻撃ボタン処理 ---
  if st.button("選択したカードで攻撃！"):
      if not selected_indices:
          st.warning("カードを選択してください。")
      else:
          # プレイヤーの攻撃処理
          chosen_cards = [st.session_state.player_hand[i] for i in selected_indices]
          phand_name, damage = evaluate_hand(chosen_cards)
          st.session_state.ai_hp = max(0, st.session_state.ai_hp - int(damage))
          st.session_state.log.insert(0, f"プレイヤーの『{phand_name}』！『{int(damage)}』のダメージを与えた！")
          # 手札の更新
          selected_indices.sort(reverse=True)
          for idx in selected_indices:
              st.session_state.player_hand.pop(idx)
              if st.session_state.deck:
                  st.session_state.player_hand.append(st.session_state.deck.pop())
  
          # AIのターン：手札の中でコンボを狙う
          if st.session_state.ai_hp > 0 and st.session_state.ai_hand:
            # 最強の組み合わせを選択（ai_choiceには選ばれたカードのリスト、ai_damageにはそのダメージが入る）
            ai_choice, ai_damage = get_ai_best_move(st.session_state.ai_hand)
            
            if ai_choice:
                # 実際にコンボに使ったカードだけを記録
                st.session_state.ai_last_card = ai_choice 
                
                st.session_state.player_hp = max(0, st.session_state.player_hp - int(ai_damage))
                
                # 役の名前もログに出すようにする
                hand_name, _ = evaluate_hand(ai_choice)
                st.session_state.log.insert(0, f"AIの『{hand_name}』！ **{int(ai_damage)}** のダメージを受けた！")
                
                # AIの手札から「コンボに使用したカードのみ」を除去して、使った枚数分だけデッキから補充
                for card in ai_choice:
                    if card in st.session_state.ai_hand:
                        st.session_state.ai_hand.remove(card)
                
                # 減った枚数分を補充
                for _ in range(len(ai_choice)):
                    if st.session_state.deck:
                        st.session_state.ai_hand.append(st.session_state.deck.pop())
  
          st.rerun()
  
  # 4. バトルログ
  st.subheader("📜 バトルログ")
  for log in st.session_state.log[:3]:
      st.text(log)
