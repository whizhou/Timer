 * 所有操作均在`frontends`目录下进行
### 环境配置
 * 前往官网下载并安装node.js: `https://nodejs.org/zh-cn` ，建议选择 `v22.15.0`
### 开发与调试
 * cmd输入`npm i`安装依赖
 * 实时调试：`npm run dev`
 * 打包项目：`npm run build`，随后会生成`dist`文件夹，即为打包好的网页文件
### 查看效果
 * 可以通过调试命令`npm run dev`实时查看网页效果
 * 也可以在打包完之后，在`dist`目录下执行以下步骤：
 * cmd -> `npm install http-server -g`
 * cmd -> `http-server -c-1`
 * 浏览器访问`localhost:8080`
