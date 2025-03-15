# Graduation-Project
### 启动资料

#### 技术分析

WebGL: Urdf-Viz 利用现代浏览器内置的WebGL技术，实现了3D图形的实时渲染，无需任何额外的插件或软件支持。
Three.js: 该项目基于Three.js库构建，这是JavaScript的一个强大3D库，提供了丰富的功能和高效的性能。
URDF解析器: 该工具包含一个自定义的URDF解析器，可以读取并解释XML文件中的机器人模型数据，包括关节、连杆、碰撞几何体等。
交互界面: 用户可以通过简单的鼠标和键盘操作来旋转、平移、缩放模型，甚至模拟关节运动，以直观地了解机器人的工作原理。
 上述3d部分用verge3d实现

#### 参考链接：

https://verge3d.funjoy.tech/
https://funjoytech.github.io/verge3d.cn/#/?id=verge3d

探索3D世界：Urdf-Viz 交互式URDF模型可视化工具
项目地址:https://gitcode.com/gh_mirrors/ur/urdf-viz
使用WebGL结合Three.js实现3D模型的在线展示与交互优化技术https://blog.csdn.net/qq_36287830/article/details/144013832



### **项目应用点总结**

#### **1. 用户上传 URDF 文件**

- **功能**：用户通过网页上传本地的 URDF 文件。
- **实现**：
  - 使用 HTML 的文件上传控件 (`<input type="file">`)。
  - 通过 JavaScript 将文件发送到服务器。

#### **2. URDF 文件解析与加载**

- **功能**：服务器解析 URDF 文件并加载 3D 模型。
- **实现**：
  - 使用 `urdf-viz` 解析 URDF 文件。
  - 将 URDF 文件转换为 glTF 格式（通过 Blender 插件）。

#### **3. 3D 模型渲染与交互**

- **功能**：在网页中渲染 3D 模型，支持用户通过鼠标和键盘操作（旋转、平移、缩放）。
- **实现**：
  - 使用 Verge3D 加载 glTF 模型。
  - 通过 Verge3D 的拼图编辑器或 JavaScript API 实现交互功能。

#### **4. 关节运动模拟**

- **功能**：用户可以通过界面控制机器人模型的关节运动。
- **实现**：
  - 使用 Verge3D 的 JavaScript API 调用 `urdf-viz` 的 Web API，设置关节角度。
  - 提供滑块或按钮供用户操作。

#### **5. 用户界面与状态显示**

- **功能**：提供用户友好的界面，显示机器人模型的状态（如关节角度、原点位置）。
- **实现**：
  - 使用 Verge3D 的 UI 组件构建控制面板。
  - 通过 `urdf-viz` 的 Web API 获取机器人状态并显示。

#### **6. 性能优化与跨平台支持**

- **功能**：确保应用在不同设备上流畅运行。
- **实现**：
  - 使用 Verge3D 的性能优化工具（如 LOD、纹理压缩）。
  - 支持响应式设计，适配桌面和移动设备。

