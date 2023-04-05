# -*- coding:utf-8 -*-
import gradio as gr

# ChatGPT 设置
initial_prompt = '''
我们是数据开发组，每个同事会写多个sql脚本。这些sql脚本中包含一些开发同事定义的参数，称为开发参数，
需要传入这些参数才可以执行脚本。开发参数的参数名可以随意，但是必须引用几个基础
参数，或称为引用参数。
这些引用参数都基于跑批日期，跑批日期指的是当前自然日期的上一个自然日。
这些引用参数有：
1.base_date: 和跑批日期相等。开发参数可以在其基础上按天偏移，如-1d、2d等，且可以指定是偏移自然日或工作日。
2.first_wkdate_bymonth：跑批日期所在月的第一个工作日。开发参数可以在其基础上按月偏移，如-1m、2m等，没有偏移自然日或工作日的概念。
3.last_wkdate_bymonth：跑批日期所在月的最后一个工作日。开发参数可以在其基础上按月偏移，如-1m、2m等，没有偏移自然日或工作日的概念。
4.first_date_bymonth：跑批日期所在月的第一个自然日。开发参数可以在其基础上按月偏移，如-1m、2m等，没有偏移自然日或工作日的概念。
5.last_date_bymonth：跑批日期所在月的最后一个自然日。开发参数可以在其基础上按月偏移，如-1m、2m等，没有偏移自然日或工作日的概念。
6.first_wkdate_byweek：跑批日期所在周的第一个工作日。开发参数可以在其基础上按周偏移，如-1w、2w等，没有偏移自然日或工作日的概念。
7.last_wkdate_byweek：跑批日期所在周的最后一个工作日。开发参数可以在其基础上按周偏移，如-1w、2w等，没有偏移自然日或工作日的概念。
8.first_date_byweek：跑批日期所在周的第一个自然日。开发参数可以在其基础上按周偏移，如-1w、2w等，没有偏移自然日或工作日的概念。
9.last_date_byweek：跑批日期所在周的最后一个自然日。开发参数可以在其基础上按周偏移，如-1w、2w等，没有偏移自然日或工作日的概念。
对于date结尾的参数，偏移量必须以d结尾，代表偏移的是天。对于bymonth结尾的参数，偏移量必须以m结尾，代表偏移的是月。
对于byweek结尾的参数，偏移量必须以w结尾，代表偏移的是周。
例子1：开发同事可以自定义一个参数startdate,它等于base_date-2d，并指定偏移工作日，这代表取跑批日期的前两个工作日。
例子2：开发同事可以自定义一个参数startdate,它等于first_wkdate_bymonth-2m，这代表取跑批日期的所在月的前两个月的第一个工作日。
例子3：开发同事可以自定义一个参数startdate,它等于first_date_byweek-1w，这代表取跑批日期的所在周的上一周的第一个自然日。
你负责做我的小助手，如果有开发同事人向你问起脚本如何配置自己的参数的话，按我说的回答他。
明白的话回我"明白"
'''
API_URL = "https://api.openai.com/v1/chat/completions"
BALANCE_API_URL="https://127.0.0.1"
USAGE_API_URL="https://127.0.0.1"
HISTORY_DIR = "history"
TEMPLATES_DIR = "templates"

# 错误信息
standard_error_msg = "☹️发生了错误："  # 错误信息的标准前缀
error_retrieve_prompt = "请检查网络连接，或者API-Key是否有效。"  # 获取对话时发生错误
connection_timeout_prompt = "连接超时，无法获取对话。"  # 连接超时
read_timeout_prompt = "读取超时，无法获取对话。"  # 读取超时
proxy_error_prompt = "代理错误，无法获取对话。"  # 代理错误
ssl_error_prompt = "SSL错误，无法获取对话。"  # SSL 错误
no_apikey_msg = "API key长度不是51位，请检查是否输入正确。"  # API key 长度不足 51 位
no_input_msg = "请输入对话内容。"  # 未输入对话内容

timeout_streaming = 10  # 流式对话时的超时时间
timeout_all = 200  # 非流式对话时的超时时间
enable_streaming_option = True  # 是否启用选择选择是否实时显示回答的勾选框
HIDE_MY_KEY = True  # 如果你想在UI中隐藏你的 API 密钥，将此值设置为 True
CONCURRENT_COUNT = 10 # 允许同时使用的用户数量

SIM_K = 5
INDEX_QUERY_TEMPRATURE = 1.0

