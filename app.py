import random
import streamlit as st

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
  st.session_state.player_hp = 100
  st.session_state.ai_hp = 100
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
  is_same_value = len(set(values)) == 1
  is_sequential = (
      values == list(range(values[0], values[0] + len(values)))
      if len(values) > 1
      else True
  )

  base_power = sum(values)

  # ストレートフラッシュ (3枚以上で連番かつ同属性)
  if len(cards) >= 3 and is_same_suit and is_sequential:
    return (
        "🌟 ストレートフラッシュ！【超絶強力な神速の一撃】",
        base_power * 4,
    )

  # 同色フラッシュ (同属性)
  if len(cards) >= 2 and is_same_suit:
    return f"🔥 {cards[0].suit}のフラッシュ【属性共鳴】", base_power * 2

  # 同数ペア
  if is_same_value:
    return f"✨ 同数コンボ（{len(cards)}枚）", base_power * 1.5

  return "普通の一撃", base_power


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
  if st.session_state.ai_last_card:
      c = st.session_state.ai_last_card
      col_ai1, col_ai2 = st.columns([1, 4])
      with col_ai1:
          st.image(f"images/{c.suit}_{c.value}.jpg", width=120)
      with col_ai2:
          st.write(f"### AIは {ATTRIBUTES[c.suit]['icon']} {c.suit} の {c.value} を出した！")
  else:
      st.write("AIはまだカードを出していません。")
  
  st.markdown("---")
  
  # 2. HP表示
  col_h1, col_h2 = st.columns(2)
  with col_h1:
      st.metric("プレイヤー HP", f"{st.session_state.player_hp}/100")
  with col_h2:
      st.metric("AI 相手 HP", f"{st.session_state.ai_hp}/100")
  
  st.markdown("---")
  
  # 3. プレイヤーの手札選択（プレイヤーの場）
  st.subheader("👤 あなたの手札")
  selected_indices = []
  cols = st.columns(len(st.session_state.player_hand))
  
  for i, card in enumerate(st.session_state.player_hand):
      with cols[i]:
          st.image(f"images/{card.suit}_{card.value}.jpg", width=120)
          st.checkbox("選択", key=f"card_{i}")
          if st.session_state.get(f"card_{i}"):
              selected_indices.append(i)
  
  # --- 攻撃ボタン処理 ---
  if st.button("選択したカードで攻撃！"):
      if not selected_indices:
          st.warning("カードを選択してください。")
      else:
          # プレイヤーの攻撃処理
          chosen_cards = [st.session_state.player_hand[i] for i in selected_indices]
          hand_name, damage = evaluate_hand(chosen_cards)
          st.session_state.ai_hp = max(0, st.session_state.ai_hp - int(damage))
          
          # 手札の更新
          selected_indices.sort(reverse=True)
          for idx in selected_indices:
              st.session_state.player_hand.pop(idx)
              if st.session_state.deck:
                  st.session_state.player_hand.append(st.session_state.deck.pop())
  
          # AIのターン：手札の中で最も数値が高いカードを選択
          if st.session_state.ai_hp > 0:
              # 戦略：手札の中で最強のカードを選ぶ
              ai_choice = max(st.session_state.ai_hand, key=lambda x: x.value)
              st.session_state.ai_last_card = ai_choice
              
              ai_damage = ai_choice.value * 2
              st.session_state.player_hp = max(0, st.session_state.player_hp - ai_damage)
              
              # AIの手札入れ替え
              st.session_state.ai_hand.remove(ai_choice)
              if st.session_state.deck:
                  st.session_state.ai_hand.append(st.session_state.deck.pop())
  
          st.rerun()
  
  # 4. バトルログ
  st.subheader("📜 バトルログ")
  for log in st.session_state.log[:3]:
      st.text(log)
