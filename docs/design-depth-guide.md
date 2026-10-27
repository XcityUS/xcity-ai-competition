# Design-depth evidence and review / 设计深度证据与评审

The four levels in `brief/design-depth.json` are connected tests of the same city. They do not impose four fixed map extents. The urban-design enlargement may coincide with part of the phase-one master area; select it for the spatial question, not an area target. Keep the existing three-node group choice.

## Fill the matrix / 填写矩阵

Copy `templates/design_depth_matrix.json` (the scaffolder does this). Rows are `whole_site`, `phase_one`, `urban_design`, `nodes`, and `node:<ID>` for every selected node. Each row links:

- `drawings`: package-relative formal drawings or PDF paths. Identify page/figure and its claim in the linked proposal heading; the checker checks files, not their visual content.
- `geometry`: package-relative submitted geometry used for that decision.
- `metrics`: exact keys present in `metrics.json`, with scope/phase/basis explained in the proposal.
- `explanation`: package-relative text path and an existing `## ` heading prefix.
- `status`: `documented` or `partial`, an entrant declaration; neither means approved.
- `gaps`: missing evidence/data/design, next verification and responsible role. Empty evidence lists need a disclosed gap. Do not invent missing data to clear a check.

Paths must remain inside the submission, without symlink escapes. A combined drawing can support several rows. There is no required page count. A matrix of links to uninformative pictures may pass reference checks and still fail content review. Partial disclosure allows honest uncertainty; it is not a guarantee of design acceptance. The published gates still apply to all other required files and metrics.

## Three independent results / 三类结果

1. **Automatic compliance / 自动检查**: G1–G12 check encoded file, geometry, number, version and reference rules. The matrix subsection says `references_consistent` or `failed`; it does not say design passed.
2. **Content review / 内容评审**: always `not_assessed` in generated reports. A reviewer must judge whether the whole-site structure is reasonable, phase one can stand alone, the enlargement creates streets/public life, and nodes support the overall promise. No automated content score is generated.
3. **Further work / 待深化**: reports repeat entrant-declared gaps and next verification/responsibility. `none_declared_not_verified` means no gaps were declared, not that none exist.

`self_check.json.design_depth_assessment` preserves all three; CLI output distinguishes them. Reviewers should add their separate signed/dated review rather than changing an entrant's machine check into an approval. Missing organiser information itself is not an automatic elimination reason.

The two exact organiser-listed legacy entries are unchanged and retain their previous evidence requirements. They opt in to the matrix only by adding it. Presentation-index opt-in is independent; regenerating a booklet alone does not silently demand an invented matrix.

## Review questions / 评审时要问

- 全场地：选址与保留的取舍有什么依据？城镇、五类系统、交通与资源如何连接？容量情景是否对应资源约束？
- 首期：后续停止时，居住、公服、岗位、物流和市政是否仍然完整？第一批工程和资金/资源依赖在哪里？
- 城市设计：街区与建筑高度、入口、步行、阴影、公共空间和服务界面是否共同支持日常生活？
- 节点：谁在何时使用？平剖面和运行情景能否解释效果图？对总体方案的哪个承诺进行了检验？

Use the annotated examples in `reference-examples.md` as method prompts, never as a preferred urban form.
