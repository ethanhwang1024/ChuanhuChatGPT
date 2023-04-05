# -*- coding:utf-8 -*-
import os
import logging
import sys
import webbrowser

import gradio as gr

from modules.utils import *
from modules.presets import *
from modules.overwrites import *
from modules.chat_func import *
# from modules.openai_func import get_usage
import calendar
import time

import gradio as gr
import pandas as pd

from datetime import datetime
import datetime as dt
import exchange_calendars as ec

from Db import *



logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
)


my_api_key = ""  # 在这里输入你的 API 密钥

# if we are running in Docker
if os.environ.get("dockerrun") == "yes":
    dockerflag = True
else:
    dockerflag = False

authflag = False
auth_list = []


#
# def redirect_to_outside():
#     webbrowser.open_new_tab("https://chatgpt.insjc.info/")


if not my_api_key:
    my_api_key = os.environ.get("my_api_key")
if dockerflag:
    if my_api_key == "empty":
        logging.error("Please give a api key!")
        sys.exit(1)
    # auth
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")
    if not (isinstance(username, type(None)) or isinstance(password, type(None))):
        auth_list.append((os.environ.get("USERNAME"), os.environ.get("PASSWORD")))
        authflag = True
else:
    if (
        not my_api_key
        and os.path.exists("api_key.txt")
        and os.path.getsize("api_key.txt")
    ):
        with open("api_key.txt", "r") as f:
            my_api_key = f.read().strip()
    if os.path.exists("auth.json"):
        authflag = True
        with open("auth.json", "r", encoding='utf-8') as f:
            auth = json.load(f)
            for _ in auth:
                if auth[_]["username"] and auth[_]["password"]:
                    auth_list.append((auth[_]["username"], auth[_]["password"]))
                else:
                    logging.error("请检查auth.json文件中的用户名和密码！")
                    sys.exit(1)

gr.Chatbot.postprocess = postprocess
PromptHelper.compact_text_chunks = compact_text_chunks

with open("assets/custom.css", "r", encoding="utf-8") as f:
    customCSS = f.read()


