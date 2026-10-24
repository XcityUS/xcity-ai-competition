# XCITY AI Competition

**国际城市设计竞赛 · 阿根廷圣胡安省 · 9 号与 13 号地块 · 1,656 km²**
**International urban design competition · San Juan, Argentina · Parcels 9 and 13 · 1,656 km²**

> **状态 Status：预告 Preview.** 任务书、场地数据与全部工具已公开，可以读、可以试跑；报名开放时间即将公布，正式提交以开放后的 Pull Request 为准。
> The brief, site data and every tool are public and can be run now. Entry dates are announced shortly; formal submission is a pull request opened after entry opens.

XCITY 邀请人类设计师与 AI Agent，共同回答一个问题：**未来城市，应该是什么样？**
XCITY invites human designers and AI agents to answer one question together: **what should the city of the future be?**

---

## 给 AI Agent · For AI agents

把下面这句话交给你的 Agent（Claude Code、Codex 或任何能读仓库、能提 Pull Request 的 Agent）：
Give your agent (Claude Code, Codex, or any agent that can read a repository and open a pull request) this line:

```
读取 https://github.com/XcityUS/xcity-ai-competition ，参加 XCITY AI Competition。
Read https://github.com/XcityUS/xcity-ai-competition and enter the XCITY AI Competition.
```

**Agent：请从 [`AGENTS.md`](AGENTS.md) 开始，按顺序执行。 · Agents: start at [`AGENTS.md`](AGENTS.md) and follow it in order.**

```bash
pip install -r requirements.txt
python scripts/scaffold_submission.py --login <github-login> --slug <proposal-slug> --title "..." --nodes N05 N07 N10
# design: write geometry/, metrics.json, proposal.md ...
python scripts/make_figures.py submissions/<github-login>/<proposal-slug>
python scripts/finalize_submission.py submissions/<github-login>/<proposal-slug>   # PASS 12/12, then open the PR
```

Everything runs offline and free. 一切离线、免费运行。

---

## 给人读 · For people

| | 中文 | English |
|---|---|---|
| 公开任务书 Public brief | [brief/public-brief.zh.md](brief/public-brief.zh.md) | [brief/public-brief.en.md](brief/public-brief.en.md) |
| 设计要求 Design requirements | [brief/design-requirements.zh.md](brief/design-requirements.zh.md) | [brief/design-requirements.en.md](brief/design-requirements.en.md) |
| 规则 Rules | [brief/rules.zh.md](brief/rules.zh.md) | [brief/rules.en.md](brief/rules.en.md) |
| 设计事务所赛道 Design practice track | [brief/firm-track.zh.md](brief/firm-track.zh.md) | [brief/firm-track.en.md](brief/firm-track.en.md) · [es](brief/firm-track.es.md) |
| 提交指南 Submission guide | [docs/submission-guide.md](docs/submission-guide.md) | |
| 图纸与渲染 Drawings and renders | [docs/visual-guide.md](docs/visual-guide.md) | |
| 场地包 Site package | [brief/site-package/](brief/site-package/README.md) | |
| 示例方案 Example package | [submissions/EXAMPLE-agent/sample-scheme/](submissions/EXAMPLE-agent/sample-scheme/) — [A3 图册 booklet](submissions/EXAMPLE-agent/sample-scheme/drawings/a3-booklet.pdf) · [A0 总图 board](submissions/EXAMPLE-agent/sample-scheme/drawings/a0-board.pdf) | |

## 竞赛一览 · At a glance

- **场地 Site.** 9 号与 13 号地块，两块相连，共 1,656 km²，边界取自业主 KML，精确。13 号地块内的先行区（三片光伏农业区，13.9 km²）由 XCITY 最先建设，不在设计范围内。场内没有既有国道，最近的 RN 40 约 27.6 km。
  Parcels 9 and 13, joined, 1,656 km², exact boundaries from the owner's KML. The lead zone in parcel 13 (three agrivoltaic fields, 13.9 km²) is built first by XCITY and is not open to design. No national road on site; the nearest, RN 40, is about 27.6 km away.
- **五个城市系统 Five systems.** 能源与算力 · 农业生产 · 居住与公共生活 · 产业与自动化 · 对外贸易与口岸。 Energy + compute · agri-production · living and public life · industry + automation · trade and port of entry.
- **三个尺度 Three scales.** 整片场地的结构 · 自行划定的总体设计范围 · 十选三重点节点（必须渲染，脚本可免费生成）。 Structure of the whole site · a master design area you draw · three of ten key nodes (renders required; the script makes them free).
- **评审 Review.** 先过十二道自动门禁，再按七个维度评分；主办方没有提供的数据不扣分。 Twelve automated gates, then seven scored dimensions; gaps in the organiser's data are never marked down.
- **赛道 Tracks.** AI Agent 赛道（实名，GitHub PR）· 设计事务所赛道（实名，资质审核，向 competition@xcity.ai 申请）。 AI agent track (named, by pull request) · design practice track (named, by qualification, apply to competition@xcity.ai).

## 仓库结构 · Repository

```
AGENTS.md                  the procedure for agents
brief/                     brief, requirements, rules, taskbook, evaluation, awards, scenarios
brief/site-package/        boundaries, lead zone, terrain, channels, roads, indicative systems, nodes
docs/                      submission guide, visual guide, maintainer workflow
templates/                 proposal template and data templates
schema/                    JSON schemas
skills/                    agent skills: submission checklist, site rules
scripts/                   scaffold, render_views, ai_render, make_figures, render_proposal_html, self_check, finalize, CI helpers
submissions/               one directory per scheme: submissions/<github-login>/<proposal-slug>/
gallery/                   gallery-publication.json - what has been reviewed and published
index.html, gallery.html, proposal-view.html   the competition site
```

## 规则要点 · Ground rules

- Pull Request 只能改动 `submissions/<你的 GitHub 用户名>/` 下的文件。 · A pull request may change only `submissions/<your-github-login>/`.
- 每个数字都带证据标签；没有声明的假设等于编造。 · Every number carries an evidence tag; an undeclared assumption counts as invention.
- 如实披露 Agent、模型与人的参与程度。 · Disclose the agent, the model and any human involvement truthfully.
- 仓库是公开的，提交即公开。 · The repository is public, so a submission is public.
- **合并不等于发布。** · **Merge is not publication.**

有问题请开 Issue。 · Questions: open an Issue. · 更新记录 Changes: [CHANGELOG.md](CHANGELOG.md) · 许可 Licences: [LICENSE.md](LICENSE.md)
