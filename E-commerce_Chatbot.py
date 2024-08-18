from openai import OpenAI
import streamlit as st
import comet_llm

# Comet API 키 설정

MY_COMET_KEY = 'AqLaPzNJxWIxibcKnZkqMWL1d' # st.secrets["comet_api_key"]

# Comet LLM 초기화
comet_llm.init(project='E-commerce_Chatbot', api_key=MY_COMET_KEY) # 이름 변경하기

# Product List 및 Context 설정
product_list = '''
# Fashion Shop Product List

## Men's Clothing:
- T-shirt
  - Price: $20
  - Available Sizes: Small, Medium, Large, XL
  - Available Colors: Green, White, Black, Gray, Navy

- Jeans
  - Price: $50
  - Available Sizes: Small, Medium, Large, XL
  - Available Colors: Blue, Black, Gray, Navy

## Women's Clothing:
- T-shirt
  - Price: $20
  - Available Sizes: Small, Medium, Large, XL
  - Available Colors: Red, White, Black, Gray, Navy

- Dress
  - Price: $50
  - Available Sizes: Small, Medium, Large, XL
  - Available Colors: Red, White, Black, Gray, Navy

# ... (Other product categories and details)
'''

context = [{'role': 'system',
            'content': f"""
You are ShopBot, an AI assistant for my online fashion shop - Trendy Fashion.

Your role is to assist customers in browsing products, providing information, and guiding them through the checkout process.

Be friendly and helpful in your interactions.

We offer a variety of products across categories such as Women's Clothing, Men's clothing, Accessories, Kids' Collection, Footwears and Activewear products.

Feel free to ask customers about their preferences, recommend products, and inform them about any ongoing promotions.

The Current Product List is limited as below:

```{product_list}```

Make the shopping experience enjoyable and encourage customers to reach out if they have any questions or need assistance.
"""}]

with st.sidebar:
    openai_api_key = st.text_input('OpenAI API Key', key='chatbot_api_key', type='password')

st.title('Trendy Fashion 챗봇')
st.caption('AI 쇼핑 어시스턴트입니다.')

# 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# 대화 기록을 화면에 출력
for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

# 사용자 입력 처리 및 GPT 응답 생성
if prompt := st.chat_input():
    if not openai_api_key.startswith('sk-'):
        st.warning('OpenAI API Key를 입력하세요!', icon='⚠')
        st.stop()

    # 사용자 입력을 대화 기록에 추가
    st.session_state['messages'].append({'role': 'user', 'content': prompt})
    st.chat_message('user').write(prompt)

    # GPT 모델을 사용하여 응답 생성 (context를 메시지에 추가하여 사용)
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=context + st.session_state['messages']
    )
    
    # 응답 메시지를 대화 기록에 추가
    msg = response.choices[0].message.content
    st.session_state['messages'].append({'role': 'assistant', 'content': msg})
    st.chat_message('assistant').write(msg)

    # Comet LLM 로그 저장
    comet_llm.log_prompt(
        prompt=prompt,
        output=msg,
        metadata={
            'role': st.session_state['messages'][-1]['role'],
            'content': st.session_state['messages'][-1]['content'],
            'context': st.session_state['messages'],
            'product_list': product_list
        }
    )
