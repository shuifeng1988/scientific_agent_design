"""Render the runtime collaboration of research agents as a PNG."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/scientific_agents_runtime_workflow_v0.8.0.png"
PREVIEW = ROOT / "figures/scientific_agents_runtime_workflow_v0.8.0_preview.png"
S = 2
W, H = 2200, 1500
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
C = {"ink":"#17283f","muted":"#62748a","line":"#d7e2ee","blue":"#2563a8",
     "teal":"#087f83","purple":"#7352a0","orange":"#b66c23","green":"#247953",
     "paper":"#f4f7fb"}
im = Image.new("RGB", (W*S,H*S), C["paper"])
d = ImageDraw.Draw(im)
fonts = {}
def font(n,b=False):
    k=(n,b)
    if k not in fonts: fonts[k]=ImageFont.truetype(BOLD if b else FONT,n*S,index=2)
    return fonts[k]
def rect(x,y,w,h,fill="#fff",outline=None,r=16,width=1):
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),r*S,fill=fill,outline=outline or fill,width=max(1,width*S))
def txt(x,y,s,n=16,color=None,bold=False,anchor="lt"):
    d.text((x*S,y*S),s,font=font(n,bold),fill=color or C["ink"],anchor=anchor)
def line(points,color=None,width=2,dashed=False):
    color=color or C["line"]
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        if not dashed:
            d.line((x1*S,y1*S,x2*S,y2*S),fill=color,width=width*S); continue
        dx,dy=x2-x1,y2-y1; dist=math.hypot(dx,dy) or 1
        for a in range(0,int(dist),14):
            b=min(a+7,dist); p=a/dist; q=b/dist
            d.line(((x1+dx*p)*S,(y1+dy*p)*S,(x1+dx*q)*S,(y1+dy*q)*S),fill=color,width=width*S)
def arrow(points,color=None,width=2,dashed=False):
    color=color or C["blue"]; line(points,color,width,dashed)
    (x1,y1),(x2,y2)=points[-2:]; ang=math.atan2(y2-y1,x2-x1); z=10
    d.polygon([(x2*S,y2*S),((x2-z*math.cos(ang-.5))*S,(y2-z*math.sin(ang-.5))*S),
               ((x2-z*math.cos(ang+.5))*S,(y2-z*math.sin(ang+.5))*S)],fill=color)
def pill(x,y,label,color,w):
    rect(x,y,w,31,color,color,16); txt(x+w/2,y+16,label,13,"#fff",True,"mm")
def agent(x,y,w,number,role,subtitle,rows,color):
    rect(x+4,y+5,w,250,"#e5ebf3","#e5ebf3",16); rect(x,y,w,250,"#fff",C["line"],16)
    rect(x+18,y+18,44,38,color,color,10); txt(x+40,y+37,number,16,"#fff",True,"mm")
    txt(x+76,y+20,role,22,color,True); txt(x+76,y+51,subtitle,14,C["muted"])
    line([(x+18,y+78),(x+w-18,y+78)],C["line"],1)
    for i,row in enumerate(rows):
        d.ellipse(((x+22)*S,(y+99+i*28)*S,(x+29)*S,(y+106+i*28)*S),fill=color)
        txt(x+40,y+94+i*28,row,15)

# Header
rect(56,42,10,105,C["teal"],C["teal"],4)
txt(88,38,"SCIENTIFIC RESEARCH AGENT FRAMEWORK",15,C["teal"],True)
txt(88,70,"科研智能体运行工作流",44,C["ink"],True)
txt(90,129,"一次已批准任务如何从问题澄清走到可审计成果，并在技术与科学异常处正确停留",18,C["muted"])
pill(1814,60,"RUNTIME VIEW",C["blue"],270); txt(1817,107,"v0.8.0 · Agent collaboration",15,C["muted"])
line([(56,180),(2144,180)],C["line"],2)

# Shared contract
rect(56,215,2088,108,"#edf5fb","#cfe0ef",16)
txt(84,236,"共享项目契约",20,C["blue"],True)
txt(84,275,"00_PROJECT.md · 01_PLAN.md · 02_SOFTWARE.md · 03_DATA.md · 04_STATUS.md",17)
txt(1000,236,"每个 Agent 都必须遵守",16,C["blue"],True)
txt(1000,275,"任务 ID / 结果路径 · 证据收据 · 用户决定 · 版本与哈希 · 真实状态",16)

# Main timeline
txt(72,366,"主流程",20,C["ink"],True); txt(72,397,"实线 = 交接；虚线 = 约束、等待或反馈",14,C["muted"])
x0,gap,w=72,28,384
xs=[x0+i*(w+gap) for i in range(5)]
data=[
("01","Supervisor","协调与方向确认",["读取五根文件与任务卡","澄清问题，等待真实回答","生成阶段交接与用户问题"],C["blue"]),
("02","Researcher","证据与方法设计",["调用 evidence / design Skill","保存检索、反证和方法比较","形成 appraisal / proposal"],C["purple"]),
("03","Executor","授权任务执行",["读取批准的 task contract","提交运行，记录 run ID 与资源","失败时只做有界技术修复"],C["teal"]),
("04","Reviewer","科学验收与解释",["检查分母、统计、图表和主张","区分支持、反证和替代解释","返回 adequate / revise / needs_user"],C["green"]),
("05","Reporter","完整成果交付",["生成同源 README / Word","链接 tables / figures / evidence","写入事件并更新结果索引"],C["orange"])]
for x,(n,r,sub,rows,col) in zip(xs,data): agent(x,434,w,n,r,sub,rows,col)
for i in range(4): arrow([(xs[i]+w+5,553),(xs[i+1]-8,553)],C["blue"])

txt(72,720,"阶段交接产物",18,C["ink"],True)
arts=[("方向简报","真实未决问题\n不制造批准",C["blue"]),("appraisal.json\nproposal.json","来源、反证、方法\n计划与任务映射",C["purple"]),("run / QC / artifact","代码、环境、输入\n哈希和运行状态",C["teal"]),("reflection.json\nscientific_review","预期 vs 观察\n证据定位与缺陷",C["green"]),("REPORT.docx\nREADME.md","方法、表图、结果\n结论和限制",C["orange"])]
for x,(title,body,col) in zip(xs,arts):
    rect(x,756,w,84,"#fff",C["line"],12); rect(x+14,772,5,51,col,col,2)
    title_rows = title.split("\n")
    title_size = 15 if len(title_rows) > 1 else 17
    for j, title_row in enumerate(title_rows): txt(x+34,770+j*18,title_row,title_size,col,True)
    body_y = 797 if len(title_rows) == 1 else 813
    for j,row in enumerate(body.split("\n")): txt(x+34,body_y+j*15,row,12,C["muted"])

# Branches
txt(72,895,"必须停留或分支的位置",20,C["ink"],True)
branches=[
(72,936,630,"用户决定等待","方向、范围、关键假设或高影响修订尚未由用户确认。","needs_user",C["blue"]),
(738,936,630,"技术恢复分支","远端失败或报告故障：保留成功产物，诊断后从断点恢复，不改变科学范围。","repairable",C["teal"]),
(1404,936,740,"科学审阅等待","缺少独立审阅、必要补充证据或存在重大未解决缺陷；不消耗技术重试预算。","reviewing",C["green"])]
for x,y,bw,title,body,state,col in branches:
    rect(x,y,bw,172,"#fff",C["line"],15); rect(x+18,y+18,150,31,col,col,15); txt(x+93,y+34,state,13,"#fff",True,"mm")
    txt(x+18,y+67,title,19,col,True); txt(x+18,y+103,body,14,C["ink"])
    txt(x+18,y+136,"返回条件：实际决定 / 最小验证通过 / 新审阅或证据完成",13,C["muted"])

# Feedback footer
rect(72,1165,2072,194,"#172d47","#172d47",18)
txt(102,1190,"Supervisor + 事件层：持续反馈与状态真相",22,"#fff",True)
txt(102,1238,"project_events 记录",15,"#b9cbe0",True)
txt(102,1270,"run.started · qc.passed / failed · review.pending · plan.amendment.approved",15,"#fff")
txt(792,1238,"持久状态核对",15,"#b9cbe0",True)
txt(792,1270,"DAG 依赖 · 资源预算 · 作业 ID · 输入/输出哈希 · 监控快照",15,"#fff")
txt(1480,1238,"反馈回到",15,"#b9cbe0",True)
txt(1480,1270,"用户决定 / Researcher 解释 / Executor 修复 / 下一计划版本",15,"#fff")
arrow([(1170,1130),(1170,1156)],"#91c2cf",2,True)
arrow([(1820,1360),(1820,1401),(267,1401),(267,1360)],"#91c2cf",2,True)
txt(72,1418,"图中不代表每次任务都启动全部五个 Agent；阶段按任务需要调用，确定性程序保留调度、哈希、预算和事件写入权。",14,C["muted"])
txt(1810,1418,"2026.09 · v0.8.0",14,C["muted"])

im.save(OUT,optimize=True,dpi=(240,240))
im.resize((1600,1090),Image.Resampling.LANCZOS).save(PREVIEW,optimize=True)
print(OUT); print("PNG dimensions:",im.size)
