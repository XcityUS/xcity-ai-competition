# XCITY 规则一致性核对 2026年10月26日

本次是主办方已授权的说明、工具与提交流程修订，不是外部审批。机构与 Agent 两赛道共用场地事实，各自保留独立任务、提交方式和评审。当前规则以本记录和下列权威定义为准；CHANGELOG 较早条目是历史，不是同时生效的流程。

## 保留 修改 删除 新增 待确认

| 处理 | 本次结果 |
|---|---|
| 保留 | 固定全域边界与两类既定试点；M1–M12；十四章关联；三组各一节点及原有必交视图；机构十页构想、五家付费入围和既定日期；两份旧投稿原文件与指纹 |
| 修改 | 对外三个尺度、内部四层深度；全域与首期、放大区、首批工程分开；正式设计图留主册；新版按 master_area 裁切建筑量及密度；机构注册后获专属网页链接上传提交 |
| 删除 | 最低1500字作为完成门槛；自动建立定时任务的指示；官网重复订阅区；公开成果对照按钮；用“自行划定总体设计范围”描述首期；邮件回复申请附件 |
| 新增 | 中英文 Agent 任务书对照；矩阵v2实际判断/范围/阶段/缺口类型；防版本降级；独立场外context研究层；用地分区遗漏/重叠检查；元数据schema与跨文件一致性检查；首页两赛道订阅勾选 |
| 待真实资料或工程师接入 | 实测水文、地籍确认、水权、电网及场外通行权等资料仍未获得；邮件服务需工程师配置，当前由授权工作人员发送私链。不虚称自动发信或资料已核实 |

## 要求 权威定义 模板 schema 检查 证据

| 要求 | 权威定义 | 模板及字段 | schema / 检查脚本 | 成果证据与限制 |
|---|---|---|---|---|
| 固定全场地与三尺度四任务 | brief/design-depth.json / requirements.json.design_depth；site-conditions | proposal第7/9/10章，matrix decision、scope | design_depth_matrix.schema；design_depth.py | 全域结构、完整首期、放大区、三个节点；自动引用一致不等于充分 |
| 三类各选一节点 | site-package/nodes/design_nodes.json | manifest.nodes、nodes.geojson | node_selection.py；G9 | 每节点鸟瞰/人视和解释设计的平剖面；旧名单例外独立于矩阵迁移 |
| 农光场/生活区分别保护 | requirements.fixed_pilot_context | geometry land_use/system；来源与说明 | xcity_common.pilot_land_use_conflicts；G9 | 两者都不允许新增建筑；生活区不得概括为农光用途 |
| 洪泛筛选与真实限制 | site-conditions；water README；evidence-index | assumptions、sources、matrix.gaps | G9提示；内容审阅 | DEM筛选不等于湖泊/实测洪水线/法定退界；不能反推安全 |
| 范围/指标核算 | design-requirements中Metric scope；matrix v2 | master_area、land_use、buildings、metrics | spatial_checks.py；compute_metrics.py；G4 | v2建筑量按master裁切，区外另报；实际首期与远期情景另列 |
| 场外接入研究 | site-conditions；context.schema.json | 可选context/*.geojson status/authority/basis | spatial_checks.context_errors；G9 | 可超出边界，仅研究，不计场内用地/建成指标或取得权利 |
| 正式设计主册和技术附件 | presentation-requirements；presentation-guide | presentation模板；booklet.section_pages | presentation.py；G10/G12 | 主册保留正式分析/平剖面/体量/运行图，附件放原始重复控制与完整计算 |
| 数据性质、版本和局限 | site-package/evidence-index、sources、datapackage | sources、assumptions、矩阵缺口 | site-evidence.schema；check_rule_consistency | CRS/单位/尺度/来源日期/方法/许可/缺口；不知道则标未知 |
| 三类结果 | design-depth.review_states；evaluation | self_check三个结果对象 | self_check_submission；design_depth | 自动合规、内容未评审、待核实事项；无自动设计批准 |
| 机构申请 | practice-schedule；firm-track；中英PDF | 官网注册、专属逐项材料页、可选工作表 | 私有API的文件/页数/完整性/权限校验 | 注册截止12月31日；完整在线申请1月31日；2月选五家；邮件只发送私链/通知 |
| 更新订阅 | 首页interest表单 | tracks多选 | interest.js | 仅首页、可选两赛道；邮件发送后才完成订阅，与报名分开 |

## 兼容与迁移

两份指定历史投稿不批量重写。其节点选择、主册包装和矩阵适用分别判断，不能相互替代。只有这两条完整路径可保留第一版矩阵；新目录必须第二版，不能自行声明旧版。第二版需实际 decision、范围与阶段、分类型缺口、绘图和几何引用；主动升级后复算指标、更新图纸与HTML再跑检查。

旧版历史建筑量分子可能包括master外全部建筑，分母为master面积，不能自动当作真实首期密度。v2仅按master裁切计算GFA/覆盖率/FAR，区外GFA另报；实际首期、首批工程及必要外置工程仍须分别说明。五类系统可以复合，不套用互斥land_use分区规则。

两类固定试点均受保护。旧生活区被标农业的背景表达仅为v1历史兼容，不代表已核实其内部用途；迁移时应按生活区语义修正。主办方资料缺口不自动淘汰，但缺口披露不能代替参赛者必交图纸和设计判断。

## 可复现验证

- `python -m unittest discover -s scripts -p 'test_*.py'`
- `python scripts/check_rule_consistency.py`
- `python scripts/check_boundary_consistency.py`
- `python scripts/self_check_submission.py --all --no-write`
- `python scripts/verify_rule_example.py <new-isolated-repository-root>`：在独立仓库根复制规则源并署名现有样例，规范账面分区并生成第二版证据矩阵/场景/图册/HTML/检查报告。该转换只验证集成，不是修补参赛者原方案，更不是设计质量示范或审批。

测试覆盖两类pilot标签、新旧指标口径、分区遗漏重叠、场外研究标签、节点身份、引用越界/缺失、矩阵降级、占位字段、PDF损坏与页码、图纸输入与文件变更。自动检查不能判断空间品质、图纸可读性、真实适建性或工程可行性，这些保留给内容评审与专业核实。

## 本轮验证结果

30 项 Python 回归测试通过；全部 schema 解析及跨文件一致性检查通过；同源边界 GeoJSON/KML/KMZ/SHP/DXF/ZIP 继续一致。两份真实旧投稿各12/12自动检查通过，原文件指纹不变。独立副本中的非旧名单v2示例全流程12/12，通过引用一致性检查，内容评审仍为not_assessed、专业核实缺口仍declared；主册16页、技术附件10页、A0一页，无固定页数要求。

机构API通过11项单测、TypeScript及生产构建；本地浏览器已验证专属材料页、上传一页虚拟PDF、保存、读取、声明和最终收件。没有在生产建立测试机构。两份31页任务书及中英文六页可选工作表已重新渲染并检查本轮变更页。
