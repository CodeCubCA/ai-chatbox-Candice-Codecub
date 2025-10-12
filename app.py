"""
AI学习助手 - 使用Streamlit和Groq API
这是一个智能学习伙伴，可以帮助你解答问题、解释概念、提供学习建议
"""

import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化Groq客户端
def init_groq_client():
    """初始化Groq API客户端"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ 请设置GROQ_API_KEY环境变量")
        st.stop()
    return Groq(api_key=api_key)

# 页面配置
st.set_page_config(
    page_title="AI学习助手",
    page_icon="📚",
    layout="wide"
)

# 标题和说明
st.title("📚 AI学习助手")
st.markdown("你好！我是你的智能学习伙伴，可以帮你解答问题、解释概念、提供学习建议。")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 添加欢迎消息
    st.session_state.messages.append({
        "role": "assistant",
        "content": "你好！我是你的AI学习助手。无论你想学习什么知识，或者有什么问题需要解答，都可以问我！💡"
    })

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("输入你的问题..."):
    # 添加用户消息到聊天历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 获取AI回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # 初始化客户端
            client = init_groq_client()

            # 准备消息历史（添加系统提示）
            messages = [
                {
                    "role": "system",
                    "content": "你是一个友好、耐心的AI学习助手。你的任务是帮助学生学习和理解各种知识。请用清晰、易懂的方式解释概念，并在必要时提供例子。保持鼓励和支持的态度。"
                }
            ]
            # 添加历史对话
            messages.extend(st.session_state.messages)

            # 调用Groq API（流式输出）
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True
            )

            # 显示流式响应
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"抱歉，发生了错误：{str(e)}"
            message_placeholder.markdown(full_response)

        # 添加AI回复到聊天历史
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")

    # 清空对话按钮
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "你好！我是你的AI学习助手。无论你想学习什么知识，或者有什么问题需要解答，都可以问我！💡"
        })
        st.rerun()

    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.markdown("""
    - 问我任何学习相关的问题
    - 请我解释复杂的概念
    - 让我帮你复习知识点
    - 寻求学习方法建议
    - 请我出题测试你的理解
    """)

    st.markdown("---")
    st.markdown("### 📊 对话统计")
    st.markdown(f"消息数量: {len(st.session_state.messages)}")

    st.markdown("---")
    st.markdown("**模型**: llama-3.3-70b-versatile")
    st.markdown("**技术栈**: Streamlit + Groq API")
