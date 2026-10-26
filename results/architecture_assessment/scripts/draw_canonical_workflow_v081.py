"""Render a readable v0.8.1 canonical workflow in a landscape flowchart layout."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/scientific_research_workflow_v0.8.1.png"
PREVIEW = ROOT / "figures/scientific_research_workflow_v0.8.1_preview.png"
S = 2
W, H = 2600, 1900
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
C = {"ink":"#17283f", "muted":"#61758a", "line":"#cbd9e7", "blue":"#2867a9",
     "teal":"#087f83", "purple":"#7653a3", "orange":"#b96e22", "green":"#287d55",
     "red":"#b54848", "paper":"#f4f7fb", "navy":"#172d47"}
im = Image.new("RGB", (W*S, H*S), C["paper"])
d = ImageDraw.Draw(im)
fonts = {}
def font(n, bold=False):
    key = (n, bold)
    if key not in fonts: fonts[key] = ImageFont.truetype(BOLD if bold else FONT, n*S, index=2)
    return fonts[key]
def rect(x, y, w, h, fill="#fff", outline=None, r=14, width=1):
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S), r*S, fill=fill, outline=outline or fill, width=max(1,width*S))
def txt(x, y, s, n=16, color=None, bold=False, anchor="lt"):
    d.text((x*S,y*S), s, font=font(n,bold), fill=color or C["ink"], anchor=anchor)
def line(points, color, width=2, dashed=False):
    for (x1,y1),(x2,y2) in zip(points, points[1:]):
        if not dashed:
            d.line((x1*S,y1*S,x2*S,y2*S), fill=color, width=width*S)
            continue
        dx,dy=x2-x1,y2-y1; dist=math.hypot(dx,dy) or 1
        for a in range(0,int(dist),18):
            b=min(a+9,dist); p=a/dist; q=b/dist
            d.line(((x1+dx*p)*S,(y1+dy*p)*S,(x1+dx*q)*S,(y1+dy*q)*S), fill=color, width=width*S)
def arrow(x1,y1,x2,y2,color,width=2):
    line([(x1,y1),(x2,y2)], color, width)
    a=math.atan2(y2-y1,x2-x1); z=12
    d.polygon([(x2*S,y2*S),((x2-z*math.cos(a-.5))*S,(y2-z*math.sin(a-.5))*S),((x2-z*math.cos(a+.5))*S,(y2-z*math.sin(a+.5))*S)], fill=color)
def pill(x,y,w,label,color):
    rect(x,y,w,32,color,color,16); txt(x+w/2,y+16,label,13,"#fff",True,"mm")
def card(x,y,w,h,num,title,role,detail,color):
    rect(x+5,y+6,w,h,"#e2eaf2","#e2eaf2",14); rect(x,y,w,h,"#fff",C["line"],14)
    rect(x+18,y+18,52,38,color,color,9); txt(x+44,y+37,num,14,"#fff",True,"mm")
    txt(x+88,y+16,title,25,color,True); txt(x+88,y+54,role,15,C["muted"])
    line([(x+18,y+82),(x+w-18,y+82)],C["line"],1)
    txt(x+22,y+105,detail,17,C["ink"])
def stage(y,label,color,caption):
    rect(55,y,2490,58,color,color,13); txt(82,y+29,label,24,"#fff",True,"lm"); txt(700,y+29,caption,15,"#e7f0f7","#e7f0f7" if False else False,"lm")

# Header and governing ribbon
rect(58,40,10,98,C["teal"],C["teal"],4)
txt(90,36,"SCIENTIFIC RESEARCH AGENT FRAMEWORK",15,C["teal"],True)
txt(90,70,"科研项目主工作流 · v0.8.1",42,C["ink"],True)
txt(92,124,"保留 v0.6.3 的阶段分带与横向箭头；Agent、Skill、证据和自验证在节点内明确标注",18,C["muted"])
pill(2190,58,280,"CANONICAL WORKFLOW",C["blue"])
line([(55,170),(2545,170)],C["line"],2)
rect(55,195,2490,78,"#edf5fb","#cfe0ef",14)
txt(85,216,"固定指导",17,C["blue"],True); txt(85,245,"五根文件 · 用户决定 · plan_step_id ↔ task_id ↔ result_path · 证据 receipts",15)
txt(1330,216,"全程自验证",17,C["teal"],True); txt(1330,245,"schema · hash · scope · run_id · QC · scientific review · monitor",15)

xs=[75,585,1095,1605,2115]; cw=430
stage(315,"A  理解、证据与设计",C["blue"],"Supervisor 先澄清；Researcher 做证据与方法比较；Reviewer 独立审阅")
row1=[("U","用户提出问题","用户 / 外层对话","目标、范围、已有资源"),("A","分轮澄清并确认方向","Supervisor · scientific-intake","等待回答；未决 → needs_user"),("B","初步 00_PROJECT / 01_PLAN","intake + design","草案与 intake receipt"),("C","深度研究与方法比较","scientific-evidence · literature-review","来源、反证、可行性、方法"),("D","讨论、修订与用户确认","scientific-design + 用户","统计单位、终点、资源")]
for x,(n,t,r,dt) in zip(xs,row1): card(x,395,cw,170,n,t,r,dt,C["blue"] if n in "UAB" else C["purple"])
for x in xs[:-1]: arrow(x+cw+8,472,x+cw+72,472,C["blue"])
stage(650,"B  设计冻结、计划与执行",C["teal"],"冻结后才启动正式任务；每个任务都有唯一目录、依赖和运行证据")
row2=[("E","独立审阅与设计冻结","Reviewer · scientific-review","approval receipt → 五根文件基线"),("P","01_PLAN.md 具体步骤","project_contract","输入、方法、输出、QC、停止标准"),("R","计划—任务—结果一一绑定","project_contract + registry","plan_step_id = task_id = result_path"),("S","Supervisor 调度就绪任务","daemon · DAG / budget","依赖、资源、attempt、job_id"),("X","按主机配置执行","Executor · scientific-execution","local / SSH / systemd · run_id")]
for x,(n,t,r,dt) in zip(xs,row2): card(x,730,cw,170,n,t,r,dt,C["teal"] if n in "PRSX" else C["orange"])
for x in xs[:-1]: arrow(x+cw+8,807,x+cw+72,807,C["teal"])
stage(985,"C  结果、质量与科学验收",C["green"],"技术成功不等于科学完成；结果必须进入对应任务成果包并接受解释与审阅")
row3=[("V","核对结果与技术质量","artifact QC · execution_policy","哈希、QC、分母、输入 lineage"),("O","建立对应任务成果包","Reporter · scientific-reporting","README · data · tables · figures"),("I","解释、图表、Word 与审阅","interpretation + Reviewer","预期/观察、反证、主张—证据"),("H","事件记录与状态更新","project_events + monitor","validate-package · 04_STATUS.md"),("N","证据评估与下一步判断","Supervisor + 用户 / Reviewer","支持、反对或不确定；证据不足 → 补证据")]
for x,(n,t,r,dt) in zip(xs,row3): card(x,1065,cw,170,n,t,r,dt,C["green"] if n != "N" else C["purple"])
for x in xs[:-1]: arrow(x+cw+8,1142,x+cw+72,1142,C["green"])

# Cross-stage transitions are shown in the gaps, not by ambiguous card-to-card diagonals.
pill(1215,585,170,"A → B",C["blue"]); pill(1215,920,170,"B → C",C["teal"])

# Branch and self-validation panels, with no text or lines over cards.
stage(1325,"D  分支状态与自验证",C["purple"],"异常停留在最小必要阶段；科学循环只能由明确判断触发")
panels=[(75,"needs_user","外层对话 / 用户决定","A → 等待回答 → 回到 A",C["blue"]),(585,"technical recovery","Executor · scientific-recovery","保存证据 → 最小验证 → 回到 X",C["red"]),(1095,"reviewing","Reviewer / required evidence","补齐证据 → 回到 I，不消耗技术重试",C["green"]),(1605,"每阶段自验证","schema · hash · scope · run_id · QC","结构 → 证据 → 运行 → 成果",C["teal"]),(2115,"证据与结论闭环","Reviewer + 用户决定","强证据支持/反对；不足 → 补证据",C["purple"])]
for x,title,role,detail,color in panels:
    rect(x,1405,cw,150,"#fff",C["line"],14); rect(x,1405,8,150,color,color,4); txt(x+28,1428,title,20,color,True); txt(x+28,1462,role,14,C["muted"]); txt(x+28,1505,detail,14,C["ink"])
for x in xs[:-1]: arrow(x+cw+8,1480,x+cw+72,1480,C["purple"])

# Explicit loops, kept below the panels.
pill(85,1600,190,"技术失败 → X",C["red"]); pill(350,1600,190,"审阅等待 → I",C["green"]); pill(615,1600,210,"证据不足 → 补证据",C["blue"])
txt(900,1607,"科学结论：逐条给出支持、反对或不确定的证据；证据不足时登记补充任务，不凭空生成新观点",16,C["ink"])

rect(55,1695,2490,125,C["navy"],C["navy"],16)
txt(85,1722,"阅读顺序",19,"#fff",True); txt(85,1762,"从上到下读三条主阶段，从左到右读每条阶段；底部只看分支、验证与循环，不把状态线穿过主流程。",15,"#dce8f5")
txt(1910,1722,"PNG + Mermaid",18,"#a8c9dc",True); txt(1910,1762,"详细契约与扩展模块见 MODULAR_ARCHITECTURE.md",15,"#fff")

im.save(OUT,optimize=True,dpi=(240,240)); im.resize((1600,1169),Image.Resampling.LANCZOS).save(PREVIEW,optimize=True)
print(OUT); print("PNG dimensions:", im.size)
