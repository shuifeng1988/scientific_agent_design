"""Render the current architecture as a typography-led high-resolution PNG."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parents[1]
S = 2
W, H = 2000, 1690
im = Image.new('RGB', (W*S, H*S), '#f3f6fb')
d = ImageDraw.Draw(im)
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
fonts = {}
C = dict(ink='#17283f', muted='#52657d', line='#dbe4ef', blue='#2563a8', teal='#087f83',
         purple='#7352a0', orange='#b66c23', green='#247953', slate='#526980')

def font(sz, bold=False):
    key = (sz, bold)
    if key not in fonts:
        fonts[key] = ImageFont.truetype(BOLD if bold else FONT, round(sz*S), index=2)
    return fonts[key]

def rr(box, fill, outline=None, r=16, width=1):
    d.rounded_rectangle(tuple(round(v*S) for v in box), round(r*S), fill=fill,
                        outline=outline, width=round(width*S))

def line(points, color, width=1.6):
    d.line([(round(x*S), round(y*S)) for x,y in points], fill=color, width=round(width*S), joint='curve')

def txt(x,y,t,sz=16,color=None,bold=False):
    d.text((round(x*S),round(y*S)), t, font=font(sz,bold), fill=color or C['ink'], anchor='lt')

def arrow(points, color=None, dashed=False, width=1.7):
    color=color or '#7e93ad'
    for p,q in zip(points,points[1:]):
        if dashed:
            dx,dy=q[0]-p[0],q[1]-p[1];dist=math.hypot(dx,dy)
            for n in range(0,math.ceil(dist),10):
                a=n/dist;b=min(n+5,dist)/dist
                line([(p[0]+dx*a,p[1]+dy*a),(p[0]+dx*b,p[1]+dy*b)],color,width)
        else:line([p,q],color,width)
    p,q=points[-2:];a=math.atan2(q[1]-p[1],q[0]-p[0]);size=7
    pts=[q,(q[0]-size*math.cos(a-.47),q[1]-size*math.sin(a-.47)),
           (q[0]-size*math.cos(a+.47),q[1]-size*math.sin(a+.47))]
    d.polygon([(round(x*S),round(y*S)) for x,y in pts],fill=color)

def panel(x,y,w,h,title,number,color):
    rr((x,y+3,x+w,y+h+3),'#e8edf5',r=19)
    rr((x,y,x+w,y+h),'#ffffff',C['line'],r=19)
    rr((x+21,y+21,x+60,y+53),color,r=9)
    txt(x+29,y+27,number,16,'#ffffff',True)
    txt(x+74,y+23,title,22,C['ink'],True)

def card(x,y,w,h,title,body,color=C['blue'],fill='#f6f9fd',fs=15,titlefs=19):
    rr((x,y,x+w,y+h),fill,'#e1e8f2',r=12)
    rr((x+15,y+18,x+19,y+h-18),color,r=2)
    txt(x+32,y+17,title,titlefs,color,True)
    for n,t in enumerate(body):txt(x+32,y+49+n*25,t,fs)

# Header: restrained scientific editorial style.
rr((55,44,64,150),C['teal'],r=4)
txt(82,41,'SCIENTIFIC RESEARCH AGENT FRAMEWORK',15,C['teal'],True)
txt(79,72,'模块化科研智能体 · 完整架构',44,C['ink'],True)
txt(82,135,'统一项目规范与证据链  /  按需组合 Agent 与 Skill  /  可替换专业研究方法',18,C['muted'])
rr((1680,61,1945,109),'#e5edf8',r=24)
txt(1708,74,'SOURCE v0.8.0',20,C['blue'],True)
txt(1682,125,'5 种角色 · 8 个阶段 Skill · 治理增强',17,C['muted'])
line([(55,184),(1945,184)],'#d7e1ee',1)

# Left: invariant project foundation.
x,w=55,420
panel(x,215,w,470,'五个根文件 · 共同指导','A',C['blue'])
docs=[('00_PROJECT.md','研究目的、科学问题、范围与假设'),
      ('01_PLAN.md','详细步骤、方法、依赖与完成标准'),
      ('02_SOFTWARE.md','软件、模型、版本、环境与验证'),
      ('03_DATA.md','数据来源、版本、路径、划分与校验'),
      ('04_STATUS.md','真实进度、失败、阻断与证据链接')]
for i,(name,desc) in enumerate(docs):
    yy=290+i*65
    rr((79,yy,451,yy+55),'#f3f7fc',r=9)
    txt(95,yy+7,name,19,C['blue'],True)
    txt(95,yy+32,desc,14,C['muted'])
txt(80,632,'00 / 01：批准后保护科学基线',14,C['muted'])
txt(80,653,'02 / 03 / 04：随真实证据与事件更新',14,C['muted'])

panel(x,707,w,335,'先理解目的，再推进研究','B',C['teal'])
steps=['澄清问题，分轮交流并等待回答','确认方向 → 建立初步 00 / 01',
       '真实深度调研 → 比较方法与可行性','讨论正式方案 → 用户确认 → 冻结',
       '按计划执行 → 质控 → 解释与报告']
for i,t in enumerate(steps):
    yy=786+i*43
    rr((81,yy-3,105,yy+21),'#e3f2f0',r=12)
    txt(89,yy+1,str(i+1),12,C['teal'],True)
    txt(116,yy,t,15)

txt(81,1012,'已有批准任务沿用授权，不重复接洽。',14,C['muted'])

panel(x,1064,w,397,'全过程保留的科研特点','C',C['purple'])
features=['任务与结果目录一一对应','完整方法、图表、结果、结论与解释',
          '真实来源、反证、不确定性与局限','完整比较范围，保留失败与排除分母',
          '失败证据 → 诊断 → 验证 → 断点恢复','科学异常只暂停受影响分支',
          '不静默修改冻结设计或重跑成功阶段','会话隔离、版本记录与持续监控']
for i,t in enumerate(features):
    yy=1140+i*35
    d.ellipse((83*S,(yy+5)*S,90*S,(yy+12)*S),fill=C['purple'])
    txt(102,yy,t,15)

# Main layered architecture.
x,w=515,1430
panel(x,215,w,173,'用户、平台与项目总入口','01',C['blue'])
card(539,277,300,86,'研究者 / 用户',['目标、澄清回答与真实决定'],fs=15)
card(870,277,435,86,'平台接入',['Codex / Claude / 其他宿主适配'],fs=15)
card(1336,277,585,86,'scientific-research-project',['协调阶段、保持全局目标、对接用户决定'],fs=15)
arrow([(844,320),(864,320)])
arrow([(1310,320),(1330,320)])

panel(x,410,w,292,'Agent 负责分工 · Skill 提供可复用能力','02',C['blue'])
roles=[('Supervisor','总协调',['scientific-intake'],['需求澄清与阶段交接']),
       ('Researcher','研究角色',['scientific-evidence','scientific-design','scientific-interpretation'],['证据、设计与结果解释']),
       ('Executor','执行角色',['scientific-execution','scientific-recovery'],['执行准备与技术修复']),
       ('Reviewer','审阅角色',['scientific-review'],['实质方法与证据审阅']),
       ('Reporter','报告角色',['scientific-reporting'],['整理完整科研成果'])]
for i,(en,cn,skills,desc) in enumerate(roles):
    xx=539+i*279
    rr((xx,479,xx+265,675),'#f4f7fc','#dfe7f2',r=12)
    txt(xx+17,493,en,20,C['blue'],True)
    txt(xx+17,522,cn,15,C['muted'])
    line([(xx+17,548),(xx+246,548)],'#d9e3ef',1)
    for j,s in enumerate(skills):txt(xx+17,560+j*23,s,12.5,C['ink'],True)
    txt(xx+17,648,desc[0],14,C['muted'])

panel(x,724,w,240,'可替换方法层 · 外部能力统一遵守项目契约','03',C['purple'])
card(539,793,293,113,'能力路由', ['modules.json：能力规范','providers.json：方法选择'],C['purple'], '#f7f4fb',fs=14)
rr((863,783,1186,841),'#f5f7fb','#e1e8f2',r=10)
txt(880,793,'内置方法',17,C['purple'],True)
txt(880,818,'现有 references / 自含流程',12,C['muted'])
rr((863,852,1186,919),'#f0eaf8','#d9cce9',r=10)
txt(880,862,'外部 Skill / sub-agent',17,C['purple'],True)
txt(880,889,'literature-review · 深入研究 · 领域方法',13,C['muted'])
card(1220,793,320,113,'宿主执行方法任务',['核实入口、版本、权限、工具','按当前问题与任务调用'],C['purple'],'#f7f4fb',fs=14)
card(1573,793,348,113,'标准产物与交接检查',['保留原始输出，适配既有格式','核对任务、版本、路径与哈希'],C['purple'],'#f7f4fb',fs=14)
arrow([(837,844),(848,844),(848,812),(857,812)],C['purple'])
arrow([(848,844),(848,885),(857,885)],C['purple'])
arrow([(1191,812),(1204,812),(1204,849),(1214,849)],C['purple'])
arrow([(1191,885),(1204,885),(1204,849)],C['purple'])
arrow([(1545,849),(1567,849)],C['purple'])
txt(541,932,'交接产物：调研 appraisal  /  执行或修复 proposal  /  科学反思 reflection  /  报告 report',14,C['muted'])

panel(x,986,w,218,'确定性执行内核 · 保留原有调度与恢复机制','04',C['teal'])
card(539,1054,324,111,'planning / repair worker',['当前内置 Codex CLI','提交契约与修复提案'],C['teal'],'#f1f8f7',fs=14)
card(892,1054,324,111,'常驻 Supervisor daemon',['依赖、资源、作业 ID 与预算','重启核对，未知状态不重复提交'],C['teal'],'#f1f8f7',fs=13)
card(1245,1054,324,111,'驱动与实际领域程序',['Linux local / SSH + systemd','本地限显式 lightweight 任务'],C['teal'],'#f1f8f7',fs=13)
card(1598,1054,323,111,'技术产物 QC',['核验输出、run ID、哈希与来源','合格产物放行独立下游计算'],C['teal'],'#f1f8f7',fs=13)
arrow([(868,1097),(886,1097)],C['teal'])
arrow([(886,1123),(868,1123)],C['teal'])
arrow([(1221,1110),(1239,1110)],C['teal'])
arrow([(1574,1110),(1592,1110)],C['teal'])
arrow([(1761,1168),(1761,1186),(1053,1186),(1053,1168)],C['teal'],dashed=True,width=1.4)

panel(x,1226,w,235,'科学成果验收 · 技术成功后继续完成科研交付','05',C['green'])
card(539,1295,324,125,'解释与独立审阅',['预期 vs 观察、支持与反证','独立 invocation 与缺陷清单','必要证据不足 → reviewing'],C['green'],'#f1f8f3',fs=13)
card(892,1295,324,125,'报告与包内容校验',['详细方法、结果与结论','表图来源及 Markdown / Word 一致','QC、反思和证据完整'],C['green'],'#f1f8f3',fs=12.5)
card(1245,1295,275,125,'治理与版本修订',['事件、审阅与补充节点','amendment 事务可回滚','旧基线与已完成结果保留'],C['green'],'#f1f8f3',fs=13)
card(1549,1295,372,125,'任务唯一成果包',['results / Q问题 / Q任务','README.md + REPORT.docx','tables / figures / _evidence'],C['green'],'#eaf5ee',fs=14)
arrow([(868,1357),(886,1357)],C['green'])
arrow([(1221,1357),(1239,1357)],C['green'])
arrow([(1525,1357),(1543,1357)],C['green'])
txt(541,1436,'技术产物可用与正式科学完成分别验收；报告故障不拖停无关的合格计算。',14,C['muted'])

# Vertical stage connectors stay inside the clear inter-panel gutters.
for yy in [388,702,964,1204]:arrow([(1230,yy+3),(1230,yy+17)],'#8b9eb5',width=1.7)
# Cross-cutting governance rail in the gutter.
line([(494,248),(494,1450)],'#9ab4d0',1.4)
for yy in [301,552,843,1095,1348]:
    arrow([(479,yy),(509,yy)],'#8aa7c7',dashed=True,width=1.2)

# Cross-cutting operational evidence footer.
rr((55,1490,1945,1623),'#172d47',r=18)
txt(81,1510,'持续反馈 · 全程可追溯',22,'#ffffff',True)
txt(81,1551,'任务注册表 / DAG / 持久状态',17,'#dce7f5')
txt(538,1551,'provenance / 事件 / 输入输出哈希',17,'#dce7f5')
txt(1090,1551,'04_STATUS.md / 后台监控快照',17,'#dce7f5')
txt(1580,1551,'结果与阻断 → Supervisor',17,'#dce7f5')
txt(81,1586,'区分服务存活与科研推进 · 完成需监控及产物验证一致 · 会话日志隔离 · 不因升级重跑已完成研究',15,'#afc4dd')

txt(58,1645,'实线：主要调用 / 产物交接     虚线：约束 / 反馈',14,C['muted'])
txt(780,1645,'平台边界：角色按需调用；外部 provider 需真实宿主核验。',14,C['muted'])
txt(1790,1645,'2026.09 · v0.8.0',14,C['muted'])

out=ROOT/'figures/scientific_architecture_v0.8.0.png'
im.save(out, optimize=True, dpi=(240,240))
preview=ROOT/'figures/scientific_architecture_v0.8.0_preview.png'
im.resize((1600,1352),Image.Resampling.LANCZOS).save(preview,optimize=True)
print(out)
print('PNG dimensions:',im.size)
