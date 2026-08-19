import random
import streamlit as st

# 属性と表示設定
ATTRIBUTES = {
    "火": {"color": "red", "icon": "🔥"},
    "水": {"color": "blue", "icon": "💧"},
    "雷": {"color": "orange", "icon": "⚡"},
    "風": {"color": "green", "icon": "🌪️"},
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

# HP表示
col1, col2 = st.columns(2)
with col1:
  st.metric(
      label="プレイヤー HP",
      value=f"{st.session_state.player_hp}/100",
  )
with col2:
  st.metric(label="AI 相手 HP", value=f"{st.session_state.ai_hp}/100")

st.markdown("---")

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
  # プレイヤーの手札選択
  st.subheader("あなたの手札（攻撃に使うカードを選択してください）")

  selected_indices = []
  cols = st.columns(len(st.session_state.player_hand))

  for i, card in enumerate(st.session_state.player_hand):
    with cols[i]:
      image_path = f"images/{card.suit}_{card.value}.jpg"
      st.image(image_path, width=100)
      st.markdown(
          f"**{ATTRIBUTES[card.suit]['icon']} {card.suit}**<br>数値: **{card.value}**",
          unsafe_allow_html=True,
      )
      if st.checkbox("選択", key=f"card_{i}"):
        selected_indices.append(i)

  if st.button("選択したカードで攻撃！"):
    if not selected_indices:
      st.warning("1枚以上のカードを選択してください。")
    else:
      # プレイヤーの攻撃処理
      chosen_cards = [st.session_state.player_hand[i] for i in selected_indices]
      hand_name, damage = evaluate_hand(chosen_cards)

      damage = int(damage)
      st.session_state.ai_hp = max(0, st.session_state.ai_hp - damage)
      st.session_state.log.insert(
          0,
          f"プレイヤーの攻撃！『{hand_name}』を発動！ AIに **{damage}** のダメージ！",
      )

      # 手札の補充
      selected_indices.sort(reverse=True)
      for idx in selected_indices:
        st.session_state.player_hand.pop(idx)
        if st.session_state.deck:
          st.session_state.player_hand.append(st.session_state.deck.pop())

      # AIのターン（簡易的ランダム反撃）
      if st.session_state.ai_hp > 0 and st.session_state.ai_hand:
        ai_choice = random.choice(st.session_state.ai_hand)
        ai_damage = ai_choice.value * 2
        st.session_state.player_hp = max(
            0, st.session_state.player_hp - ai_damage
        )
        st.session_state.log.insert(
            0,
            f"AIの反撃！{ATTRIBUTES[ai_choice.suit]['icon']} {ai_choice.suit}の{ai_choice.value}で攻撃され、**{ai_damage}** のダメージを受けた！",
        )
        # AIの手札入れ替え
        st.session_state.ai_hand.remove(ai_choice)
        if st.session_state.deck:
          st.session_state.ai_hand.append(st.session_state.deck.pop())

      st.rerun()

  # バトルログ
  st.markdown("### 📜 バトルログ")
  for log in st.session_state.log[:5]:
    st.text(log)
