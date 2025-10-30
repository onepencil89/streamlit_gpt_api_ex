import base64
from io import BytesIO
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image
import pyperclip

# .env 파일 로드
load_dotenv(override=True)

# Open AI API 키 설정 및 OpenAI 객체 생성
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# 이미지를 Base64로 변환하는 함수
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # PNG 형식으로 변환
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# 이미지 파일을 분석하여 설명을 반환하는 함수
def ai_describe(image_data, is_url=True):
    try:
        if is_url:
            image_content = {"type": "image_url", "image_url": {"url": image_data}}
        else:
            base64_image = encode_image(image_data)  # 이미지를 Base64로 변환
            image_content = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 미술관 20년이상 경력을 보야한 전문 큐레이터입니다."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "이 이미지에 대해서 자세하게 설명해 주세요."},
                        image_content,
                    ],
                }
            ],
            max_tokens=1024,
        )

        text = response.choices[0].message.content
        return text
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 웹 앱 UI 설정
st.title("AI 도슨트: 이미지를 설명해드려요!")

# 선택 탭 추가
tab1, tab2 = st.tabs(["이미지 파일 업로드", "이미지 URL 입력"])

with tab1:
    uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, width=300)
        if st.button("해설", key="file_button"):
            image = Image.open(uploaded_file)  # PIL 이미지 열기
            result = ai_describe(image, is_url=False)
            st.code(result, language=None)
             

with tab2:
    st.text("적용하려면 ctrl + enter를 눌러주세요")
    input_url = st.text_area("이미지 URL을 입력하세요", height=70)
    if input_url:
        st.image(input_url, width=300)
        if st.button("해설", key="url_button"):
            result = ai_describe(input_url, is_url=True)
            st.code(result, language=None)
