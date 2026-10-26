"""Render the English counterpart of the readable v0.8.1 canonical workflow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/scientific_research_workflow_v0.8.1_en.png"
PREVIEW = ROOT / "figures/scientific_research_workflow_v0.8.1_en_preview.png"
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
    title_size = 18 if len(title) > 29 else (21 if len(title) > 22 else 24)
    txt(x+88,y+18,title,title_size,color,True); txt(x+88,y+56,role,14,C["muted"])
    line([(x+18,y+82),(x+w-18,y+82)],C["line"],1)
    txt(x+22,y+105,detail,17,C["ink"])
def stage(y,label,color,caption):
    rect(55,y,2490,58,color,color,13); txt(82,y+29,label,24,"#fff",True,"lm"); txt(700,y+29,caption,15,"#e7f0f7","#e7f0f7" if False else False,"lm")

# Header and governing ribbon
rect(58,40,10,98,C["teal"],C["teal"],4)
txt(90,36,"SCIENTIFIC RESEARCH AGENT FRAMEWORK",15,C["teal"],True)
txt(90,70,"Scientific Research Workflow · v0.8.1",42,C["ink"],True)
txt(92,124,"v0.6.3-style phase bands and horizontal arrows; agents, skills, evidence and self-checks are explicit",18,C["muted"])
pill(2190,58,280,"CANONICAL WORKFLOW",C["blue"])
line([(55,170),(2545,170)],C["line"],2)
rect(55,195,2490,78,"#edf5fb","#cfe0ef",14)
txt(85,216,"Fixed guidance",17,C["blue"],True); txt(85,245,"five root files · user decisions · plan_step_id ↔ task_id ↔ result_path · evidence receipts",15)
txt(1330,216,"Self-validation throughout",17,C["teal"],True); txt(1330,245,"schema · hash · scope · run_id · QC · scientific review · monitor",15)

xs=[75,585,1095,1605,2115]; cw=430
stage(315,"A  Understand, evidence and design",C["blue"],"Supervisor clarifies; Researcher compares evidence and methods; Reviewer audits independently")
row1=[("U","User submits research question","User / outer dialogue","goals, scope, available resources"),("A","Clarify and confirm direction","Supervisor · scientific-intake","wait for answer; unresolved → needs_user"),("B","Draft 00_PROJECT / 01_PLAN","intake + design","draft plus intake receipt"),("C","Deep research and method comparison","scientific-evidence · literature-review","sources, counterevidence, feasibility, methods"),("D","Discuss, revise and confirm","scientific-design + user","statistical unit, endpoint, resources")]
for x,(n,t,r,dt) in zip(xs,row1): card(x,395,cw,170,n,t,r,dt,C["blue"] if n in "UAB" else C["purple"])
for x in xs[:-1]: arrow(x+cw+8,472,x+cw+72,472,C["blue"])
stage(650,"B  Design freeze, planning and execution",C["teal"],"Formal work starts only after freeze; every task has a unique path, dependencies and run evidence")
row2=[("E","Independent review and freeze","Reviewer · scientific-review","approval receipt → five-root baseline"),("P","Concrete 01_PLAN.md steps","project_contract","inputs, method, outputs, QC, stop criteria"),("R","Bind plan, task and result one-to-one","project_contract + registry","plan_step_id = task_id = result_path"),("S","Supervisor schedules ready work","daemon · DAG / budget","dependencies, resources, attempt, job_id"),("X","Execute on actual host","Executor · scientific-execution","local / SSH / systemd · run_id")]
for x,(n,t,r,dt) in zip(xs,row2): card(x,730,cw,170,n,t,r,dt,C["teal"] if n in "PRSX" else C["orange"])
for x in xs[:-1]: arrow(x+cw+8,807,x+cw+72,807,C["teal"])
stage(985,"C  Results, quality and scientific acceptance",C["green"],"Technical success is not scientific completion; results require packaging, interpretation and review")
row3=[("V","Check results and technical quality","artifact QC · execution_policy","hashes, QC, denominators, input lineage"),("O","Build task-matched result package","Reporter · scientific-reporting","README · data · tables · figures"),("I","Interpretation, figures, Word and review","interpretation + Reviewer","expected/observed, alternatives, claim–evidence"),("H","Record events and update status","project_events + monitor","validate-package · 04_STATUS.md"),("N","Evaluate evidence and choose next step","Supervisor + user / Reviewer","support, contradict or unresolved; insufficient → evidence task")]
for x,(n,t,r,dt) in zip(xs,row3): card(x,1065,cw,170,n,t,r,dt,C["green"] if n != "N" else C["purple"])
for x in xs[:-1]: arrow(x+cw+8,1142,x+cw+72,1142,C["green"])

# Cross-stage transitions are shown in the gaps, not by ambiguous card-to-card diagonals.
pill(1215,585,170,"A → B",C["blue"]); pill(1215,920,170,"B → C",C["teal"])

# Branch and self-validation panels, with no text or lines over cards.
stage(1325,"D  Branch states and self-validation",C["purple"],"Exceptions stop at the minimum necessary stage; scientific loops require an explicit judgment")
panels=[(75,"needs_user","Outer dialogue / user decision","A → wait for answer → A",C["blue"]),(585,"technical recovery","Executor · scientific-recovery","save evidence → minimum check → X",C["red"]),(1095,"reviewing","Reviewer / required evidence","add evidence → I; no technical retry",C["green"]),(1605,"Self-check each stage","schema · hash · scope · run_id · QC","structure → evidence → run → result",C["teal"]),(2115,"Evidence–conclusion loop","Reviewer + user decision","strong support/contradiction; insufficient → evidence task",C["purple"])]
for x,title,role,detail,color in panels:
    rect(x,1405,cw,150,"#fff",C["line"],14); rect(x,1405,8,150,color,color,4); txt(x+28,1428,title,20,color,True); txt(x+28,1462,role,14,C["muted"]); txt(x+28,1505,detail,14,C["ink"])
for x in xs[:-1]: arrow(x+cw+8,1480,x+cw+72,1480,C["purple"])

# Explicit loops, kept below the panels.
pill(85,1600,190,"technical failure → X",C["red"]); pill(350,1600,190,"review wait → I",C["green"]); pill(615,1600,210,"insufficient evidence → add task",C["blue"])
txt(900,1607,"Scientific conclusion: every claim gets supporting, contrary or unresolved evidence; insufficient evidence creates a bounded evidence task, not a new unsupported idea",16,C["ink"])

rect(55,1695,2490,125,C["navy"],C["navy"],16)
txt(85,1722,"How to read",19,"#fff",True); txt(85,1762,"Read the three main stages top to bottom and each stage left to right; the bottom row contains states, checks and loops.",15,"#dce8f5")
txt(1910,1722,"PNG + Mermaid",18,"#a8c9dc",True); txt(1910,1762,"Detailed contracts and extensions: MODULAR_ARCHITECTURE.md",15,"#fff")

im.save(OUT,optimize=True,dpi=(240,240)); im.resize((1600,1169),Image.Resampling.LANCZOS).save(PREVIEW,optimize=True)
print(OUT); print("PNG dimensions:", im.size)