title = """<h2 align="left" style="min-width:200px; margin-top:0;">向ChatGPT询问调度相关问题，比如如何获得上个月的第一个工作日</h2>"""
description = """\
"""

footer = """\
<div class="versions">{versions}</div>
"""

summarize_prompt = "你是谁？我们刚才聊了什么？"  # 总结对话时的 prompt

MODELS = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
]  # 可选的模型

MODEL_SOFT_TOKEN_LIMIT = {
    "gpt-3.5-turbo": {
        "streaming": 3500,
        "all": 3500
    },
    "gpt-3.5-turbo-0301": {
        "streaming": 3500,
        "all": 3500
    },
    "gpt-4": {
        "streaming": 7500,
        "all": 7500
    },
    "gpt-4-0314": {
        "streaming": 7500,
        "all": 7500
    },
    "gpt-4-32k": {
        "streaming": 31000,
        "all": 31000
    },
    "gpt-4-32k-0314": {
        "streaming": 31000,
        "all": 31000
    }
}

REPLY_LANGUAGES = [
    "简体中文",
    "繁體中文",
    "English",
    "日本語",
    "Español",
    "Français",
    "Deutsch",
    "跟随问题语言（不稳定）"
]


WEBSEARCH_PTOMPT_TEMPLATE = """\
Web search results:

{web_results}
Current date: {current_date}

Instructions: Using the provided web search results, write a comprehensive reply to the given query. Make sure to cite results using [[number](URL)] notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.
Query: {query}
Reply in {reply_language}
"""

PROMPT_TEMPLATE = """\
Context information is below.
---------------------
{context_str}
---------------------
Current date: {current_date}.
Using the provided context information, write a comprehensive reply to the given query.
Make sure to cite results using [number] notation after the reference.
If the provided context information refer to multiple subjects with the same name, write separate answers for each subject.
Use prior knowledge only if the given context didn't provide enough information.
Answer the question: {query_str}
Reply in {reply_language}
"""

REFINE_TEMPLATE = """\
The original question is as follows: {query_str}
We have provided an existing answer: {existing_answer}
We have the opportunity to refine the existing answer
(only if needed) with some more context below.
------------
{context_msg}
------------
Given the new context, refine the original answer to better
Reply in {reply_language}
If the context isn't useful, return the original answer.
"""

ALREADY_CONVERTED_MARK = "<!-- ALREADY CONVERTED BY PARSER. -->"

small_and_beautiful_theme = gr.themes.Soft(
        primary_hue=gr.themes.Color(
            c50="#02C160",
            c100="rgba(2, 193, 96, 0.2)",
            c200="#02C160",
            c300="rgba(2, 193, 96, 0.32)",
            c400="rgba(2, 193, 96, 0.32)",
            c500="rgba(2, 193, 96, 1.0)",
            c600="rgba(2, 193, 96, 1.0)",
            c700="rgba(2, 193, 96, 0.32)",
            c800="rgba(2, 193, 96, 0.32)",
            c900="#02C160",
            c950="#02C160",
        ),
        secondary_hue=gr.themes.Color(
            c50="#576b95",
            c100="#576b95",
            c200="#576b95",
            c300="#576b95",
            c400="#576b95",
            c500="#576b95",
            c600="#576b95",
            c700="#576b95",
            c800="#576b95",
            c900="#576b95",
            c950="#576b95",
        ),
        neutral_hue=gr.themes.Color(
            name="gray",
            c50="#f9fafb",
            c100="#f3f4f6",
            c200="#e5e7eb",
            c300="#d1d5db",
            c400="#B2B2B2",
            c500="#808080",
            c600="#636363",
            c700="#515151",
            c800="#393939",
            c900="#272727",
            c950="#171717",
        ),
        radius_size=gr.themes.sizes.radius_sm,
    ).set(
        button_primary_background_fill="#06AE56",
        button_primary_background_fill_dark="#06AE56",
        button_primary_background_fill_hover="#07C863",
        button_primary_border_color="#06AE56",
        button_primary_border_color_dark="#06AE56",
        button_primary_text_color="#FFFFFF",
        button_primary_text_color_dark="#FFFFFF",
        button_secondary_background_fill="#F2F2F2",
        button_secondary_background_fill_dark="#2B2B2B",
        button_secondary_text_color="#393939",
        button_secondary_text_color_dark="#FFFFFF",
        # background_fill_primary="#F7F7F7",
        # background_fill_primary_dark="#1F1F1F",
        block_title_text_color="*primary_500",
        block_title_background_fill="*primary_100",
        input_background_fill="#F6F6F6",
    )
