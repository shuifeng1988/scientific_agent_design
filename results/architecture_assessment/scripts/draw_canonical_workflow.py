"""Render the canonical research workflow with Agent/Skill labels and validation loops."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures/scientific_research_workflow_v0.8.0.png"
PREVIEW=ROOT/"figures/scientific_research_workflow_v0.8.0_preview.png"
S=2; W,H=2400,3400
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
C={"ink":"#17283f","muted":"#60758d","line":"#c8d7e6","blue":"#2563a8",
   "teal":"#087f83","purple":"#7352a0","orange":"#b66c23","green":"#247953",
   "red":"#b54747","paper":"#f4f7fb","navy":"#172d47"}
im=Image.new("RGB",(W*S,H*S),C["paper"]); d=ImageDraw.Draw(im); fonts={}
def font(n,b=False):
    k=(n,b)
    if k not in fonts: fonts[k]=ImageFont.truetype(BOLD if b else FONT,n*S,index=2)
    return fonts[k]
def rect(x,y,w,h,fill="#fff",outline=None,r=18,width=1):
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
def arrow(points,color=C["blue"],width=3,dashed=False):
    line(points,color,width,dashed); (x1,y1),(x2,y2)=points[-2:]; a=math.atan2(y2-y1,x2-x1); z=12
    d.polygon([(x2*S,y2*S),((x2-z*math.cos(a-.48))*S,(y2-z*math.sin(a-.48))*S),
               ((x2-z*math.cos(a+.48))*S,(y2-z*math.sin(a+.48))*S)],fill=color)
def node(x,y,w,h,num,title,rows,color):
    rect(x+5,y+6,w,h,"#e4ebf3","#e4ebf3",18); rect(x,y,w,h,"#fff",C["line"],18)
    rect(x+18,y+18,56,38,color,color,10); txt(x+46,y+37,num,16,"#fff",True,"mm")
    txt(x+93,y+17,title,22,color,True)
    line([(x+18,y+73),(x+w-18,y+73)],C["line"],1)
    for i,row in enumerate(rows): txt(x+24,y+91+i*25,row,15,C["ink"])
def tag(x,y,label,color,w):
    rect(x,y,w,32,color,color,16); txt(x+w/2,y+16,label,13,"#fff",True,"mm")
def phase(y,num,title,subtitle,color):
    rect(280,y,1840,56,color,color,17); txt(305,y+14,num,16,"#fff",True); txt(365,y+11,title,23,"#fff",True); txt(1070,y+17,subtitle,15,"#edf4fb")
def diamond(cx,cy,w,h,fill,outline):
    pts=[(cx*S,(cy-h/2)*S),((cx+w/2)*S,cy*S),(cx*S,(cy+h/2)*S),((cx-w/2)*S,cy*S)]
    d.polygon(pts,fill=fill,outline=outline,width=3*S)
# Header
rect(55,40,11,112,C["teal"],C["teal"],4)
txt(91,38,"SCIENTIFIC RESEARCH AGENT FRAMEWORK",15,C["teal"],True)
txt(91,70,"科研项目主工作流 · Agent / Skill / 自验证 / 循环改进",41,C["ink"],True)
txt(93,128,"沿用原始 flowchart 结构，补充实际角色、能力路由、结果验收和反馈闭环",18,C["muted"])
tag(1960,60,"CANONICAL WORKFLOW",C["blue"],320)
line([(55,180),(2345,180)],C["line"],2)

# fixed contract
rect(55,205,2290,105,"#edf5fb","#cfe0ef",16)
txt(84,226,"固定指导",19,C["blue"],True)
txt(84,263,"五根文件 · 真实用户决定 · task_id / result_path · registry/tasks.tsv · 证据 receipts",16)
txt(1250,226,"贯穿自验证",19,C["teal"],True)
txt(1250,263,"schema / hash / scope / run_id / 输入输出 / scientific review / monitor",16)

# Main central spine
x,y,w,h=350,360,1700,110
phase(350,"A","理解、证据与设计","Supervisor → Researcher → 用户：先形成可检验方向，不直接执行",C["blue"])
node(x,y+85,w,h,"U","用户提出科研项目或问题",["目标、范围、预期结果、已有资源","输出：真实需求，不是自动批准"],C["blue"])
node(x,y+225,w,h,"A","分轮澄清、等待回答并确认方向",["Supervisor · scientific-intake","1–3 个高影响问题；用户回答进入会话","未回答 → needs_user；不制造默认决定"],C["blue"])
node(x,y+365,w,h,"B","初步 00_PROJECT.md 与 01_PLAN.md",["Supervisor + Researcher · scientific-intake/design","draft：初步目标、问题和计划","仍是草案；没有正式冻结或执行授权"],C["blue"])
node(x,y+505,w,h,"C","深度研究：进展、意义、可行性与方法",["Researcher · scientific-evidence","literature-review / parallel-cli provider / database sub-agent","保存主来源、反证、方法比较和访问限制"],C["purple"])
node(x,y+645,w,h,"D","用户讨论、修订与确认",["Researcher · scientific-design + 用户决定","比较方案、统计单位、资源与未决选择","重大未决 → 返回澄清；确认后进入审阅"],C["orange"])
node(x,y+785,w,h,"E","建立五个正式根文件并冻结研究设计",["Reviewer · scientific-review + 独立 invocation","approval + design review + freeze","生成 immutable baseline / design.json / task registry"],C["orange"])
for yy in [470,610,750,890,1030]: arrow([(1200,yy),(1200,yy+47)],C["blue"])
# self-validation rail for design
tag(70,690,"阶段自验证",C["teal"],150)
txt(240,699,"proposal / appraisal / review subject / approval hash；失败留在当前阶段",14,C["muted"])
arrow([(350,560),(235,560),(235,1000),(340,1000)],C["teal"],2,True)

phase(1210,"B","计划任务与确定性运行","01_PLAN → 任务注册 → Supervisor 调度 → 实际主机执行",C["teal"])
node(x,1295,w,h,"P","01_PLAN.md 的具体步骤",["scientific-design / project_contract","每步目的、输入、方法、统计、输出、QC","定义哪些证据才算完成"],C["teal"])
node(x,1435,w,h,"R","登记编号、唯一结果目录、依赖与资源",["Supervisor · registry + module_provider","task_id / result_path / depends_on / host","provider handoff 与输入 receipts"],C["teal"])
node(x,1575,w,h,"S","Supervisor 调度就绪任务",["Supervisor daemon · DAG / budget / expansion policy","资源、attempt、job_id、run_id","unknown 不重复提交；独立分支可继续"],C["teal"])
node(x,1715,w,h,"X","按实际主机配置执行",["Executor · scientific-execution","local / SSH / systemd driver","实际命令、软件、数据、环境、日志"],C["teal"])
node(x,1855,w,h,"V","核对结果与质量",["execution_policy / artifact QC / scientific self-check","run_id、输入输出哈希、qc.json、分母","技术 artifact 可放行；尚不等于科学完成"],C["green"])
for yy in [1350,1490,1630,1770]: arrow([(1200,yy),(1200,yy+47)],C["teal"])
# Technical failure side branch
node(70,1715,225,250,"F","技术失败",["Executor · scientific-recovery","保存成功证据","诊断 → 最小验证","只恢复失败阶段"],C["red"])
arrow([(350,1850),(295,1850)],C["red"],2)
arrow([(180,1715),(180,1640),(340,1640)],C["red"],2,True)
tag(70,1995,"技术恢复",C["red"],130)
txt(220,2004,"failed → repair proposal → minimal test → X",14,C["muted"])
# self-validation rail execution
tag(1635,1300,"每阶段自验证",C["teal"],150)
txt(1800,1308,"contract / input / run / output",13,C["teal"])
arrow([(1630,1345),(2120,1345),(2120,1935),(2055,1935)],C["teal"],2,True)

phase(2140,"C","成果包、解释与科学验收","技术成功后继续完成正式科研交付；结果不直接变成结论",C["green"])
node(x,2225,w,h,"O","results 中对应任务的成果包",["Reporter · scientific-reporting","唯一 task result_path：README / data / tables / figures","report manifest + 实际输入、软件与运行收据"],C["green"])
node(x,2365,w,h,"I","方法、结果、解释、图表与 Word 验收",["Researcher · scientific-interpretation + Reviewer · scientific-review","expected vs observed、统计、不确定性、反证、替代解释","同源 README / REPORT.docx / tables / figures"],C["green"])
node(x,2505,w,h,"H","事件记录与文档状态更新",["research_workflow + project_events + monitor","validate-package、qc.passed/failed、04_STATUS.md","独立审阅与必要 supplement 必须绑定版本"],C["green"])
for yy in [2280,2420]: arrow([(1200,yy),(1200,yy+47)],C["green"])
# self validation on results
tag(70,2350,"科学自验证",C["green"],145)
txt(235,2359,"claim ↔ evidence · denominator · figure lineage · review",14,C["muted"])
arrow([(350,2420),(235,2420),(235,2590),(340,2590)],C["green"],2,True)

# Decision
phase(2750,"D","下一步科学判断与循环改进","Supervisor 汇总真实状态；下一步不是自动默认继续",C["purple"])
diamond(1200,2940,520,210,"#fff","#7352a0")
txt(1200,2920,"下一步科学判断",20,C["purple"],True,"mm")
txt(1200,2955,"continue / supplement / needs_user / amend",14,C["muted"],False,"mm")
tag(1470,2880,"继续或登记补充证据任务",C["green"],250)
txt(1740,2888,"回到 R：新 task / supplement node",14,C["muted"])
arrow([(1460,2940),(1725,2940)],C["green"],2)
arrow([(1725,2940),(1725,1515),(2055,1515)],C["green"],2,True)
tag(1470,3020,"重大异常或设计变化",C["red"],200)
txt(1690,3028,"plan_amendment → D / E",14,C["muted"])
arrow([(1460,2980),(1700,2980),(1700,3070),(1200,3070),(1200,2945)],C["red"],2,True)
tag(610,3020,"needs_user",C["blue"],130)
txt(755,3028,"回到 A：补充真实决定后再继续",14,C["muted"])
arrow([(940,2940),(550,2940),(550,520),(340,520)],C["blue"],2,True)

# Footer governance
rect(55,3180,2290,150,C["navy"],C["navy"],18)
txt(85,3205,"循环改进的边界",21,"#fff",True)
txt(85,3245,"Agent 自验证：结构、哈希、范围、run_id、证据定位和报告完整性；失败时停留或回到最小必要阶段。",15,"#dce8f5")
txt(85,3275,"科学改进：由用户/Reviewer 决定继续、补证据、修订设计或接受限制；不由 Agent 自动改终点、分母或批准。",15,"#dce8f5")
txt(1700,3205,"平台边界",18,"#a8c9dc",True)
txt(1700,3245,"Skills / sub-agents 提供方法",15,"#fff")
txt(1700,3275,"Supervisor / runtime 保留状态与调度",15,"#fff")

im.save(OUT,optimize=True,dpi=(240,240))
im.resize((1600,2067),Image.Resampling.LANCZOS).save(PREVIEW,optimize=True)
print(OUT); print("PNG dimensions:",im.size)
