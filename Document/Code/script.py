class UseCase:
    def __init__(self, name, actors, preconditions, main_flow, alternative_flow, postconditions, non_functional):
        self.name = name
        self.actors = actors
        self.preconditions = preconditions
        self.main_flow = main_flow
        self.alternative_flow = alternative_flow
        self.postconditions = postconditions
        self.non_functional = non_functional

    def to_markdown(self):
        return f"""### {self.name}

| 项目 | 描述 |
|------|------|
| 用例名称 | {self.name} |
| 主要参与者 | {', '.join(self.actors)} |
| 前置条件 | {self.preconditions} |
| 基本流程 | {self.main_flow} |
| 替代流程 | {self.alternative_flow} |
| 后置条件 | {self.postconditions} |
| 非功能需求 | {self.non_functional} |
"""

def generate_use_cases():
    use_cases = [
        UseCase(
            name="上传URDF文件",
            actors=["用户", "前端系统", "文件管理API"],
            preconditions="用户已登录系统，有可用的URDF文件",
            main_flow="""1. 用户点击"上传文件"按钮
2. 系统打开文件选择对话框
3. 用户选择URDF文件
4. 系统验证文件格式
5. 系统上传文件到服务器
6. 系统显示上传成功消息""",
            alternative_flow="""3a. 用户取消选择：返回主界面
4a. 文件格式无效：显示错误消息
5a. 上传失败：显示错误消息并允许重试""",
            postconditions="URDF文件成功保存到服务器，文件列表更新",
            non_functional="""- 上传响应时间 < 5秒
- 支持文件大小限制
- 支持并发上传"""
        ),
        UseCase(
            name="浏览URDF文件列表",
            actors=["用户", "前端系统", "文件管理API"],
            preconditions="系统中存在已上传的URDF文件",
            main_flow="""1. 用户进入文件浏览器页面
2. 系统加载文件列表
3. 系统显示分页文件列表
4. 用户浏览文件信息
5. 用户选择文件进行可视化""",
            alternative_flow="""2a. 加载失败：显示错误消息
4a. 用户翻页：加载下一页内容
4b. 用户返回：返回上一页""",
            postconditions="用户可以选择文件进行可视化操作",
            non_functional="""- 页面加载时间 < 2秒
- 每页显示20个文件
- 支持文件搜索和排序"""
        ),
        UseCase(
            name="加载和显示URDF模型",
            actors=["用户", "前端系统", "URDF处理API", "Three.js渲染器"],
            preconditions="用户已选择有效的URDF文件",
            main_flow="""1. 用户选择文件进行可视化
2. 系统获取URDF文件内容
3. 系统初始化Three.js场景
4. 系统加载URDF模型
5. 系统设置相机和控制器
6. 系统显示3D模型""",
            alternative_flow="""2a. 获取失败：显示错误消息
4a. 模型加载失败：显示错误消息
6a. 渲染失败：显示错误消息""",
            postconditions="URDF模型成功加载并显示在3D视图中",
            non_functional="""- 模型加载时间 < 10秒
- 支持大型模型
- 保持60fps的渲染帧率"""
        ),
        UseCase(
            name="3D模型交互控制",
            actors=["用户", "前端系统", "Three.js渲染器"],
            preconditions="URDF模型已成功加载并显示",
            main_flow="""1. 用户操作模型（旋转/缩放/平移）
2. 系统接收用户输入
3. 系统更新控制器状态
4. 系统更新相机位置
5. 系统重新渲染场景
6. 系统显示更新后的视图""",
            alternative_flow="""2a. 无效操作：忽略输入
3a. 超出范围：限制操作范围""",
            postconditions="模型视图根据用户操作更新",
            non_functional="""- 操作响应时间 < 100ms
- 平滑的动画过渡
- 支持触摸和鼠标操作"""
        ),
        UseCase(
            name="停止URDF模型可视化",
            actors=["用户", "前端系统", "URDF处理API", "Three.js渲染器"],
            preconditions="URDF模型正在显示中",
            main_flow="""1. 用户点击停止按钮
2. 系统发送停止请求
3. 系统停止动画循环
4. 系统释放3D资源
5. 系统清理内存
6. 系统显示停止状态""",
            alternative_flow="""2a. 停止请求失败：显示错误消息
4a. 资源释放失败：记录错误日志""",
            postconditions="可视化完全停止，资源被释放",
            non_functional="""- 停止响应时间 < 1秒
- 确保资源完全释放
- 支持优雅降级"""
        )
    ]
    
    return use_cases

def generate_markdown():
    use_cases = generate_use_cases()
    markdown = "# URDF可视化平台用例描述\n\n"
    
    for use_case in use_cases:
        markdown += use_case.to_markdown() + "\n"
    
    return markdown

def save_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    markdown_content = generate_markdown()
    save_to_file(markdown_content, "use_cases.md")
    print("用例描述表已生成到 use_cases.md")