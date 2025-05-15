## GitHub Pull Request 流程指南

建议添加 [GitHub SSH]()

### **一、贡献者（Contributor）视角**  

#### **1. 准备工作**  

1. **Fork 仓库**  
   - 在 GitHub 上找到目标仓库，点击 `Fork` 按钮，创建个人副本。  
2. **克隆本地仓库**  

   ```bash
   git clone https://github.com/你的用户名/仓库名.git
   cd 仓库名
   git remote add upstream https://github.com/原始仓库/仓库名.git  # 关联上游仓库
   ```

#### **2. 开发新功能/修复**  

3. **创建新分支**  

   ```bash
   git checkout -b feature/your-feature-name  # 分支名需清晰描述功能
   ```

4. **提交代码**  
   - 修改代码后提交，遵循项目 Commit 规范（如 [Conventional Commits](https://www.conventionalcommits.org)）：

   ```bash
   git add .
   git commit -m "feat: add user login API"
   ```

5. **同步上游变更（避免冲突）**  

   ```bash
   git fetch upstream
   git rebase upstream/main  # 或 merge
   ```

#### **3. 发起 PR**  

6. **推送分支到个人 Fork**  

   ```bash
   git push origin feature/your-feature-name
   ```

7. **在 GitHub 上创建 PR**  
   - 进入个人 Fork 仓库页面，点击 `Compare & pull request`。  
   - 填写 PR 模板：  
     - **标题**：清晰描述变更（如 "feat: add user login API"）。  
     - **内容**：说明修改目的、关联的 Issue（如 `Closes #123`）、测试结果等。  
   - 选择目标分支（通常是 `main` 或 `develop`）。  

#### **4. 跟进 PR 审查**  

8. **响应 Review 意见**  
   - 根据仓库管理者的评论修改代码，追加提交：  

   ```bash
   git add .
   git commit -m "fix: address review comments"
   git push origin feature/your-feature-name  # 自动更新 PR
   ```

   - 如需合并多个 Commit 保持整洁：  

     ```bash
     git rebase -i HEAD~3  # 交互式合并
     git push -f origin feature/your-feature-name  # 强制推送
     ```

---

### **二、仓库管理者（Maintainer）视角**  

#### **1. 预检 PR**  

1. **检查 PR 合规性**  
   - 确认 PR 标题/描述符合规范。  
   - 检查关联的 Issue 或讨论（如有）。  
   - 验证 CI 测试是否通过（如 GitHub Actions）。  

#### **2. 代码审查（Code Review）**  

2. **Review 代码**  
   - 在 GitHub PR 页面的 `Files changed` 选项卡中：  
     - 逐行评论（点击行号左侧 `+`）。  
     - 提出改进建议或请求变更。  
   - 使用标签（如 `needs-test`、`blocked`）标记状态。  

3. **请求变更或批准**  
   - 若需修改：点击 `Request changes` 并说明原因。  
   - 若通过：点击 `Approve`。  

#### **3. 合并 PR**  

4. **选择合并策略**（需符合项目规则）  
   - **Merge Commit**：保留完整历史（`Create a merge commit`）。  
   - **Rebase**：线性提交历史（`Rebase and merge`）。  
   - **Squash**：压缩为单个 Commit（`Squash and merge`）。  
5. **删除分支**（勾选 `Delete branch` 清理无用分支）。  

#### **4. 后续处理**  

6. **版本发布**  
   - 若 PR 涉及新功能，更新 `CHANGELOG.md` 或打版本标签（Tag）。
7. **同步 Fork 仓库**（可选）  
   - 提醒贡献者更新其 Fork 副本：  

     ```bash
     git fetch upstream
     git checkout main
     git merge upstream/main
     ```

---

### **三、关键注意事项**  

- **分支管理**：  
  - 贡献者：确保分支基于最新上游代码，避免冲突。  
  - 管理者：保护主分支（通过 GitHub 的 `Branch protection rules`）
- **CI/CD 集成**：PR 需通过自动化测试后才能合并。
- **沟通礼仪**：Review 时保持友好，明确问题与建议。

---

### **流程图示意（简化版）**  

```
贡献者：Fork → Clone → 开发 → Push → PR → 修改 → 合并  
管理者：预检 → Review → 批准/拒绝 → 合并 → 清理  
```
