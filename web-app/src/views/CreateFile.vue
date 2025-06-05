<!-- CreateFile.vue -->
<template>
  <BackgroundLayout>
    <div class="create-container">
      <!-- URDF 预览面板 -->
      <div v-if="isModeling" class="urdf-preview-panel" :class="{ 'collapsed': !showURDFPreview }">
        <div class="preview-header" @click="toggleURDFPreview">
          <h3>URDF 预览</h3>
          <span class="toggle-icon">{{ showURDFPreview ? '−' : '+' }}</span>
        </div>
        <div v-show="showURDFPreview" class="preview-content">
          <pre><code>{{ generateURDF() }}</code></pre>
        </div>
      </div>

      <button class="home-button" @click="goToHome">
        Back to Home
      </button>
      
      <div class="main-content">
        <!-- 左侧工具栏 -->
        <div class="toolbar">
          <BasicOperations 
            :is-modeling="isModeling"
            @start-modeling="startModeling"
            @add-link="addLink"
            @add-joint="addJoint"
          />
          
          <div class="tool-section" v-if="isModeling">
            <h3>文件操作</h3>
            <button class="tool-button" @click="saveURDF">
              <span class="icon">💾</span>
              保存URDF
            </button>
          </div>

          <!-- 添加视图控制部分 -->
          <div class="tool-section" v-if="isModeling">
            <h3>视图控制</h3>
            <button class="tool-button" @click="toggleGrid">
              <span class="icon">📏</span>
              {{ showGrid ? '隐藏网格' : '显示网格' }}
            </button>
            <button class="tool-button" @click="resetView">
              <span class="icon">🔄</span>
              重置视图
            </button>
          </div>
        </div>

        <!-- 中间3D视图区域 -->
        <div class="viewer-container" :class="{ 'with-panel': showPropertyPanel }">
          <div v-if="!isModeling" class="start-prompt">
            <div class="prompt-content">
              <div class="prompt-icon">🎨</div>
              <div class="prompt-text">点击"开始建模"按钮开始创建您的机器人模型</div>
            </div>
          </div>
          <URDFViewer
            v-if="isModeling"
            :urdf-content="currentURDF"
            class="viewer"
            ref="urdfViewer"
          />
        </div>

        <!-- 右侧属性面板占位 -->
        <div class="properties-panel-space">
          <div class="properties-panel" v-if="showPropertyPanel">
            <div class="panel-section">
              <div class="panel-header">
                <h3>{{ isAddingJoint ? '添加新关节' : (isEditing ? '添加新连杆' : '编辑属性') }}</h3>
                <button class="close-button" @click="cancelEdit">×</button>
              </div>
              
              <!-- 使用连杆属性组件 -->
              <LinkProperties
                v-if="!isAddingJoint"
                v-model:properties="linkProperties"
                :is-editing="isEditing"
                @save="saveProperties"
                @delete="deleteSelectedObject"
                @cancel="cancelEdit"
              />

              <!-- 使用关节属性组件 -->
              <JointProperties
                v-else
                v-model:properties="jointProperties"
                :is-editing="isEditing"
                :links="links"
                @save="saveProperties"
                @delete="deleteSelectedObject"
                @cancel="cancelEdit"
              />
              
              <!-- 添加验证错误提示 -->
              <div v-if="jointValidationErrors.length > 0" class="validation-errors">
                <div class="error-header">
                  <span class="error-icon">⚠</span>
                  <span>验证错误</span>
                </div>
                <ul>
                  <li v-for="(error, index) in jointValidationErrors" :key="index">
                    {{ error }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BackgroundLayout>
</template>

<script>
import BackgroundLayout from '@/components/BackgroundLayout.vue'
import BasicOperations from '@/components/BasicOperations.vue'
import LinkProperties from '@/components/LinkProperties.vue'
import JointProperties from '@/components/JointProperties.vue'
import URDFViewer from '@/components/URDFViewer.vue'
import * as THREE from 'three'
import { ElMessage } from 'element-plus'

export default {
  name: 'CreateFile',
  components: {
    BackgroundLayout,
    BasicOperations,
    LinkProperties,
    JointProperties,
    URDFViewer
  },
  data() {
    return {
      isModeling: false,
      selectedObject: null,
      showPropertyPanel: false,
      isEditing: false,
      isAddingJoint: false,
      jointValidationErrors: [],
      showURDFPreview: true,
      links: new Map(), // 存储所有连杆
      joints: new Map(), // 存储所有关节
      currentURDF: null, // 当前的 URDF 内容
      linkProperties: {
        name: '',
        type: 'box',
        dimensions: {
          x: 1,
          y: 1,
          z: 1
        },
        color: '#9f6bff',
        position: {
          x: 0,
          y: 0,
          z: 0
        },
        rotation: {
          roll: 0,
          pitch: 0,
          yaw: 0
        },
        mass: 1,
        inertia: {
          ixx: 1,
          ixy: 0,
          ixz: 0,
          iyy: 1,
          iyz: 0,
          izz: 1
        },
        collision: {
          enabled: false,
          type: 'box',
          dimensions: {
            x: 1,
            y: 1,
            z: 1
          }
        },
        material: {
          type: 'default',
          texture: ''
        }
      },
      jointProperties: {
        name: '',
        type: 'revolute',
        parent: '',
        child: '',
        position: {
          x: 0,
          y: 0,
          z: 0
        },
        rotation: {
          roll: 0,
          pitch: 0,
          yaw: 0
        },
        axis: {
          x: 0,
          y: 0,
          z: 1
        },
        limits: {
          lower: -3.14,
          upper: 3.14,
          effort: 100,
          velocity: 1
        }
      },
      showGrid: true, // 控制网格显示
    }
  },
  methods: {
    goToHome() {
      this.$router.push('/')
    },
    // 将十六进制颜色转换为rgba格式
    hexToRgba(hex) {
      // 移除#号如果存在
      hex = hex.replace('#', '')
      
      // 解析RGB值
      const r = parseInt(hex.substring(0, 2), 16) / 255
      const g = parseInt(hex.substring(2, 4), 16) / 255
      const b = parseInt(hex.substring(4, 6), 16) / 255
      
      // URDF中的alpha值默认为1
      return `${r.toFixed(3)} ${g.toFixed(3)} ${b.toFixed(3)} 1.0`
    },
    startModeling() {
      this.isModeling = true;
      this.updateURDFPreview();
    },
    addLink() {
      console.log('Step 1: addLink method called');
      console.log('Before - linkProperties:', JSON.stringify(this.linkProperties));
      
      this.showPropertyPanel = true;
      this.isEditing = true;
      // 不要重置属性，而是保持用户输入的值
      if (!this.linkProperties.name) {
        console.log('Resetting properties because name is empty');
        this.resetLinkProperties();
      }
      
      console.log('After - linkProperties:', JSON.stringify(this.linkProperties));
      console.log('showPropertyPanel:', this.showPropertyPanel);
      console.log('isEditing:', this.isEditing);
    },
    addJoint() {
      this.showPropertyPanel = true
      this.isEditing = true
      this.isAddingJoint = true
      this.resetJointProperties()
    },
    saveURDF() {
      try {
        // 生成URDF内容
        const urdfContent = this.generateURDF()
        
        // 显示保存对话框
        const filename = prompt('请输入文件名（不需要.urdf后缀）：', 'robot')
        if (!filename) return
        
        // 发送保存请求
        fetch('http://localhost:5000/api/files/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            filename: filename,
            content: urdfContent
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 200) {
            alert(`文件保存成功：${data.filename}`)
          } else {
            alert(`保存失败：${data.error}`)
          }
        })
        .catch(error => {
          console.error('保存文件时出错：', error)
          alert('保存文件时出错')
        })
      } catch (error) {
        console.error('生成URDF时出错：', error)
        alert('生成URDF时出错')
      }
    },
    generateURDF() {
      // 生成URDF头部
      let urdf = `<?xml version="1.0"?>
<robot name="robot">
`

      // 添加所有连杆
      for (const [, link] of this.links) {
        const props = link.properties
        urdf += `  <!-- ${props.name} -->
  <link name="${props.name}">
    <visual>
      <origin xyz="${props.position.x} ${props.position.y} ${props.position.z}" 
              rpy="${props.rotation.roll * Math.PI / 180} ${props.rotation.pitch * Math.PI / 180} ${props.rotation.yaw * Math.PI / 180}"/>
      <geometry>
`
        // 根据类型添加几何体
        switch (props.type) {
          case 'box':
            urdf += `        <box size="${props.dimensions.x} ${props.dimensions.y} ${props.dimensions.z}"/>
`
            break
          case 'cylinder':
            urdf += `        <cylinder radius="${props.dimensions.x/2}" length="${props.dimensions.y}"/>
`
            break
          case 'sphere':
            urdf += `        <sphere radius="${props.dimensions.x/2}"/>
`
            break
        }
        
        urdf += `      </geometry>
      <material name="${props.name}_material">
        <color rgba="${this.hexToRgba(props.color)}"/>
      </material>
    </visual>
    <collision>
      <origin xyz="${props.position.x} ${props.position.y} ${props.position.z}" 
              rpy="${props.rotation.roll * Math.PI / 180} ${props.rotation.pitch * Math.PI / 180} ${props.rotation.yaw * Math.PI / 180}"/>
      <geometry>
`
        // 添加碰撞几何体
        if (props.collision.enabled) {
          switch (props.collision.type) {
            case 'box':
              urdf += `        <box size="${props.collision.dimensions.x} ${props.collision.dimensions.y} ${props.collision.dimensions.z}"/>
`
              break
            case 'cylinder':
              urdf += `        <cylinder radius="${props.collision.dimensions.x/2}" length="${props.collision.dimensions.y}"/>
`
              break
            case 'sphere':
              urdf += `        <sphere radius="${props.collision.dimensions.x/2}"/>
`
              break
          }
        } else {
          // 如果没有启用碰撞，使用与视觉相同的几何体
          switch (props.type) {
            case 'box':
              urdf += `        <box size="${props.dimensions.x} ${props.dimensions.y} ${props.dimensions.z}"/>
`
              break
            case 'cylinder':
              urdf += `        <cylinder radius="${props.dimensions.x/2}" length="${props.dimensions.y}"/>
`
              break
            case 'sphere':
              urdf += `        <sphere radius="${props.dimensions.x/2}"/>
`
              break
          }
        }
        
        urdf += `      </geometry>
    </collision>
    <inertial>
      <origin xyz="${props.position.x} ${props.position.y} ${props.position.z}" 
              rpy="${props.rotation.roll * Math.PI / 180} ${props.rotation.pitch * Math.PI / 180} ${props.rotation.yaw * Math.PI / 180}"/>
      <mass value="${props.mass}"/>
      <inertia ixx="${props.inertia.ixx}" ixy="${props.inertia.ixy}" ixz="${props.inertia.ixz}"
               iyy="${props.inertia.iyy}" iyz="${props.inertia.iyz}" izz="${props.inertia.izz}"/>
    </inertial>
  </link>
`
      }

      // 添加所有关节
      for (const [, joint] of this.joints) {
        const props = joint.properties
        urdf += `  <!-- ${props.name} -->
  <joint name="${props.name}" type="${props.type}">
    <parent link="${props.parent}"/>
    <child link="${props.child}"/>
    <origin xyz="${props.position.x} ${props.position.y} ${props.position.z}"
            rpy="${props.rotation.roll * Math.PI / 180} ${props.rotation.pitch * Math.PI / 180} ${props.rotation.yaw * Math.PI / 180}"/>
    <axis xyz="${props.axis.x} ${props.axis.y} ${props.axis.z}"/>
`
        // 添加关节限制
        if (props.type !== 'fixed') {
          urdf += `    <limit lower="${props.limits.lower}" upper="${props.limits.upper}"
             effort="${props.limits.effort}" velocity="${props.limits.velocity}"/>
`
        }
        urdf += `  </joint>
`
      }

      // 添加URDF尾部
      urdf += `</robot>`

      return urdf
    },
    createLink() {
      // 生成唯一的连杆名称
      let linkName = this.linkProperties.name.trim();
      
      // 只有当名称为空时才生成自动名称
      if (!linkName) {
        let index = this.links.size + 1;
        while (this.links.has(`link_${index}`)) {
          index++;
        }
        linkName = `link_${index}`;
        console.warn(`使用自动生成的名称: ${linkName}`);
      } else if (this.links.has(linkName)) {
        // 如果用户提供的名称已存在，提示用户
        alert(`连杆名称 "${linkName}" 已存在，请使用其他名称。`);
        return;
      }
      
      // 存储连杆属性（创建深拷贝以避免引用问题）
      const properties = JSON.parse(JSON.stringify(this.linkProperties));
      properties.name = linkName; // 确保名称一致
      
      this.links.set(linkName, { properties });
      
      console.log('Created link:', {
        name: linkName,
        properties: properties
      });
    },
    createJoint() {
      const jointName = this.jointProperties.name.trim() || `joint_${this.joints.size + 1}`;
      
      // 存储关节属性
      const properties = JSON.parse(JSON.stringify(this.jointProperties));
      properties.name = jointName;
      
      this.joints.set(jointName, { properties });
      
      console.log('Created joint:', {
        name: jointName,
        properties: properties
      });
    },
    validateJoint(properties) {
      const errors = [];
      
      // 验证关节名称
      if (!properties.name.trim()) {
        errors.push('关节名称不能为空');
      } else if (this.joints.has(properties.name) && this.isAddingJoint) {
        errors.push('关节名称已存在');
      }
      
      // 验证父子连杆
      if (!properties.parent.trim()) {
        errors.push('必须指定父连杆');
      } else if (!this.links.has(properties.parent)) {
        errors.push('父连杆不存在');
      }
      
      if (!properties.child.trim()) {
        errors.push('必须指定子连杆');
      } else if (!this.links.has(properties.child)) {
        errors.push('子连杆不存在');
      }
      
      // 验证父子连杆不能相同
      if (properties.parent === properties.child && properties.parent !== '') {
        errors.push('父连杆和子连杆不能相同');
      }
      
      // 验证关节类型
      const validTypes = ['revolute', 'continuous', 'prismatic', 'fixed', 'floating', 'planar'];
      if (!validTypes.includes(properties.type)) {
        errors.push('无效的关节类型');
      }
      
      // 验证轴向
      if (properties.type !== 'fixed') {
        const axis = properties.axis;
        if (Math.abs(axis.x) === 0 && Math.abs(axis.y) === 0 && Math.abs(axis.z) === 0) {
          errors.push('关节轴向不能为零向量');
        }
      }
      
      // 验证限制值
      if (properties.type === 'revolute' || properties.type === 'prismatic') {
        const limits = properties.limits;
        if (limits.lower > limits.upper) {
          errors.push('下限不能大于上限');
        }
        if (limits.effort <= 0) {
          errors.push('力矩限制必须大于0');
        }
        if (limits.velocity <= 0) {
          errors.push('速度限制必须大于0');
        }
      }
      
      // 检查循环依赖
      if (this.wouldCreateCycle(properties.parent, properties.child)) {
        errors.push('不能创建循环依赖的关节链');
      }
      
      return errors;
    },
    wouldCreateCycle(parent, child) {
      // 用于检测是否会形成循环依赖的辅助函数
      const visited = new Set();
      
      const dfs = (current) => {
        if (current === parent) return true;
        if (visited.has(current)) return false;
        
        visited.add(current);
        
        // 遍历所有以current为子连杆的关节
        for (const [, joint] of this.joints) {
          if (joint.properties.child === current) {
            if (dfs(joint.properties.parent)) return true;
          }
        }
        
        return false;
      };
      
      return dfs(child);
    },
    saveProperties(properties) {
      console.log('CreateFile - Received properties:', properties);
      
      if (this.isAddingJoint || (this.selectedObject && this.selectedObject.startsWith('joint_'))) {
        // 更新 jointProperties
        this.jointProperties = { ...properties };
        
        // 执行关节验证
        const errors = this.validateJoint(properties);
        console.log('Joint validation errors:', errors);
        if (errors.length > 0) {
          this.jointValidationErrors = errors;
          return; // 如果有错误，不保存
        }
        this.jointValidationErrors = []; // 清除之前的错误
        
        if (this.isAddingJoint) {
          this.createJoint();
          this.resetJointProperties();
        } else {
          // 更新现有关节
          const jointName = this.selectedObject;
          const joint = this.joints.get(jointName);
          if (joint) {
            joint.properties = { ...properties };
          }
        }
      } else {
        // 连杆相关的逻辑
        this.linkProperties = { ...properties };
        if (this.isEditing) {
          if (this.links.has(this.linkProperties.name)) {
            console.log('Error: Link name already exists');
            alert(`连杆名称 "${this.linkProperties.name}" 已存在，请使用其他名称。`);
            return;
          }
          this.createLink();
        } else if (this.selectedObject) {
          // 更新现有连杆
          const linkName = this.selectedObject;
          const link = this.links.get(linkName);
          if (link) {
            link.properties = { ...properties };
          }
        }
      }
      
      this.showPropertyPanel = false;
      this.isEditing = false;
      this.isAddingJoint = false;

      // 更新 URDF 预览
      this.updateURDFPreview();
    },
    deleteSelectedObject() {
      if (this.selectedObject) {
        if (this.selectedObject.startsWith('joint_')) {
          // 删除关节
          this.joints.delete(this.selectedObject);
        } else {
          // 删除连杆
          this.links.delete(this.selectedObject);
        }
        this.selectedObject = null;
        this.showPropertyPanel = false;
      }
    },
    resetLinkProperties() {
      console.log('Resetting link properties to default values');
      this.linkProperties = {
        name: '',
        type: 'box',
        dimensions: {
          x: 1,
          y: 1,
          z: 1
        },
        color: '#9f6bff',
        position: {
          x: 0,
          y: 0,
          z: 0
        },
        rotation: {
          roll: 0,
          pitch: 0,
          yaw: 0
        },
        mass: 1,
        inertia: {
          ixx: 1,
          ixy: 0,
          ixz: 0,
          iyy: 1,
          iyz: 0,
          izz: 1
        },
        collision: {
          enabled: false,
          type: 'box',
          dimensions: {
            x: 1,
            y: 1,
            z: 1
          }
        },
        material: {
          type: 'default',
          texture: ''
        }
      };
      console.log('Reset link properties:', this.linkProperties);
    },
    resetJointProperties() {
      this.jointProperties = {
        name: '',
        type: 'revolute',
        parent: '',
        child: '',
        position: {
          x: 0,
          y: 0,
          z: 0
        },
        rotation: {
          roll: 0,
          pitch: 0,
          yaw: 0
        },
        axis: {
          x: 0,
          y: 0,
          z: 1
        },
        limits: {
          lower: -3.14,
          upper: 3.14,
          effort: 100,
          velocity: 1
        }
      };
    },
    cancelEdit() {
      this.showPropertyPanel = false;
      this.isEditing = false;
      this.isAddingJoint = false;
      // 重置连杆属性
      if (!this.isAddingJoint) {
        this.resetLinkProperties();
      }
      // 重置关节属性
      else {
        this.resetJointProperties();
      }
    },
    toggleURDFPreview() {
      this.showURDFPreview = !this.showURDFPreview;
    },
    // 修改更新预览的方法
    updateURDFPreview() {
      // 直接生成并更新 URDF 内容
      this.currentURDF = this.generateURDF();
    },
    // 重置视图
    resetView() {
      // 清除所有连杆和关节
      this.links.clear();
      this.joints.clear();
      
      // 重置属性
      this.selectedObject = null;
      this.showPropertyPanel = false;
      this.isEditing = false;
      this.isAddingJoint = false;
      this.jointValidationErrors = [];
      
      // 重置连杆属性
      this.linkProperties = {
        name: '',
        type: 'box',
        dimensions: {
          x: 1,
          y: 1,
          z: 1
        },
        color: '#9f6bff',
        position: {
          x: 0,
          y: 0,
          z: 0
        },
        rotation: {
          roll: 0,
          pitch: 0,
          yaw: 0
        },
        mass: 1,
        inertia: {
          ixx: 1,
          ixy: 0,
          ixz: 0,
          iyy: 1,
          iyz: 0,
          izz: 1
        },
        collision: {
          enabled: false,
          type: 'box',
          dimensions: {
            x: 1,
            y: 1,
            z: 1
          }
        },
        material: {
          type: 'default',
          texture: ''
        }
      };
      
      // 重置关节属性
      this.jointProperties = {
        name: '',
        type: 'revolute',
        parent: '',
        child: '',
        position: {
          x: 0,
          y: 0,
          z: 0
        },
        rotation: {
          roll: 0,
          pitch: 0,
          yaw: 0
        },
        axis: {
          x: 0,
          y: 0,
          z: 1
        },
        limits: {
          lower: -3.14,
          upper: 3.14,
          effort: 100,
          velocity: 1
        }
      };

      // 更新 URDF 预览
      this.updateURDFPreview();

      // 使用 ElMessage 显示提示信息
      ElMessage({
        message: '已重置到初始状态',
        type: 'success'
      });
    },
    // 切换网格显示
    toggleGrid() {
      this.showGrid = !this.showGrid;
      if (this.$refs.urdfViewer) {
        const viewer = this.$refs.urdfViewer;
        const scene = viewer.scene;
        if (scene) {
          scene.children.forEach(child => {
            if (child instanceof THREE.GridHelper) {
              child.visible = this.showGrid;
            }
          });
        }
      }
    },
  }
}
</script>

