# 上传到 Hugging Face

上传 `prepare_hf_release.py` 最终生成的完整目录。它包含类别图片 ZIP、完整 JSON、类别 JSON ZIP、实际格式报告、许可证和校验文件。准备工具目录和 `preview/` 不作为最终数据上传。

首先检查输出目录存在 `RELEASE_READY.json`。该文件表示图片 ZIP 与索引生成完成并通过结构检查。打开 `quality_report.json` 查看实际读取错误、文件名配对和尺寸差异记录；这些记录不会造成图片被自动删除。

在 Hugging Face 网页创建一个 dataset 仓库，再在有最终发布目录的机器上运行：

```bash
python3 -m pip install -U huggingface_hub
hf auth login
hf upload 你的用户名/Real-IAD-MVN /实际生成的发布目录 . --repo-type dataset
```

将仓库 ID 和发布目录替换为实际值。`hf auth login` 会交互式完成登录；不要把 Token 写进准备包或 JSON。上传操作由你执行，准备脚本只生成本地发布文件。

如果要采用 D³ 的申请访问方式，在目标数据集仓库设置页面配置 gated access；该设置不由 JSON 或 README 决定。

下载或迁移发布目录后，运行：

```bash
python3 /实际生成的发布目录/verify_release.py --root /实际生成的发布目录
```

成功会输出 `"status": "passed"`。该检查会读取全部图片 ZIP 来验证 SHA-256，耗时取决于磁盘速度。

说明和操作依据：

- [Hugging Face Dataset Cards](https://huggingface.co/docs/hub/datasets-cards)
- [Hugging Face Upload Guide](https://huggingface.co/docs/huggingface_hub/guides/upload)
- [Hugging Face Gated Datasets](https://huggingface.co/docs/hub/datasets-gated)

README 使用英文，便于全球用户阅读。总 JSON 与目录名中的中文保留为 UTF-8。JSON 路径使用 `/`，指向解压后的 `realiad_mvn_raw/`。本发布没有训练／验证／测试划分。