# with open("./custom.css", "r", encoding="utf-8") as f:
#     customCSS = f.read()
with gr.Blocks(css=customCSS,theme=small_and_beautiful_theme) as demo:
    gr.HTML("""<h1 align="left" style="min-width:200px; margin-top:0;">统一参数配置平台DEMO</h1>""")


    sql_name = gr.Textbox(
        show_label=True,
        placeholder="输入脚本名",
        visible=True,
        label="输入脚本名并回车以搜索,支持模糊匹配"
    )

    inter_df = gr.DataFrame(
        headers=["id","脚本名", "脚本参数", "参数类型", "引用参数", "偏移量", "偏移属性(对周月偏移无效)", "固定值"],
        datatype=["str","str", "str", "str", "str", "str", "str","str"],
        max_rows=10,
        col_count=[8,"fixed"],
        interactive=True
    )
    def readAll(sqlName=''):
        df = read_data()
        df = df.sort_values(by=['name'])
        df = df.rename({'name':'脚本名','param':'脚本参数','paramtype':'参数类型','referparam':'引用参数','diff':'偏移量','difftype':'偏移属性','fixvalue':'固定值'},axis=1)
        if sqlName!='':
            df = df[df['脚本名'].str.contains(sqlName)]
        if len(df)==0:
            df = pd.DataFrame(data=None,columns=['result'])
            df.loc[1] = ['不存在该脚本']
        return df

    def readAllWait(sqlName=''):
        time.sleep(4)
        df = read_data()
        df = df.sort_values(by=['name'])
        df = df.rename({'name':'脚本名','param':'脚本参数','paramtype':'参数类型','referparam':'引用参数','diff':'偏移量','difftype':'偏移属性','fixvalue':'固定值'},axis=1)
        if sqlName!='':
            df = df[df['脚本名'].str.contains(sqlName)]
        if len(df)==0:
            df = pd.DataFrame(data=None,columns=['result'])
            df.loc[1] = ['不存在该脚本']
        return df


    sql_name.submit(readAll,inputs=sql_name,outputs=inter_df)
    demo.load(readAll,inputs=None,outputs=inter_df)


    with gr.Row():
        submitBtn = gr.Button("提交修改或新增记录",elem_id="submit_btn")
        refreshBtn = gr.Button("刷新",elem_id="refresh_btn")
        def submitdata(df):
            df = df.rename({'脚本名': 'name', '脚本参数': 'param', '参数类型': 'paramtype', '引用参数': 'referparam', '偏移量': 'diff',
                            '偏移属性': 'difftype', '固定值': 'fixvalue'}, axis=1)
            save_data(df)
        submitBtn.click(submitdata,inputs=inter_df,outputs=None)
        # submitBtn.click(submitdata, inputs=inter_df, outputs=None).then(readAll, inputs=sql_name, outputs=inter_df)

        submitBtn.click(readAllWait,inputs=sql_name,outputs=inter_df)
        refreshBtn.click(readAll,inputs=sql_name,outputs=inter_df)

    # fac1 = gr.Interface(
    #     read_excel_file,
    #     inputs="file",
    #     outputs="html",
    #     description="也可上传excel，请参考样例表格",
    #     id="i1"
    # )

    with gr.Column():
        with gr.Column():
            gr.Markdown("")
            gr.Markdown("")
            gr.Markdown("<h3>样例如下：<h3>")
            gr.Markdown("引用参数base_date，按日偏移，可以是自然日或者是工作日")
            gr.Markdown("引用参数first_wkdate_bymonth，按月偏移，其他bymonth参数也是按月偏移")
            gr.Markdown("引用参数first_wkdate_byweek，按周偏移，其他byweek参数也是按周偏移")
            gr.DataFrame(
                headers=["脚本名", "脚本参数", "参数类型", "引用参数", "偏移量", "偏移属性(对周月偏移无效)", "固定值"],
                value=[["1_TEST.SQL", "startdate", "refer", "base_date", "-10d", "自然日", ""],
                       ["1_TEST.SQL", "enddate", "refer", "base_date", "-1d", "工作日"],
                       ["1_TEST.SQL", "validday", "fix", "", "", "", "30"],
                       ["1_TEST2.SQL", "startdate", "refer", "first_wkdate_bymonth", "-1m", "", ""],
                       ["1_TEST2.SQL", "enddate", "refer", "last_wkdate_bymonth", "1m", "", ""],
                       ],
                datatype=["str", "str", "str", "str", "str", "str","str"],
                row_count=6,
                col_count=(7, "fixed"),
            )
        with gr.Column():
            gr.Markdown("")
            gr.Markdown("")
            gr.Markdown("<h3>参数计算器：<h3>")
            gr.Markdown("方便大家验证自己的参数")
            with gr.Row():
                keyTxt = gr.Textbox(
                    show_label=True,
                    placeholder="输入跑批日期，yyyyMMdd格式，是自然日的上一天",
                    visible=True,
                    label="跑批日期"
                )
                btn = gr.Button(
                    "输入跑批日期后，点击我计算",
                    elem_id="cal_btn"
                )
            with gr.Row():
                base_date = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="base_date(基础日期)"
                )
                base_date_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按天偏移，输入偏移量(如-1d，为空默认为0d)"
                )
                base_date_type = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="输入偏移属性(自然日/工作日，默认为自然日)"
                )
                base_date_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期"
                )

            with gr.Row():
                first_wkdate_bymonth = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="first_wkdate_bymonth(当前月的第一个工作日)"
                )
                first_wkdate_bymonth_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按月偏移，输入偏移量(如-1m，为空默认为0m)"
                )
                first_wkdate_bymonth_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期"
                )

            with gr.Row():
                last_wkdate_bymonth = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="last_wkdate_bymonth(当前月的最后一个工作日)"
                )
                last_wkdate_bymonth_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按月偏移，输入偏移量(如-1m，为空默认为0m)"
                )
                last_wkdate_bymonth_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期"
                )

            with gr.Row():
                first_date_bymonth = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="first_date_bymonth(当前月的第一个自然日)"
                )
                first_date_bymonth_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按月偏移，输入偏移量(如-1m，为空默认为0m)"
                )
                first_date_bymonth_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期"
                )

            with gr.Row():
                last_date_bymonth = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="last_date_bymonth(当前月的最后一个自然日)"
                )
                last_date_bymonth_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按月偏移，输入偏移量(如-1m，为空默认为0m)"
                )
                last_date_bymonth_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期"
                )

            with gr.Row():
                first_wkdate_byweek = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="first_wkdate_byweek(当前周的第一个工作日)"
                )
                first_wkdate_byweek_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按周偏移，输入偏移量(如-1w，为空默认为0w)"
                )
                first_wkdate_byweek_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期(如本周无工作日，则返回base_date)"
                )

            with gr.Row():
                last_wkdate_byweek = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="last_wkdate_byweek(当前周的最后一个工作日)"
                )
                last_wkdate_byweek_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按周偏移，输入偏移量(如-1w，为空默认为0w)"
                )
                last_wkdate_byweek_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期(如本周无工作日，则返回base_date)"
                )

            with gr.Row():
                first_date_byweek = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="first_date_byweek(当前周的第一个自然日)"
                )
                first_date_byweek_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按周偏移，输入偏移量(如-1w，为空默认为0w)"
                )
                first_date_byweek_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期"
                )

            with gr.Row():
                last_date_byweek = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="last_date_byweek(当前周的最后一个自然日)"
                )
                last_date_byweek_diff = gr.Textbox(
                    show_label=True,
                    placeholder="请输入",
                    label="按周偏移，输入偏移量(如-1w，为空默认为0w)"
                )
                last_date_byweek_after = gr.Textbox(
                    show_label=True,
                    placeholder="自动生成",
                    label="偏移后日期"
                )

        # def interact_with_interface(inputs):
        #     df = read_data()
        #     for i,(col,v) in enumerate(inputs.items()):





        def getBaseDate(v, diff="0d", type="自然日"):
            if diff=="":
                diff ="0d"
            if type=="":
                type="自然日"
            sh = ec.get_calendar("XSHG")
            date = datetime.strptime(v, "%Y%m%d")
            diff = int(diff.replace("d", ""))
            if type == "自然日":
                date = date + dt.timedelta(days=diff)
            elif type == "工作日":
                if diff < 0:
                    cnt = 0
                    while cnt < -diff:
                        date = date - dt.timedelta(days=1)
                        if not sh.is_session(date):
                            continue
                        cnt += 1
                elif diff > 0:
                    cnt = 0
                    while cnt < diff:
                        date = date + dt.timedelta(days=1)
                        if not sh.is_session(date):
                            continue
                        cnt += 1
            return date.strftime("%Y%m%d")


        def getFirstWkdate_m(v, diff="0m"):
            if diff=="":
                diff ="0m"
            sh = ec.get_calendar("XSHG")
            # 获得一个自然日
            dateStr = getFirstDate_m(v,diff)
            date = datetime.strptime(dateStr, "%Y%m%d").strftime("%Y-%m-%d")
            if sh.is_session(date):
                return dateStr
            else:
                while True:
                    date = sh.date_to_session(date, direction="next")
                    if sh.is_session(date):
                        return date.strftime("%Y%m%d")


        def getLastWkdate_m(v,diff="0m"):
            if diff=="":
                diff ="0m"
            sh = ec.get_calendar("XSHG")
            dateStr = getLastDate_m(v,diff)
            date = datetime.strptime(dateStr, "%Y%m%d").strftime("%Y-%m-%d")
            if sh.is_session(date):
                return dateStr
            else:
                while True:
                    date = sh.date_to_session(date, direction="previous")
                    if sh.is_session(date):
                        return date.strftime("%Y%m%d")


        def getFirstDate_m(v, diff="0m"):
            if diff=="":
                diff ="0m"
            diff = int(diff.replace("m", ""))
            date = datetime.strptime(v, "%Y%m%d")
            month = (date.month + diff - 1) % 12 + 1
            year = date.year + (date.month + diff - 1) // 12
            firstDay = dt.date(year, month, 1)
            return firstDay.strftime("%Y%m%d")


        def getLastDate_m(v, diff="0m"):
            if diff=="":
                diff ="0m"
            diff = int(diff.replace("m", ""))
            date = datetime.strptime(v, "%Y%m%d")
            month = (date.month + diff - 1) % 12 + 1
            year = date.year + (date.month + diff - 1) // 12
            days_in_month = calendar.monthrange(year, month)[1]
            lastDay = dt.date(year, month, days_in_month)
            return lastDay.strftime("%Y%m%d")


        def getFirstDate_w(v,diff="0w"):
            if diff=="":
                diff ="0w"
            diff = int(diff.replace("w", ""))
            date = datetime.strptime(v, "%Y%m%d")
            daydiff = diff * 7
            date = date + dt.timedelta(days=daydiff)
            first_day_of_week = date - dt.timedelta(days=date.weekday())
            return first_day_of_week.strftime("%Y%m%d")


        def getLastDate_w(v,diff="0w"):
            if diff=="":
                diff ="0w"
            diff = int(diff.replace("w", ""))
            date = datetime.strptime(v, "%Y%m%d")
            daydiff = diff * 7
            date = date + dt.timedelta(days=daydiff)
            last_day_of_week = date + dt.timedelta(days=6 - date.weekday())
            return last_day_of_week.strftime("%Y%m%d")


        def getFirstWkdate_w(v,diff="0w"):
            if diff=="":
                diff ="0w"
            date = datetime.strptime(getFirstDate_w(v,diff),"%Y%m%d")
            saveDate = date
            sh = ec.get_calendar("XSHG")
            if sh.is_session(date):
                return date.strftime("%Y%m%d")
            else:
                while True:
                    date = sh.date_to_session(date, direction="next")
                    if sh.is_session(date):
                        return date.strftime("%Y%m%d")
                    if date.weekday()==7:
                        break
            return datetime.strptime(saveDate, "%Y%m%d")

        def getLastWkdate_w(v,diff="0w"):
            if diff=="":
                diff ="0w"
            date = datetime.strptime(getLastDate_w(v,diff),"%Y%m%d")
            saveDate = date
            sh = ec.get_calendar("XSHG")
            if sh.is_session(date):
                return date.strftime("%Y%m%d")
            else:
                while True:
                    date = sh.date_to_session(date, direction="previous")
                    if sh.is_session(date):
                        return date.strftime("%Y%m%d")
                    if date.weekday() == 1:
                        break
            return datetime.strptime(saveDate, "%Y%m%d")

        keyTxt.submit(fn=getBaseDate, inputs=keyTxt, outputs=base_date)
        keyTxt.submit(fn=getFirstWkdate_m, inputs=keyTxt, outputs=first_wkdate_bymonth)
        keyTxt.submit(fn=getLastWkdate_m, inputs=keyTxt, outputs=last_wkdate_bymonth)
        keyTxt.submit(fn=getFirstDate_m, inputs=keyTxt, outputs=first_date_bymonth)
        keyTxt.submit(fn=getLastDate_m, inputs=keyTxt, outputs=last_date_bymonth)
        keyTxt.submit(fn=getFirstWkdate_w, inputs=keyTxt, outputs=first_wkdate_byweek)
        keyTxt.submit(fn=getLastWkdate_w, inputs=keyTxt, outputs=last_wkdate_byweek)
        keyTxt.submit(fn=getFirstDate_w, inputs=keyTxt, outputs=first_date_byweek)
        keyTxt.submit(fn=getLastDate_w, inputs=keyTxt, outputs=last_date_byweek)

        keyTxt.submit(fn=getBaseDate, inputs=[keyTxt,base_date_diff,base_date_type], outputs=base_date_after)
        keyTxt.submit(fn=getFirstWkdate_m,inputs=[keyTxt,first_wkdate_bymonth_diff],outputs=first_wkdate_bymonth_after)
        keyTxt.submit(fn=getLastWkdate_m,inputs=[keyTxt,last_wkdate_bymonth_diff],outputs=last_wkdate_bymonth_after)
        keyTxt.submit(fn=getFirstDate_m,inputs=[keyTxt,first_date_bymonth_diff],outputs=first_date_bymonth_after)
        keyTxt.submit(fn=getLastDate_m,inputs=[keyTxt,last_date_bymonth_diff],outputs=last_date_bymonth_after)
        keyTxt.submit(fn=getFirstWkdate_w, inputs=[keyTxt,first_wkdate_byweek_diff] , outputs=first_wkdate_byweek_after)
        keyTxt.submit(fn=getLastWkdate_w, inputs=[keyTxt,last_wkdate_byweek_diff], outputs=last_wkdate_byweek_after)
        keyTxt.submit(fn=getFirstDate_w, inputs=[keyTxt,first_date_byweek_diff], outputs=first_date_byweek_after)
        keyTxt.submit(fn=getLastDate_w, inputs=[keyTxt,last_date_byweek_diff], outputs=last_date_byweek_after)


        btn.click(fn=getBaseDate, inputs=keyTxt, outputs=base_date)
        btn.click(fn=getFirstWkdate_m, inputs=keyTxt, outputs=first_wkdate_bymonth)
        btn.click(fn=getLastWkdate_m, inputs=keyTxt, outputs=last_wkdate_bymonth)
        btn.click(fn=getFirstDate_m, inputs=keyTxt, outputs=first_date_bymonth)
        btn.click(fn=getLastDate_m, inputs=keyTxt, outputs=last_date_bymonth)
        btn.click(fn=getFirstWkdate_w, inputs=keyTxt, outputs=first_wkdate_byweek)
        btn.click(fn=getLastWkdate_w, inputs=keyTxt, outputs=last_wkdate_byweek)
        btn.click(fn=getFirstDate_w, inputs=keyTxt, outputs=first_date_byweek)
        btn.click(fn=getLastDate_w, inputs=keyTxt, outputs=last_date_byweek)

        btn.click(fn=getBaseDate, inputs=[keyTxt,base_date_diff,base_date_type], outputs=base_date_after)
        btn.click(fn=getFirstWkdate_m,inputs=[keyTxt,first_wkdate_bymonth_diff],outputs=first_wkdate_bymonth_after)
        btn.click(fn=getLastWkdate_m,inputs=[keyTxt,last_wkdate_bymonth_diff],outputs=last_wkdate_bymonth_after)
        btn.click(fn=getFirstDate_m,inputs=[keyTxt,first_date_bymonth_diff],outputs=first_date_bymonth_after)
        btn.click(fn=getLastDate_m,inputs=[keyTxt,last_date_bymonth_diff],outputs=last_date_bymonth_after)
        btn.click(fn=getFirstWkdate_w, inputs=[keyTxt,first_wkdate_byweek_diff] , outputs=first_wkdate_byweek_after)
        btn.click(fn=getLastWkdate_w, inputs=[keyTxt,last_wkdate_byweek_diff], outputs=last_wkdate_byweek_after)
        btn.click(fn=getFirstDate_w, inputs=[keyTxt,first_date_byweek_diff], outputs=first_date_byweek_after)
        btn.click(fn=getLastDate_w, inputs=[keyTxt,last_date_byweek_diff], outputs=last_date_byweek_after)



        base_date_diff.submit(fn=getBaseDate, inputs=[keyTxt, base_date_diff, base_date_type], outputs=base_date_after)
        base_date_type.submit(fn=getBaseDate, inputs=[keyTxt, base_date_diff, base_date_type], outputs=base_date_after)
        first_wkdate_bymonth_diff.submit(fn=getFirstWkdate_m, inputs=[keyTxt, first_wkdate_bymonth_diff],
                      outputs=first_wkdate_bymonth_after)
        last_wkdate_bymonth_diff.submit(fn=getLastWkdate_m, inputs=[keyTxt, last_wkdate_bymonth_diff], outputs=last_wkdate_bymonth_after)
        first_date_bymonth_diff.submit(fn=getFirstDate_m, inputs=[keyTxt, first_date_bymonth_diff], outputs=first_date_bymonth_after)
        last_date_bymonth_diff.submit(fn=getLastDate_m, inputs=[keyTxt, last_date_bymonth_diff], outputs=last_date_bymonth_after)
        first_wkdate_byweek_diff.submit(fn=getFirstWkdate_w, inputs=[keyTxt, first_wkdate_byweek_diff], outputs=first_wkdate_byweek_after)
        last_wkdate_byweek_diff.submit(fn=getLastWkdate_w, inputs=[keyTxt, last_wkdate_byweek_diff], outputs=last_wkdate_byweek_after)
        first_date_byweek_diff.submit(fn=getFirstDate_w, inputs=[keyTxt, first_date_byweek_diff], outputs=first_date_byweek_after)
        last_date_byweek_diff.submit(fn=getLastDate_w, inputs=[keyTxt, last_date_byweek_diff], outputs=last_date_byweek_after)






    with gr.Blocks(css=customCSS, theme=small_and_beautiful_theme):
        history = gr.State([])
        token_count = gr.State([])
        promptTemplates = gr.State(load_template(get_template_names(plain=True)[0], mode=2))
        user_api_key = gr.State(my_api_key)
        user_question = gr.State("")
        outputing = gr.State(False)
        topic = gr.State("未命名对话历史记录")

        with gr.Row():
            gr.HTML(title)
            status_display = gr.Markdown(get_geoip(), elem_id="status_display")

        with gr.Row().style(equal_height=True):
            with gr.Column(scale=5):
                with gr.Row():
                    chatbot = gr.Chatbot(elem_id="chuanhu_chatbot").style(height="100%")
                with gr.Row():
                    with gr.Column(scale=12):
                        user_input = gr.Textbox(
                            show_label=False, placeholder="在这里输入"
                        ).style(container=False)
                    with gr.Column(min_width=70, scale=1):
                        submitBtn = gr.Button("发送", variant="primary")
                        cancelBtn = gr.Button("取消", variant="secondary", visible=False)
                with gr.Row():
                    emptyBtn = gr.Button(
                        "🧹 新的对话",
                    )
                    retryBtn = gr.Button("🔄 重新生成")
                    delFirstBtn = gr.Button("🗑️ 删除最旧对话")
                    delLastBtn = gr.Button("🗑️ 删除最新对话")
                    reduceTokenBtn = gr.Button("♻️ 总结对话")

            with gr.Column(visible=False):
                    with gr.Tab(label="Prompt"):
                        systemPromptTxt = gr.Textbox(
                            show_label=True,
                            placeholder='''
                            ''',
                            label="System prompt",
                            value=initial_prompt,
                            lines=10,
                        ).style(container=False)
                        with gr.Accordion(label="加载Prompt模板", open=True):
                            with gr.Column():
                                with gr.Row():
                                    with gr.Column(scale=6):
                                        templateFileSelectDropdown = gr.Dropdown(
                                            label="选择Prompt模板集合文件",
                                            choices=get_template_names(plain=True),
                                            multiselect=False,
                                            value=get_template_names(plain=True)[0],
                                        ).style(container=False)
                                    with gr.Column(scale=1):
                                        templateRefreshBtn = gr.Button("🔄 刷新")
                                with gr.Row():
                                    with gr.Column():
                                        templateSelectDropdown = gr.Dropdown(
                                            label="从Prompt模板中加载",
                                            choices=load_template(
                                                get_template_names(plain=True)[0], mode=1
                                            ),
                                            multiselect=False,
                                            value=load_template(
                                                get_template_names(plain=True)[0], mode=1
                                            )[0],
                                        ).style(container=False)



                    with gr.Tab(label="高级"):
                        gr.Markdown("# ⚠️ 务必谨慎更改 ⚠️\n\n如果无法使用请恢复默认设置")
                        default_btn = gr.Button("🔙 恢复默认设置")

                        with gr.Accordion("参数", open=False):
                            top_p = gr.Slider(
                                minimum=-0,
                                maximum=1.0,
                                value=1.0,
                                step=0.05,
                                interactive=True,
                                label="Top-p",
                            )
                            temperature = gr.Slider(
                                minimum=-0,
                                maximum=2.0,
                                value=1.0,
                                step=0.1,
                                interactive=True,
                                label="Temperature",
                            )

                        with gr.Accordion("网络设置", open=False):
                            apiurlTxt = gr.Textbox(
                                show_label=True,
                                placeholder=f"在这里输入API地址...",
                                label="API地址",
                                value="https://api.openai.com/v1/chat/completions",
                                lines=2,
                            )
                            changeAPIURLBtn = gr.Button("🔄 切换API地址")
                            proxyTxt = gr.Textbox(
                                show_label=True,
                                placeholder=f"在这里输入代理地址...",
                                label="代理地址（示例：http://127.0.0.1:10809）",
                                value="",
                                lines=2,
                            )
                            changeProxyBtn = gr.Button("🔄 设置代理地址")

        gr.Markdown(description)
        gr.HTML(footer.format(versions=versions_html()), elem_id="footer")
        chatgpt_predict_args = dict(
            fn=predict,
            inputs=[
                user_api_key,
                systemPromptTxt,
                history,
                user_question,
                chatbot,
                token_count,
                top_p,
                temperature
            ],
            outputs=[chatbot, history, status_display, token_count],
            show_progress=True,
        )

        start_outputing_args = dict(
            fn=start_outputing,
            inputs=[],
            outputs=[submitBtn, cancelBtn],
            show_progress=True,
        )

        end_outputing_args = dict(
            fn=end_outputing, inputs=[], outputs=[submitBtn, cancelBtn]
        )

        reset_textbox_args = dict(
            fn=reset_textbox, inputs=[], outputs=[user_input]
        )

        transfer_input_args = dict(
            fn=transfer_input, inputs=[user_input], outputs=[user_question, user_input, submitBtn, cancelBtn], show_progress=True
        )

        # Chatbot
        cancelBtn.click(cancel_outputing, [], [])

        user_input.submit(**transfer_input_args).then(**chatgpt_predict_args).then(**end_outputing_args)
        # user_input.submit(**get_usage_args)

        submitBtn.click(**transfer_input_args).then(**chatgpt_predict_args).then(**end_outputing_args)
        # submitBtn.click(**get_usage_args)

        emptyBtn.click(
            reset_state,
            outputs=[chatbot, history, token_count, status_display],
            show_progress=True,
        )
        emptyBtn.click(**reset_textbox_args)

        retryBtn.click(**start_outputing_args).then(
            retry,
            [
                user_api_key,
                systemPromptTxt,
                history,
                chatbot,
                token_count,
                top_p,
                temperature,
            ],
            [chatbot, history, status_display, token_count],
            show_progress=True,
        ).then(**end_outputing_args)
        # retryBtn.click(**get_usage_args)

        delFirstBtn.click(
            delete_first_conversation,
            [history, token_count],
            [history, token_count, status_display],
        )

        delLastBtn.click(
            delete_last_conversation,
            [chatbot, history, token_count],
            [chatbot, history, token_count, status_display],
            show_progress=True,
        )

        reduceTokenBtn.click(
            reduce_token_size,
            [
                user_api_key,
                systemPromptTxt,
                history,
                chatbot,
                token_count,
                top_p,
                temperature,
                gr.State(sum(token_count.value[-4:])),
            ],
            [chatbot, history, status_display, token_count],
            show_progress=True,
        )
        # reduceTokenBtn.click(**get_usage_args)

        # ChatGPT
        # keyTxt.change(submit_key, keyTxt, [user_api_key, status_display])
        # keyTxt.submit(**get_usage_args)

        # Template
        templateRefreshBtn.click(get_template_names, None, [templateFileSelectDropdown])
        templateFileSelectDropdown.change(
            load_template,
            [templateFileSelectDropdown],
            [promptTemplates, templateSelectDropdown],
            show_progress=True,
        )
        templateSelectDropdown.change(
            get_template_content,
            [promptTemplates, templateSelectDropdown, systemPromptTxt],
            [systemPromptTxt],
            show_progress=True,
        )


        # Advanced
        default_btn.click(
            reset_default, [], [apiurlTxt, proxyTxt, status_display], show_progress=True
        )
        changeAPIURLBtn.click(
            change_api_url,
            [apiurlTxt],
            [status_display],
            show_progress=True,
        )
        changeProxyBtn.click(
            change_proxy,
            [proxyTxt],
            [status_display],
            show_progress=True,
        )

    logging.info(
        colorama.Back.GREEN
        + "\n温馨提示：访问 http://localhost:80 查看界面"
        + colorama.Style.RESET_ALL
    )
    # 默认开启本地服务器，默认可以直接从IP访问，默认不创建公开分享链接
    demo.title = "ChatGPT 🚀"