<style scoped>
.create-container {
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-top: 100px;
  position: relative;
}

.main-content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
  margin-top: 20px;
  position: relative;
  z-index: 1;
}

.toolbar {
  width: 200px;
  background: rgba(10, 10, 26, 0.4);
  border: 1px solid rgba(159, 107, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(159, 107, 255, 0.1);
  backdrop-filter: blur(5px);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tool-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-section h3 {
  color: #d8b5ff;
  font-size: 16px;
  margin-bottom: 10px;
  font-family: 'Orbitron', sans-serif;
}

.tool-button {
  background: rgba(159, 107, 255, 0.15);
  color: #d8b5ff;
  border: 2px solid rgba(216, 181, 255, 0.5);
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-button:hover {
  background: rgba(159, 107, 255, 0.25);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.5);
  transform: translateY(-2px);
}

.tool-button .icon {
  font-size: 18px;
}

.viewer-container {
  flex: 1;
  background: rgba(10, 10, 26, 0.4);
  border: 1px solid rgba(159, 107, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(159, 107, 255, 0.1);
  position: relative;
  overflow: hidden;
  margin: 0 20px;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.viewer {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.start-prompt {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(159, 107, 255, 0.05);
  position: absolute;
  top: 0;
  left: 0;
}

.prompt-content {
  text-align: center;
  padding: 30px;
  background: rgba(10, 10, 26, 0.6);
  border: 2px solid rgba(159, 107, 255, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(5px);
}

.prompt-icon {
  font-size: 48px;
  margin-bottom: 20px;
  color: #d8b5ff;
}

.prompt-text {
  color: #d8b5ff;
  font-size: 18px;
  font-family: 'Orbitron', sans-serif;
  line-height: 1.5;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #d8b5ff;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(216, 181, 255, 0.3);
  border-radius: 50%;
  border-top-color: #d8b5ff;
  animation: spin 1s ease-in-out infinite;
}

.loading-text {
  margin-top: 20px;
  font-size: 16px;
}

.properties-panel-space {
  width: 320px;
  flex-shrink: 0;
}

.properties-panel {
  width: 100%;
  background: rgba(10, 10, 26, 0.6);
  border: 1px solid rgba(159, 107, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(159, 107, 255, 0.2);
  backdrop-filter: blur(10px);
  animation: slideIn 0.3s ease-out;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  max-width: 100%;
  overflow-x: hidden;
}

.panel-section {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 15px 15px 15px;
  scrollbar-width: thin;
  scrollbar-color: rgba(159, 107, 255, 0.3) rgba(159, 107, 255, 0.1);
}

.panel-section::-webkit-scrollbar {
  width: 6px;
}

.panel-section::-webkit-scrollbar-track {
  background: rgba(159, 107, 255, 0.1);
  border-radius: 3px;
}

.panel-section::-webkit-scrollbar-thumb {
  background: rgba(159, 107, 255, 0.3);
  border-radius: 3px;
}

.panel-section::-webkit-scrollbar-thumb:hover {
  background: rgba(159, 107, 255, 0.4);
}

.panel-header {
  position: sticky;
  top: 0;
  background: rgba(159, 107, 255, 0.1);
  padding: 15px 20px;
  border-bottom: 1px solid rgba(159, 107, 255, 0.2);
  z-index: 1;
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h3 {
  color: #d8b5ff;
  font-size: 18px;
  font-family: 'Orbitron', sans-serif;
  margin: 0;
  text-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
  letter-spacing: 1px;
}

.close-button {
  background: rgba(159, 107, 255, 0.1);
  border: 1px solid rgba(159, 107, 255, 0.3);
  color: #d8b5ff;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 10px;
  line-height: 1;
  transition: all 0.3s ease;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: rgba(159, 107, 255, 0.2);
  border-color: rgba(159, 107, 255, 0.5);
  color: #fff;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.3);
}

.button-group {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: rgba(10, 10, 26, 0.6);
  border-top: 1px solid rgba(159, 107, 255, 0.2);
  position: sticky;
  bottom: 0;
  margin: 0 -15px;
  width: calc(100% + 30px);
  box-sizing: border-box;
}

.property-section h4 {
  color: #d8b5ff;
  font-size: 14px;
  margin-bottom: 12px;
  font-family: 'Orbitron', sans-serif;
}

.property-item {
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.property-item:last-child {
  margin-bottom: 0;
}

.property-item label {
  color: #d8b5ff;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.property-item input,
.property-item select {
  width: 100%;
  box-sizing: border-box;
  min-width: 0;
  background: rgba(159, 107, 255, 0.1);
  border: 1px solid rgba(216, 181, 255, 0.3);
  border-radius: 4px;
  padding: 6px;
  color: #d8b5ff;
  font-size: 12px;
  height: 28px;
}

.dimension-inputs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  width: 100%;
}

.dimension-inputs input {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  text-align: center;
  padding: 4px;
  font-size: 12px;
  height: 26px;
}

.home-button {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 8px 16px;
  background: rgba(159, 107, 255, 0.15);
  color: #d8b5ff;
  border: 2px solid rgba(216, 181, 255, 0.5);
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 100;
}

.home-button:hover {
  background: rgba(159, 107, 255, 0.25);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.5);
  transform: translateY(-2px);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.property-item input[type="color"] {
  width: 100%;
  height: 40px;
  padding: 2px;
  border: 1px solid rgba(216, 181, 255, 0.3);
  border-radius: 4px;
  background: rgba(159, 107, 255, 0.1);
  cursor: pointer;
}

.property-item input[type="color"]::-webkit-color-swatch-wrapper {
  padding: 0;
}

.property-item input[type="color"]::-webkit-color-swatch {
  border: none;
  border-radius: 2px;
}

.property-item input[type="number"] {
  width: 100%;
  text-align: center;
  -moz-appearance: textfield;
}

.property-item input[type="number"]::-webkit-outer-spin-button,
.property-item input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.save-button,
.cancel-button {
  flex: 1;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-button {
  background: rgba(159, 107, 255, 0.2);
  color: #d8b5ff;
}

.save-button:hover {
  background: rgba(159, 107, 255, 0.3);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.5);
}

.cancel-button {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
  border-color: rgba(255, 107, 107, 0.5);
}

.cancel-button:hover {
  background: rgba(255, 107, 107, 0.3);
  box-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.required {
  color: #ff6b6b;
  margin-left: 4px;
}

.error {
  border-color: #ff6b6b !important;
}

.error-message {
  color: #ff6b6b;
  font-size: 12px;
  margin-top: 4px;
}

.inertia-inputs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  width: 100%;
  margin-bottom: 8px;
}

.inertia-inputs input {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  text-align: center;
  padding: 4px;
  font-size: 12px;
  height: 26px;
}

.collision-properties {
  margin-top: 8px;
  padding: 8px;
  background: rgba(159, 107, 255, 0.1);
  border-radius: 6px;
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(159, 107, 255, 0.1);
}

.delete-button {
  flex: 1;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
  border: 2px solid rgba(255, 107, 107, 0.5);
}

.delete-button:hover {
  background: rgba(255, 107, 107, 0.3);
  box-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
}

.limit-inputs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.limit-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.limit-item label {
  font-size: 12px;
  color: rgba(216, 181, 255, 0.8);
}

.limit-item input {
  width: 100%;
  text-align: center;
}

/* 关节类型选择器样式 */
.property-item select {
  width: 100%;
  padding: 8px;
  background: rgba(159, 107, 255, 0.1);
  border: 1px solid rgba(216, 181, 255, 0.3);
  border-radius: 4px;
  color: #d8b5ff;
  font-size: 14px;
  cursor: pointer;
}

.property-item select:focus {
  outline: none;
  border-color: rgba(216, 181, 255, 0.8);
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
}

.property-item select option {
  background: rgba(10, 10, 26, 0.9);
  color: #d8b5ff;
}

/* 关节属性面板动画 */
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.properties-panel {
  animation: slideIn 0.3s ease-out;
}

.property-item input:disabled {
  background: rgba(159, 107, 255, 0.05);
  border-color: rgba(216, 181, 255, 0.2);
  color: rgba(216, 181, 255, 0.5);
  cursor: not-allowed;
}

.property-item input:disabled::placeholder {
  color: rgba(216, 181, 255, 0.3);
}

.property-section:last-child {
  margin-bottom: 0;
}

.property-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.property-item input:focus,
.property-item select:focus {
  outline: none;
  border-color: rgba(216, 181, 255, 0.8);
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
}

.save-button,
.cancel-button {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(216, 181, 255, 0.5);
}

/* 添加验证错误样式 */
.validation-errors {
  margin-top: 15px;
  padding: 12px;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 8px;
  color: #ff6b6b;
}

.validation-errors .error-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
}

.validation-errors .error-icon {
  font-size: 18px;
}

.validation-errors ul {
  margin: 0;
  padding-left: 24px;
  list-style-type: disc;
}

.validation-errors li {
  margin: 4px 0;
  font-size: 14px;
}

/* URDF 预览面板样式 */
.urdf-preview-panel {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  background: rgba(10, 10, 26, 0.9);
  border: 1px solid rgba(159, 107, 255, 0.3);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  max-height: 400px;
}

.urdf-preview-panel.collapsed {
  height: 40px;
  overflow: hidden;
}

.preview-header {
  padding: 10px 15px;
  background: rgba(159, 107, 255, 0.1);
  border-bottom: 1px solid rgba(159, 107, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  flex-shrink: 0;
}

.preview-header h3 {
  margin: 0;
  color: #d8b5ff;
  font-size: 14px;
  font-family: 'Orbitron', sans-serif;
}

.toggle-icon {
  color: #d8b5ff;
  font-size: 18px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-content {
  padding: 15px;
  overflow-y: auto;
  font-family: 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.4;
  color: #d8b5ff;
  background: rgba(10, 10, 26, 0.8);
  flex-grow: 1;
  min-height: 100px;
}

.preview-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.preview-content code {
  display: block;
  padding: 10px;
  background: rgba(159, 107, 255, 0.05);
  border-radius: 4px;
}

.preview-content::-webkit-scrollbar {
  width: 6px;
}

.preview-content::-webkit-scrollbar-track {
  background: rgba(159, 107, 255, 0.1);
  border-radius: 3px;
}

.preview-content::-webkit-scrollbar-thumb {
  background: rgba(159, 107, 255, 0.3);
  border-radius: 3px;
}

.preview-content::-webkit-scrollbar-thumb:hover {
  background: rgba(159, 107, 255, 0.4);
}
</style> 