"""Render a clean canonical workflow: one spine, separated branches, no crossing labels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures/scientific_research_workflow_clean_v0.8.0.png"
PREVIEW=ROOT/"figures/scientific_research_workflow_clean_v0.8.0_preview.png"
S=2; W,H=2200,3100
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
C={"ink":"#17283f","muted":"#60758d","line":"#cbd9e7","blue":"#2563a8","teal":"#087f83",
   "purple":"#7352a0","orange":"#b66c23","green":"#247953","red":"#b54747","paper":"#f4f7fb","navy":"#172d47"}
im=Image.new("RGB",(W*S,H*S),C["paper"]); d=ImageDraw.Draw(im); fonts={}
def font(n,b=False):
    k=(n,b)
    if k not in fonts: fonts[k]=ImageFont.truetype(BOLD if b else FONT,n*S,index=2)
    return fonts[k]
def rect(x,y,w,h,fill="#fff",outline=None,r=16,width=1):
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),r*S,fill=fill,outline=outline or fill,width=max(1,width*S))
def txt(x,y,s,n=16,color=None,bold=False,anchor="lt"):
    d.text((x*S,y*S),s,font=font(n,bold),fill=color or C["ink"],anchor=anchor)
def line(points,color,width=2,dashed=False):
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        if not dashed: d.line((x1*S,y1*S,x2*S,y2*S),fill=color,width=width*S); continue
        dx,dy=x2-x1,y2-y1; dist=math.hypot(dx,dy) or 1
        for a in range(0,int(dist),16):
            b=min(a+8,dist); p=a/dist; q=b/dist
            d.line(((x1+dx*p)*S,(y1+dy*p)*S,(x1+dx*q)*S,(y1+dy*q)*S),fill=color,width=width*S)
def arrow(points,color=C["blue"],width=2,dashed=False):
    line(points,color,width,dashed); (x1,y1),(x2,y2)=points[-2:]; a=math.atan2(y2-y1,x2-x1); z=10
    d.polygon([(x2*S,y2*S),((x2-z*math.cos(a-.5))*S,(y2-z*math.sin(a-.5))*S),
               ((x2-z*math.cos(a+.5))*S,(y2-z*math.sin(a+.5))*S)],fill=color)
def label(x,y,s,color,w):
    rect(x,y,w,30,color,color,15); txt(x+w/2,y+15,s,13,"#fff",True,"mm")
def card(x,y,w,h,num,title,meta,body,color,fill="#fff",small=14):
    rect(x+4,y+5,w,h,"#e4ebf3","#e4ebf3",15); rect(x,y,w,h,fill,C["line"],15)
    rect(x+16,y+17,46,34,color,color,9); txt(x+39,y+34,num,14,"#fff",True,"mm")
    txt(x+78,y+14,title,20,color,True); txt(x+78,y+47,meta,13,C["muted"])
    line([(x+16,y+70),(x+w-16,y+70)],C["line"],1)
    for i,row in enumerate(body): txt(x+24,y+86+i*22,row,small,C["ink"])
def diamond(cx,cy,w,h,fill,outline):
    pts=[(cx*S,(cy-h/2)*S),((cx+w/2)*S,cy*S),(cx*S,(cy+h/2)*S),((cx-w/2)*S,cy*S)]
    d.polygon(pts,fill=fill,outline=outline,width=3*S)

# header
rect(55,38,10,103,C["teal"],C["teal"],4)
txt(86,34,"SCIENTIFIC RESEARCH AGENT FRAMEWORK",15,C["teal"],True)
txt(86,67,"科研项目主工作流（清晰版）",43,C["ink"],True)
txt(88,125,"主干流程、Agent/Skill、分支状态与自验证分别展示，避免线条穿过节点",18,C["muted"])
label(1840,55,"CANONICAL FLOW",C["blue"],280)
line([(55,175),(2145,175)],C["line"],2)

# contract bar
rect(55,200,2090,96,"#edf5fb","#cfe0ef",15)
txt(82,220,"固定指导",18,C["blue"],True)
txt(82,255,"五根文件 · 用户决定 · task_id / result_path · 证据 receipts",15)
txt(1080,220,"全程自验证",18,C["teal"],True)
txt(1080,255,"schema · hash · scope · run_id · QC · scientific review · monitor",15)

# spine
x,w=270,1250
ys=[340,485,630,775,920,1080,1235,1390,1545,1700,1855,2010,2165,2320]
data=[
("U","用户提出科研问题","用户 / 外层对话",["目标、范围、已有资源","没有自动批准"]),
("A","分轮澄清并确认方向","Supervisor · scientific-intake",["1–3 个高影响问题","等待回答；未决 → needs_user"]),
("B","初步 00_PROJECT.md / 01_PLAN.md","Supervisor + Researcher · intake/design",["draft 与 intake receipt","仍是草案，不启动正式计算"]),
("C","深度研究与方法比较","Researcher · scientific-evidence",["literature-review / parallel-cli","主来源、反证、可行性、访问限制"]),
("D","讨论、修订与用户确认","Researcher · scientific-design",["统计单位、终点、资源、替代方案","重大选择回到用户"]),
("E","独立审阅与设计冻结","Reviewer · scientific-review",["独立 invocation + approval","freeze → 五根文件基线 / design.json"]),
("P","01_PLAN.md 具体步骤","Researcher · project_contract",["目的、输入、方法、输出、QC、停止标准","每项回答一个问题"]),
("R","登记任务、目录、依赖与资源","Supervisor · registry / module_provider",["task_id + 唯一 result_path","provider handoff + input receipts"]),
("S","Supervisor 调度就绪任务","Supervisor daemon · DAG / budget",["依赖、资源、attempt、job_id","unknown 不重复提交"]),
("X","按实际主机配置执行","Executor · scientific-execution",["local / SSH / systemd","实际命令、软件、数据、run_id"]),
("V","核对结果与技术质量","execution_policy + artifact QC",["输出哈希、QC、分母、输入 lineage","技术成功 ≠ 科学完成"]),
("O","建立对应任务成果包","Reporter · scientific-reporting",["README / data / tables / figures","manifest + 结果目录一一对应"]),
("I","解释、图表、Word 与科学审阅","Researcher · interpretation + Reviewer",["预期 vs 观察、统计、反证、主张—证据","required supplement 需纳入"]),
("H","事件记录与文档状态更新","research_workflow + project_events",["validate-package、QC、04_STATUS.md","事件、监控、结果索引"])]
colors=[C["blue"],C["blue"],C["blue"],C["purple"],C["orange"],C["orange"],C["teal"],C["teal"],C["teal"],C["teal"],C["green"],C["green"],C["green"],C["green"]]
heights=[115,115,115,115,115,115,115,115,115,115,115,115,115,115]
for y,(item,color) in zip(ys,zip(data,colors)):
    num,title,meta,body=item; card(x,y,w,heights[ys.index(y)],num,title,meta,body,color)
for a,b in zip(ys,ys[1:]):
    arrow([(x+w/2,a+115),(x+w/2,b-8)],C["blue"],2)

# stage labels left, not on the spine
label(60,338,"01 理解 / 设计",C["blue"],175)
label(60,1233,"02 计划 / 执行",C["teal"],175)
label(60,2008,"03 成果 / 验收",C["green"],175)

# side status rail
sx=1570
rect(sx,340,510,465,"#fff","#d8e3ee",18)
txt(sx+24,365,"分支与恢复",21,C["red"],True)
txt(sx+24,401,"主干不被异常线条打断；状态在侧栏处理",14,C["muted"])
card(sx+20,435,470,102,"NU","needs_user","外层对话 / 用户决定",["不代填答案；决定后回到 A"],C["blue"],"#f7faff",12)
card(sx+20,560,470,102,"FR","technical recovery","Executor · scientific-recovery",["保存成功证据；最小验证；回到 X"],C["red"],"#fff8f8",12)
card(sx+20,685,470,102,"RV","reviewing","Reviewer / required evidence",["不消耗技术重试；补齐后回到 I"],C["green"],"#f5fbf7",12)
arrow([(x+w,525),(1545,525)],C["blue"],2,True)
arrow([(x+w,1755),(1545,610)],C["red"],2,True)
arrow([(x+w,2220),(1545,735)],C["green"],2,True)

# self validation rail
rect(sx,850,510,380,"#f0f8f7","#c9e0dd",18)
txt(sx+24,875,"每阶段自验证",21,C["teal"],True)
txt(sx+24,912,"失败停留在当前阶段或回到最小必要阶段",14,C["muted"])
checks=[("01","结构","schema、路径、task identity"),("02","证据","输入 receipts、来源、反证"),("03","运行","scope、run_id、QC、哈希"),("04","成果","图表 lineage、审阅、supplements")]
for i,(n,t,b) in enumerate(checks):
    yy=950+i*63; rect(sx+24,yy,50,34,C["teal"],C["teal"],9); txt(sx+49,yy+17,n,13,"#fff",True,"mm")
    txt(sx+91,yy+3,t,16,C["teal"],True); txt(sx+91,yy+27,b,13,C["ink"])
# Validation signals use the outer gutter only; no dashed line crosses a main card.
line([(x+w,1040),(1540,1040),(1540,1040),(sx,1040)],C["teal"],2,True)
line([(x+w,1390),(1540,1390),(1540,1070),(sx,1070)],C["teal"],2,True)
line([(x+w,2010),(1540,2010),(1540,1130),(sx,1130)],C["teal"],2,True)
line([(x+w,2320),(1540,2320),(1540,1190),(sx,1190)],C["teal"],2,True)

# final decision panel
rect(270,2490,1250,390,"#fff","#d8d2e8",18)
txt(300,2520,"下一步科学判断",23,C["purple"],True)
txt(300,2560,"Supervisor 汇总真实状态，科学方向由用户 / Reviewer 决定",15,C["muted"])
diamond(880,2700,450,150,"#f8f4fc",C["purple"])
txt(880,2683,"继续 / 补充 / 用户决定 / 修订",18,C["purple"],True,"mm")
txt(880,2715,"不是自动默认继续",14,C["muted"],False,"mm")
label(305,2800,"继续 / supplement",C["green"],185); txt(510,2808,"登记新 task 或 supplement node → 回到 R",14,C["ink"])
label(875,2800,"needs_user",C["blue"],120); txt(1015,2808,"回到 A",14,C["ink"])
label(305,2842,"重大设计变化",C["red"],175); txt(500,2850,"plan_amendment → 新审阅 / 新版本 → 回到 D/E",14,C["ink"])

# arrows into decision and loops
arrow([(x+w/2,2435),(x+w/2,2490)],C["green"],2)
arrow([(x+w/2,2775),(x+w/2,2855),(1550,2855),(1550,1400),(x+w,1400)],C["green"],2,True)
arrow([(700,2700),(180,2700),(180,540),(260,540)],C["blue"],2,True)
arrow([(1050,2775),(1050,2885),(840,2885),(840,930),(x,930)],C["red"],2,True)

# footer
rect(55,2940,2090,115,C["navy"],C["navy"],18)
txt(82,2964,"清晰性原则",20,"#fff",True)
txt(82,3003,"主干只表达科研推进；侧栏表达用户等待、技术恢复、科学审阅等待；自验证单独成栏；循环改进只从科学判断产生。",15,"#dce8f5")
txt(1680,2964,"PNG + Mermaid",18,"#a8c9dc",True)
txt(1680,3003,"适合 GitHub 文档渲染",15,"#fff")

im.save(OUT,optimize=True,dpi=(240,240))
im.resize((1600,2247),Image.Resampling.LANCZOS).save(PREVIEW,optimize=True)
print(OUT); print("PNG dimensions:",im.size)