if __name__ == "__main__":
    reload_javascript()
    # if running in Docker
    if dockerflag:
        if authflag:
            demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
                server_name="0.0.0.0",
                server_port=7860,
                auth=auth_list,
                favicon_path="./assets/favicon.ico",
            )
        else:
            demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
                server_name="0.0.0.0",
                server_port=7860,
                share=False,
                favicon_path="./assets/favicon.ico",
            )
    # if not running in Docker
    else:
        if authflag:
            demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
                share=False,
                auth=auth_list,
                favicon_path="./assets/favicon.ico",
                inbrowser=True,
            )
        else:
            # demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
            #     share=False, favicon_path="./assets/favicon.ico", inbrowser=True
            # )  # 改为 share=True 可以创建公开分享链接
            demo.queue(concurrency_count=CONCURRENT_COUNT).launch(server_name="0.0.0.0", server_port=80, share=False) # 可自定义端口
        # demo.queue(concurrency_count=CONCURRENT_COUNT).launch(server_name="0.0.0.0", server_port=7860,auth=("在这里填写用户名", "在这里填写密码")) # 可设置用户名与密码
        # demo.queue(concurrency_count=CONCURRENT_COUNT).launch(auth=("在这里填写用户名", "在这里填写密码")) # 适合Nginx反向代理
