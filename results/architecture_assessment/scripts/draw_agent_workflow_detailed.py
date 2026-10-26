"""Render a detailed executable scientific-agent workflow as a PNG."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/scientific_agents_workflow_detailed_v0.8.0.png"
PREVIEW = ROOT / "figures/scientific_agents_workflow_detailed_v0.8.0_preview.png"
S=2; W,H=2400,3400
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
C={"ink":"#17283f","muted":"#5f7188","line":"#d6e1ed","blue":"#2563a8",
   "teal":"#087f83","purple":"#7352a0","orange":"#b66c23","green":"#247953",
   "red":"#b54747","paper":"#f4f7fb","navy":"#172d47"}
im=Image.new("RGB",(W*S,H*S),C["paper"]); d=ImageDraw.Draw(im); fonts={}
def font(n,b=False):
    k=(n,b)
    if k not in fonts: fonts[k]=ImageFont.truetype(BOLD if b else FONT,n*S,index=2)
    return fonts[k]
def rect(x,y,w,h,fill="#fff",outline=None,r=14,width=1):
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),r*S,fill=fill,outline=outline or fill,width=max(1,width*S))
def txt(x,y,s,n=16,color=None,bold=False):
    d.text((x*S,y*S),s,font=font(n,bold),fill=color or C["ink"])
def line(points,color=None,width=2,dashed=False):
    color=color or C["line"]
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        if not dashed: d.line((x1*S,y1*S,x2*S,y2*S),fill=color,width=width*S); continue
        dx,dy=x2-x1,y2-y1; dist=math.hypot(dx,dy) or 1
        for a in range(0,int(dist),14):
            b=min(a+7,dist); p=a/dist; q=b/dist
            d.line(((x1+dx*p)*S,(y1+dy*p)*S,(x1+dx*q)*S,(y1+dy*q)*S),fill=color,width=width*S)
def arrow(points,color=None,width=2,dashed=False):
    color=color or C["blue"]; line(points,color,width,dashed)
    (x1,y1),(x2,y2)=points[-2:]; a=math.atan2(y2-y1,x2-x1); z=10
    d.polygon([(x2*S,y2*S),((x2-z*math.cos(a-.5))*S,(y2-z*math.sin(a-.5))*S),
               ((x2-z*math.cos(a+.5))*S,(y2-z*math.sin(a+.5))*S)],fill=color)
def pill(x,y,label,color,w):
    rect(x,y,w,30,color,color,15); txt(x+w/2-6,y+7,label,13,"#fff",True)
def card(x,y,w,h,title,rows,color,fill="#fff",small=14):
    rect(x+4,y+5,w,h,"#e6edf5","#e6edf5",14); rect(x,y,w,h,fill,C["line"],14)
    rect(x+14,y+16,6,h-32,color,color,3)
    txt(x+34,y+14,title,18,color,True)
    for i,row in enumerate(rows): txt(x+34,y+48+i*22,row,small,C["ink"])
def phase(y,num,title,subtitle,color):
    rect(55,y,2290,55,color,color,14); txt(78,y+14,num,16,"#fff",True); txt(130,y+11,title,23,"#fff",True); txt(780,y+17,subtitle,15,"#e8f0f8")

# Header
rect(55,40,11,112,C["teal"],C["teal"],4)
txt(91,36,"SCIENTIFIC RESEARCH AGENT FRAMEWORK",15,C["teal"],True)
txt(91,69,"科研智能体可执行工作流（详细版）",43,C["ink"],True)
txt(93,128,"依据真实项目契约、脚本入口、任务状态和结果验收绘制；不是 GitHub CI 流程图",18,C["muted"])
pill(1975,58,"v0.8.0 · DETAILED",C["blue"],295)
line([(55,178),(2345,178)],C["line"],2)

# Contract and lanes
rect(55,205,2290,115,"#edf5fb","#cfe0ef",15)
txt(84,227,"固定输入",19,C["blue"],True)
txt(84,263,"用户目标 · 五根文件 · 已批准方向 · task_id / result_path · registry/tasks.tsv",16)
txt(1110,227,"贯穿每个阶段",19,C["blue"],True)
txt(1110,263,"证据收据 · 输入/输出哈希 · 实际状态 · 用户决定 · 会话日志 · 监控快照",16)
lanes=[("用户 / Supervisor",55,C["blue"]),("Researcher / Provider",635,C["purple"]),
       ("Executor / Daemon",1215,C["teal"]),("Reviewer / Reporter",1795,C["green"])]
for label,x,col in lanes:
    rect(x,340,550,42,"#eaf0f7","#d7e2ee",9); txt(x+18,351,label,16,col,True)

# Phase 1
phase(410,"01","理解、澄清与建立研究边界","Supervisor 先读上下文；高影响问题必须真实等待用户回答",C["blue"])
card(70,490,340,170,"接收方向",["读取 00/01（若已有）","读取会话日志隔离规则","判断：新方向 / 已批准任务"],C["blue"],"#fff",14)
card(435,490,340,170,"intake 对话",["提出 1–3 个关键问题","给出选择 + 自由输入","不把默认项当作同意"],C["blue"],"#fff",14)
card(800,490,340,170,"用户决定点",["方向、范围、目的","资源与预期结果","未决定 → needs_user"],C["blue"],"#fff",14)
card(1240,490,340,170,"阶段交接",["intake brief","未决事项与影响","不启动正式计算"],C["blue"],"#fff",14)
card(1605,490,340,170,"draft",["research_workflow.py draft","建立初步 00 / 01","写入 intake receipt"],C["blue"],"#fff",14)
card(1970,490,340,170,"进入 evidence",["目标问题已确认","任务边界可审查","开始证据获取"],C["blue"],"#fff",14)
for a,b in [(410,435),(775,800),(1140,1240),(1580,1605),(1945,1970)]: arrow([(a,575),(b,575)],C["blue"])
arrow([(970,660),(970,700),(600,700),(600,720)],C["blue"],2,True)
pill(72,680,"等待用户",C["blue"],130); txt(220,688,"答案进入当前会话，不由 Agent 代填",14,C["muted"])

# Phase 2
phase(760,"02","证据获取、综合与正式设计","Researcher 调用内置或外部方法；所有结果仍回到项目契约",C["purple"])
card(70,840,340,180,"provider resolve",["modules.json → capability","literature-review / 其他 provider","检查 host、版本、入口、工具"],C["purple"],"#fff",13)
card(435,840,340,180,"prepare handoff",["输入 receipts","objective / task_id","timeout / output limit","输出目录与保护路径"],C["purple"],"#fff",13)
card(800,840,340,180,"外部文献方法",["parallel-cli search / extract","保留原始检索与提取","记录工具和访问限制"],C["purple"],"#fff",13)
card(1165,840,340,180,"normalize + check",["appraisal.json","两条检索路线","主来源、反证、方法比较"],C["purple"],"#fff",13)
card(1530,840,340,180,"deep synthesis",["closest work","contrary evidence","feasibility / information gain"],C["purple"],"#fff",13)
card(1895,840,415,180,"design proposal",["五个正式文档草案","任务卡、依赖、统计与 QC","proposal + appraisal receipts"],C["purple"],"#fff",13)
for a,b in [(410,435),(775,800),(1140,1165),(1505,1530),(1870,1895)]: arrow([(a,930),(b,930)],C["purple"])
txt(72,1045,"外部 provider 只能替换证据获取/综合方法，不能建立第二套根文件、总计划、结果目录或批准路径。",14,C["muted"])

# Design gate
phase(1080,"03","设计审阅、用户批准与冻结","方案是可修改草案；冻结后 00/01 成为版本化科学基线",C["orange"])
card(70,1160,430,175,"设计审阅",["scientific_review.py subject","问题/方法、反证、分析单位","控制、统计、可行性、任务覆盖"],C["orange"],"#fff",13)
card(535,1160,430,175,"独立 Reviewer",["独立 invocation/context","逐项 adequate / revise / needs_user","重大缺陷必须解决"],C["green"],"#fff",13)
card(1000,1160,430,175,"真实用户批准",["approval receipt","绑定 proposal/appraisal hash","批准不由 Agent 制造"],C["blue"],"#fff",13)
card(1465,1160,430,175,"freeze",["research_workflow.py freeze","五根文件 baseline","registry/tasks + design.json"],C["orange"],"#fff",13)
card(1930,1160,380,175,"任务启动条件",["workflow_policy","review_policy","task/result 一一对应","可进入执行层"],C["orange"],"#fff",13)
for a,b in [(500,535),(965,1000),(1430,1465),(1895,1930)]: arrow([(a,1245),(b,1245)],C["orange"])
arrow([(750,1335),(750,1375),(580,1375),(580,1410)],C["red"],2,True)
pill(74,1370,"revise / needs_user",C["red"],195); txt(284,1378,"回到设计或用户决定，不进入冻结",14,C["muted"])

# Execution
phase(1450,"04","执行准备、DAG 调度与技术恢复","Executor 准备契约；daemon 才拥有持久状态、资源和作业提交权",C["teal"])
card(70,1530,350,200,"contract preparation",["task card + inputs","software/data/version","gates + resource limits","预算与 host"],C["teal"],"#fff",13)
card(445,1530,350,200,"planning / repair worker",["Codex execution/recovery","proposal.json","最小验证与修复证据","不改科学范围"],C["teal"],"#fff",13)
card(820,1530,350,200,"Supervisor daemon",["依赖可用性","资源/预算/attempt","提交与幂等重启","unknown 不重复提交"],C["teal"],"#fff",13)
card(1195,1530,350,200,"driver / job",["local / SSH systemd","submitting → running","job_id + run_id","实际程序产生输出"],C["teal"],"#fff",13)
card(1570,1530,350,200,"artifact QC",["qc.json","输出哈希与 run_id","artifact 可放行下游","科学完成仍未达成"],C["teal"],"#fff",13)
card(1945,1530,365,200,"技术故障分支",["failed → diagnosis","repairable → minimal test","unknown → reconcile first","预算不重置"],C["red"],"#fff",13)
for a,b in [(420,445),(795,820),(1170,1195),(1545,1570),(1920,1945)]: arrow([(a,1630),(b,1630)],C["teal"])
arrow([(2110,1730),(2110,1770),(970,1770),(970,1800)],C["red"],2,True)
pill(74,1765,"技术恢复",C["red"],125); txt(212,1773,"只回到必要阶段；成功产物保留",14,C["muted"])

# Result interpretation
phase(1840,"05","解释、科学审阅与必要补充","技术成功后，结果还要经过 run-bound reflection、审阅和补证据门槛",C["green"])
card(70,1920,350,195,"result package",["results/Qxx/Qxx.xx","README.md / data / tables","figures / _evidence","manifest + actual inputs"],C["green"],"#fff",13)
card(445,1920,350,195,"reflection",["expected vs observed","uncertainty / alternatives","literature search + sources","continue / supplement / needs_user"],C["green"],"#fff",13)
card(820,1920,350,195,"result subject",["绑定 plan_version","task_id + run_id","report artifacts + inputs","author invocation"],C["green"],"#fff",13)
card(1195,1920,350,195,"independent review",["methods / denominators","statistics / claim support","contrary explanations","figures / downstream impact"],C["green"],"#fff",13)
card(1570,1920,350,195,"supplement gate",["required：必须完成并纳入 reflection","optional：登记后可独立推进","防止自依赖死锁","新范围 → amendment"],C["orange"],"#fff",12.5)
card(1945,1920,365,195,"decision",["adequate + no major open","→ qc.passed / release","revise → reviewing","needs_user → 用户决定"],C["green"],"#fff",13)
for a,b in [(420,445),(795,820),(1170,1195),(1545,1570),(1920,1945)]: arrow([(a,2015),(b,2015)],C["green"])
arrow([(1010,2115),(1010,2160),(650,2160),(650,2195)],C["red"],2,True)
pill(74,2155,"reviewing",C["green"],125); txt(212,2163,"不消耗技术重试；补审阅/证据后重查",14,C["muted"])

# Reporting / amendment / final
phase(2230,"06","报告、事件、发布与下一轮","Reporter 整理可读成果；事件层更新状态，依赖分支按真实完成释放",C["orange"])
card(70,2310,410,190,"reporter",["同源 Markdown + Word","详细方法、表图、结果、结论","限制、支持与不支持的主张","REPORT.docx"],C["orange"],"#fff",13)
card(510,2310,410,190,"validate package",["report_content","render / source tables","input + figure lineage","scientific_review + supplements"],C["orange"],"#fff",13)
card(950,2310,410,190,"project events",["run.completed","qc.passed / failed","review.pending","plan.amendment.approved"],C["orange"],"#fff",13)
card(1390,2310,410,190,"managed documents",["04_STATUS.md","results/README.md","registry / provenance","monitor snapshot"],C["orange"],"#fff",13)
card(1830,2310,480,190,"next branch",["依赖任务获得释放","继续 / supplement / amendment","保存历史版本和已完成结果","新计划需要新审阅"],C["orange"],"#fff",13)
for a,b in [(480,510),(920,950),(1360,1390),(1800,1830)]: arrow([(a,2405),(b,2405)],C["orange"])
arrow([(2070,2500),(2070,2560),(250,2560),(250,2525)],C["blue"],2,True)
pill(74,2545,"反馈回 Supervisor",C["blue"],175); txt(270,2553,"状态、阻断、用户决定和下一任务",14,C["muted"])

# Amendment lane
phase(2620,"07","科学范围变化：受控方案修订","不把补充分析、安装更新或重启服务当作隐式科学迁移",C["red"])
card(70,2700,430,175,"触发条件",["新终点 / cohort / 假设","重要方法或范围改变","现有 frozen baseline 不适用"],C["red"],"#fff",13)
card(535,2700,430,175,"prepare amendment",["新 proposal/appraisal","base_design_sha256","affected_task_ids","new_dependencies"],C["red"],"#fff",13)
card(1010,2700,430,175,"review + approval",["独立 design review","真实用户 approval","暂停 daemon","清理运行中/未知状态"],C["red"],"#fff",13)
card(1485,2700,430,175,"plan_amendment",["archive old baseline","atomic transaction","失败可 recover","完成任务不重写"],C["red"],"#fff",13)
card(1960,2700,350,175,"new version",["新 design.json","新 task/result mapping","历史报告仍可验收","再进入执行"],C["red"],"#fff",13)
for a,b in [(500,535),(965,1010),(1440,1485),(1915,1960)]: arrow([(a,2785),(b,2785)],C["red"])
arrow([(2200,2875),(2200,2930),(950,2930),(950,2960)],C["red"],2,True)
pill(75,2925,"archive + recover",C["red"],170); txt(265,2933,"旧基线、旧结果和事件保持可追溯",14,C["muted"])

# Footer
rect(55,3040,2290,210,C["navy"],C["navy"],18)
txt(88,3070,"运行真相由什么组成？",22,"#fff",True)
txt(88,3116,"Agent：问题理解、证据综合、方法设计、解释与报告组织",16,"#dbe7f4")
txt(88,3148,"确定性程序：任务注册、DAG、资源/预算、作业 ID、哈希、事件、结果验收",16,"#dbe7f4")
txt(88,3180,"用户：方向、范围、关键假设、重大修订和科学未决问题的真实决定",16,"#dbe7f4")
txt(1390,3070,"不是 CI 流程",18,"#a8c9dc",True)
txt(1390,3116,"没有 .github/workflows 文件；此图依据项目实际脚本与契约",15,"#fff")
txt(1390,3148,"新项目先 intake → evidence → design → freeze",15,"#fff")
txt(1390,3180,"运行后以结果包、审阅、事件和监控共同判断完成",15,"#fff")
txt(58,3330,"实线：正常交接    虚线：等待 / 恢复 / 反馈    颜色：Supervisor / Researcher / Executor / Reviewer-Reporter / 风险分支",14,C["muted"])

im.save(OUT,optimize=True,dpi=(240,240))
im.resize((1600,2267),Image.Resampling.LANCZOS).save(PREVIEW,optimize=True)
print(OUT); print("PNG dimensions:",im.size)

