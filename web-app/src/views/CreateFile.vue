<!-- CreateFile.vue -->
<template>
  <BackgroundLayout>
    <div class="create-container">
      <button class="home-button" @click="goToHome">
        Back to Home
      </button>
      
      <div class="main-content">
        <!-- 左侧工具栏 -->
        <div class="toolbar">
          <div class="tool-section">
            <h3>基本操作</h3>
            <button class="tool-button" @click="startModeling" v-if="!isModeling">
              <span class="icon">▶</span>
              开始建模
            </button>
            <template v-else>
              <button class="tool-button" @click="addLink">
                <span class="icon">+</span>
                添加连杆
              </button>
              <button class="tool-button" @click="addJoint">
                <span class="icon">+</span>
                添加关节
              </button>
            </template>
          </div>
          
          <div class="tool-section" v-if="isModeling">
            <h3>视图控制</h3>
            <button class="tool-button" @click="resetView">
              <span class="icon">↺</span>
              重置视图
            </button>
            <button class="tool-button" @click="toggleGrid">
              <span class="icon">⊞</span>
              显示/隐藏网格
            </button>
          </div>
          
          <div class="tool-section" v-if="isModeling">
            <h3>文件操作</h3>
            <button class="tool-button" @click="saveURDF">
              <span class="icon">💾</span>
              保存URDF
            </button>
          </div>
        </div>

        <!-- 中间3D视图区域 -->
        <div class="viewer-container">
          <div v-if="!isModeling" class="start-prompt">
            <div class="prompt-content">
              <div class="prompt-icon">🎨</div>
              <div class="prompt-text">点击"开始建模"按钮开始创建您的机器人模型</div>
            </div>
          </div>
          <div ref="viewer" class="viewer" v-show="isModeling"></div>
          <div v-if="loading" class="loading-overlay">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载中...</div>
          </div>
        </div>

        <!-- 右侧属性面板 -->
        <div class="properties-panel" v-if="showPropertyPanel">
          <div class="panel-section">
            <div class="panel-header">
              <h3>{{ isAddingJoint ? '添加新关节' : (isEditing ? '添加新连杆' : '编辑属性') }}</h3>
              <button class="close-button" @click="cancelEdit">×</button>
            </div>
            <div class="property-group">
              <!-- 关节属性 -->
              <template v-if="isAddingJoint">
                <div class="property-section">
                  <h4>基本属性</h4>
                  <div class="property-item">
                    <label>名称 <span class="required">*</span></label>
                    <input 
                      type="text" 
                      v-model="jointProperties.name"
                      placeholder="请输入名称"
                      :class="{ 'error': !jointProperties.name }"
                    />
                    <span class="error-message" v-if="!jointProperties.name">名称不能为空</span>
                  </div>
                  <div class="property-item">
                    <label>类型 <span class="required">*</span></label>
                    <select v-model="jointProperties.type">
                      <option value="revolute">旋转关节</option>
                      <option value="prismatic">移动关节</option>
                      <option value="continuous">连续旋转关节</option>
                      <option value="fixed">固定关节</option>
                    </select>
                  </div>
                  <div class="property-item">
                    <label>父连杆 <span class="required">*</span></label>
                    <select v-model="jointProperties.parent">
                      <option value="">请选择父连杆</option>
                      <option v-for="[id, link] in links" :key="id" :value="id">
                        {{ link.properties.name }}
                      </option>
                    </select>
                  </div>
                  <div class="property-item">
                    <label>子连杆 <span class="required">*</span></label>
                    <select v-model="jointProperties.child">
                      <option value="">请选择子连杆</option>
                      <option v-for="[id, link] in links" :key="id" :value="id">
                        {{ link.properties.name }}
                      </option>
                    </select>
                  </div>
                </div>

                <div class="property-section">
                  <h4>位置和旋转</h4>
                  <div class="property-item">
                    <label>位置</label>
                    <div class="dimension-inputs">
                      <input 
                        type="number" 
                        v-model.number="jointProperties.position.x"
                        step="0.1"
                        placeholder="X"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                      <input 
                        type="number" 
                        v-model.number="jointProperties.position.y"
                        step="0.1"
                        placeholder="Y"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                      <input 
                        type="number" 
                        v-model.number="jointProperties.position.z"
                        step="0.1"
                        placeholder="Z"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                    </div>
                  </div>
                  <div class="property-item">
                    <label>旋转 (度)</label>
                    <div class="dimension-inputs">
                      <input 
                        type="number" 
                        v-model.number="jointProperties.rotation.roll"
                        step="1"
                        placeholder="Roll"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                      <input 
                        type="number" 
                        v-model.number="jointProperties.rotation.pitch"
                        step="1"
                        placeholder="Pitch"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                      <input 
                        type="number" 
                        v-model.number="jointProperties.rotation.yaw"
                        step="1"
                        placeholder="Yaw"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                    </div>
                  </div>
                </div>

                <div class="property-section">
                  <h4>运动属性</h4>
                  <div class="property-item">
                    <label>旋转轴</label>
                    <div class="dimension-inputs">
                      <input 
                        type="number" 
                        v-model.number="jointProperties.axis.x"
                        step="0.1"
                        placeholder="X"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                      <input 
                        type="number" 
                        v-model.number="jointProperties.axis.y"
                        step="0.1"
                        placeholder="Y"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                      <input 
                        type="number" 
                        v-model.number="jointProperties.axis.z"
                        step="0.1"
                        placeholder="Z"
                        :disabled="jointProperties.parent && jointProperties.child"
                      />
                    </div>
                  </div>
                  <div class="property-item">
                    <label>运动限制</label>
                    <div class="limit-inputs">
                      <div class="limit-item">
                        <label>下限</label>
                        <input 
                          type="number" 
                          v-model.number="jointProperties.limits.lower"
                          step="0.1"
                        />
                      </div>
                      <div class="limit-item">
                        <label>上限</label>
                        <input 
                          type="number" 
                          v-model.number="jointProperties.limits.upper"
                          step="0.1"
                        />
                      </div>
                      <div class="limit-item">
                        <label>力矩</label>
                        <input 
                          type="number" 
                          v-model.number="jointProperties.limits.effort"
                          step="1"
                        />
                      </div>
                      <div class="limit-item">
                        <label>速度</label>
                        <input 
                          type="number" 
                          v-model.number="jointProperties.limits.velocity"
                          step="0.1"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </template>

              <!-- 连杆属性 -->
              <template v-else>
                <!-- 基本属性 -->
                <div class="property-section">
                  <h4>基本属性</h4>
                  <div class="property-item">
                    <label>名称 <span class="required">*</span></label>
                    <input 
                      type="text" 
                      v-model="linkProperties.name"
                      placeholder="请输入名称"
                      :class="{ 'error': !linkProperties.name }"
                    />
                    <span class="error-message" v-if="!linkProperties.name">名称不能为空</span>
                  </div>
                  <div class="property-item">
                    <label>类型 <span class="required">*</span></label>
                    <select v-model="linkProperties.type">
                      <option value="box">长方体</option>
                      <option value="cylinder">圆柱体</option>
                      <option value="sphere">球体</option>
                      <option value="mesh">网格模型</option>
                    </select>
                  </div>
                </div>

                <!-- 几何属性 -->
                <div class="property-section">
                  <h4>几何属性</h4>
                  <div class="property-item">
                    <label>尺寸 <span class="required">*</span></label>
                    <div class="dimension-inputs">
                      <input 
                        type="number" 
                        v-model.number="linkProperties.dimensions.x"
                        step="0.1"
                        min="0.1"
                        placeholder="X"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.dimensions.y"
                        step="0.1"
                        min="0.1"
                        placeholder="Y"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.dimensions.z"
                        step="0.1"
                        min="0.1"
                        placeholder="Z"
                      />
                    </div>
                  </div>
                  <div class="property-item">
                    <label>位置</label>
                    <div class="dimension-inputs">
                      <input 
                        type="number" 
                        v-model.number="linkProperties.position.x"
                        step="0.1"
                        placeholder="X"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.position.y"
                        step="0.1"
                        placeholder="Y"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.position.z"
                        step="0.1"
                        placeholder="Z"
                      />
                    </div>
                  </div>
                  <div class="property-item">
                    <label>旋转 (度)</label>
                    <div class="dimension-inputs">
                      <input 
                        type="number" 
                        v-model.number="linkProperties.rotation.roll"
                        step="1"
                        placeholder="Roll"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.rotation.pitch"
                        step="1"
                        placeholder="Pitch"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.rotation.yaw"
                        step="1"
                        placeholder="Yaw"
                      />
                    </div>
                  </div>
                </div>

                <!-- 物理属性 -->
                <div class="property-section">
                  <h4>物理属性</h4>
                  <div class="property-item">
                    <label>质量 (kg)</label>
                    <input 
                      type="number" 
                      v-model.number="linkProperties.mass"
                      step="0.1"
                      min="0"
                    />
                  </div>
                  <div class="property-item">
                    <label>惯性矩阵</label>
                    <div class="inertia-inputs">
                      <input 
                        type="number" 
                        v-model.number="linkProperties.inertia.ixx"
                        step="0.1"
                        placeholder="Ixx"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.inertia.ixy"
                        step="0.1"
                        placeholder="Ixy"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.inertia.ixz"
                        step="0.1"
                        placeholder="Ixz"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.inertia.iyy"
                        step="0.1"
                        placeholder="Iyy"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.inertia.iyz"
                        step="0.1"
                        placeholder="Iyz"
                      />
                      <input 
                        type="number" 
                        v-model.number="linkProperties.inertia.izz"
                        step="0.1"
                        placeholder="Izz"
                      />
                    </div>
                  </div>
                </div>

                <!-- 碰撞属性 -->
                <div class="property-section">
                  <h4>碰撞属性</h4>
                  <div class="property-item">
                    <label>启用碰撞检测</label>
                    <input 
                      type="checkbox" 
                      v-model="linkProperties.collision.enabled"
                    />
                  </div>
                  <div v-if="linkProperties.collision.enabled" class="collision-properties">
                    <div class="property-item">
                      <label>碰撞类型</label>
                      <select v-model="linkProperties.collision.type">
                        <option value="box">长方体</option>
                        <option value="cylinder">圆柱体</option>
                        <option value="sphere">球体</option>
                      </select>
                    </div>
                    <div class="property-item">
                      <label>碰撞尺寸</label>
                      <div class="dimension-inputs">
                        <input 
                          type="number" 
                          v-model.number="linkProperties.collision.dimensions.x"
                          step="0.1"
                          min="0.1"
                          placeholder="X"
                        />
                        <input 
                          type="number" 
                          v-model.number="linkProperties.collision.dimensions.y"
                          step="0.1"
                          min="0.1"
                          placeholder="Y"
                        />
                        <input 
                          type="number" 
                          v-model.number="linkProperties.collision.dimensions.z"
                          step="0.1"
                          min="0.1"
                          placeholder="Z"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 材质属性 -->
                <div class="property-section">
                  <h4>材质属性</h4>
                  <div class="property-item">
                    <label>颜色</label>
                    <input 
                      type="color" 
                      v-model="linkProperties.color"
                    />
                  </div>
                  <div class="property-item">
                    <label>材质类型</label>
                    <select v-model="linkProperties.material.type">
                      <option value="default">默认</option>
                      <option value="metal">金属</option>
                      <option value="plastic">塑料</option>
                      <option value="rubber">橡胶</option>
                    </select>
                  </div>
                  <div class="property-item">
                    <label>纹理图片</label>
                    <input 
                      type="file" 
                      @change="handleTextureUpload"
                      accept="image/*"
                    />
                  </div>
                </div>
              </template>

              <div class="button-group">
                <button 
                  class="save-button" 
                  @click="saveProperties"
                  :disabled="!isValidProperties"
                >
                  保存
                </button>
                <button 
                  v-if="!isEditing && !isAddingJoint" 
                  class="delete-button" 
                  @click="deleteSelectedObject"
                >
                  删除
                </button>
                <button class="cancel-button" @click="cancelEdit">
                  取消
                </button>
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
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export default {
  name: 'CreateFile',
  components: {
    BackgroundLayout
  },
  data() {
    return {
      loading: false,
      isModeling: false,
      showGrid: true,
      selectedObject: null,
      showPropertyPanel: false,
      isEditing: false,
      isAddingJoint: false,
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
      joints: new Map() // 存储所有关节
    }
  },
  setup() {
    // 使用 setup 函数来创建非响应式的 Three.js 对象
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000)
    let renderer = null
    let controls = null
    let gridHelper = null
    let animationFrameId = null
    let links = new Map() // 存储所有连杆

    return {
      scene,
      camera,
      renderer,
      controls,
      gridHelper,
      animationFrameId,
      links
    }
  },
  methods: {
    goToHome() {
      this.$router.push('/')
    },
    initViewer() {
      try {
        // 设置场景背景
        this.scene.background = new THREE.Color(0x2a2a2a)

        // 创建相机
        const container = this.$refs.viewer
        const width = container.clientWidth
        const height = container.clientHeight
        this.camera.aspect = width / height
        this.camera.updateProjectionMatrix()
        this.camera.position.set(5, 5, 5)
        this.camera.lookAt(0, 0, 0)

        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ 
          antialias: true,
          alpha: true
        })
        this.renderer.setSize(width, height)
        this.renderer.setPixelRatio(window.devicePixelRatio)
        container.appendChild(this.renderer.domElement)

        // 添加控制器
        this.controls = new OrbitControls(this.camera, this.renderer.domElement)
        this.controls.enableDamping = true
        this.controls.dampingFactor = 0.05

        // 添加光源
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
        this.scene.add(ambientLight)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
        directionalLight.position.set(1, 1, 1)
        this.scene.add(directionalLight)

        // 添加网格和坐标轴
        this.gridHelper = new THREE.GridHelper(10, 10, 0x444444, 0x222222)
        this.scene.add(this.gridHelper)
        const axesHelper = new THREE.AxesHelper(5)
        this.scene.add(axesHelper)

        // 添加点击事件监听
        const raycaster = new THREE.Raycaster()
        const mouse = new THREE.Vector2()

        this.renderer.domElement.addEventListener('click', (event) => {
          // 计算鼠标在归一化设备坐标中的位置
          const rect = this.renderer.domElement.getBoundingClientRect()
          mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
          mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

          // 更新射线
          raycaster.setFromCamera(mouse, this.camera)

          // 获取所有连杆和关节的网格
          const meshes = [
            ...Array.from(this.links.values()).map(link => link.mesh),
            ...Array.from(this.joints.values()).map(joint => joint.mesh)
          ]
          
          // 检测射线与网格的交点
          const intersects = raycaster.intersectObjects(meshes, true)

          if (intersects.length > 0) {
            // 找到被点击的对象
            const clickedMesh = intersects[0].object
            // 如果点击的是线框，获取其父对象
            const targetMesh = clickedMesh.parent ? clickedMesh.parent : clickedMesh
            
            // 检查是否是关节
            const isJoint = Array.from(this.joints.values())
              .some(joint => joint.mesh === targetMesh)
            
            if (isJoint) {
              // 如果是关节，显示关节属性
              this.selectObject(targetMesh)
            } else {
              // 检查是否是连杆
              const isLink = Array.from(this.links.values())
                .some(link => link.mesh === targetMesh)
              
              if (isLink) {
                this.selectObject(targetMesh)
              } else {
                // 如果找不到对应的对象，取消选中
                this.deselectObject()
              }
            }
          } else {
            // 点击空白处取消选中
            this.deselectObject()
          }
        })

        // 开始动画循环
        this.animate()
        this.loading = false
      } catch (error) {
        console.error('Error initializing viewer:', error)
        this.loading = false
      }
    },
    animate() {
      if (!this.isModeling) return

      this.animationFrameId = requestAnimationFrame(this.animate)
      
      if (this.controls) {
        this.controls.update()
      }
      
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera)
      }
    },
    startModeling() {
      this.loading = true
      this.isModeling = true
      
      // 使用 nextTick 确保 DOM 更新后再初始化场景
      this.$nextTick(() => {
        try {
          this.initViewer()
        } catch (error) {
          console.error('Error in startModeling:', error)
          this.loading = false
        }
      })
    },
    resetView() {
      // 重置相机位置
      if (this.camera) {
        this.camera.position.set(5, 5, 5)
        this.camera.lookAt(0, 0, 0)
      }
      if (this.controls) {
        this.controls.reset()
      }

      // 清除所有连杆
      for (const [, link] of this.links) {
        if (link.mesh) {
          this.scene.remove(link.mesh)
          link.mesh.geometry.dispose()
          link.mesh.material.dispose()
          link.mesh.children.forEach(child => {
            child.geometry.dispose()
            child.material.dispose()
          })
        }
      }
      this.links.clear()

      // 清除所有关节
      for (const [, joint] of this.joints) {
        if (joint.mesh) {
          this.scene.remove(joint.mesh)
          joint.mesh.geometry.dispose()
          joint.mesh.material.dispose()
          joint.mesh.children.forEach(child => {
            child.geometry.dispose()
            child.material.dispose()
          })
        }
      }
      this.joints.clear()

      // 重置选中状态和属性面板
      this.selectedObject = null
      this.showPropertyPanel = false
      this.isEditing = false
      this.isAddingJoint = false
    },
    toggleGrid() {
      this.showGrid = !this.showGrid
      if (this.gridHelper) {
        this.gridHelper.visible = this.showGrid
      }
    },
    addLink() {
      this.showPropertyPanel = true
      this.isEditing = true
      this.resetLinkProperties()
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
  <!-- 添加材质 -->
  <material name="blue">
    <color rgba="0 0 0.8 1"/>
  </material>
  <material name="black">
    <color rgba="0 0 0 1"/>
  </material>
  <material name="red">
    <color rgba="0.8 0 0 1"/>
  </material>
`

      // 添加所有连杆
      for (const [, link] of this.links) {
        const props = link.properties
        urdf += `  <!-- ${props.name} -->
  <link name="${props.name}">
    <visual>
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
      <material name="${props.color === '#9f6bff' ? 'blue' : 'black'}"/>
    </visual>
    <collision>
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
            rpy="${THREE.MathUtils.degToRad(props.rotation.roll)} ${THREE.MathUtils.degToRad(props.rotation.pitch)} ${THREE.MathUtils.degToRad(props.rotation.yaw)}"/>
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
    handleResize() {
      if (this.$refs.viewer && this.camera && this.renderer) {
        const width = this.$refs.viewer.clientWidth
        const height = this.$refs.viewer.clientHeight
        this.camera.aspect = width / height
        this.camera.updateProjectionMatrix()
        this.renderer.setSize(width, height)
      }
    },
    createLink() {
      // 根据类型创建不同的几何体
      let geometry;
      switch (this.linkProperties.type) {
        case 'box':
          geometry = new THREE.BoxGeometry(
            this.linkProperties.dimensions.x,
            this.linkProperties.dimensions.y,
            this.linkProperties.dimensions.z
          );
          break;
        case 'cylinder':
          geometry = new THREE.CylinderGeometry(
            this.linkProperties.dimensions.x/2,
            this.linkProperties.dimensions.x/2,
            this.linkProperties.dimensions.y,
            32
          );
          break;
        case 'sphere':
          geometry = new THREE.SphereGeometry(
            this.linkProperties.dimensions.x/2,
            32,
            32
          );
          break;
        default:
          geometry = new THREE.BoxGeometry(1, 1, 1);
      }

      const material = new THREE.MeshPhongMaterial({ 
        color: this.linkProperties.color,
        transparent: true,
        opacity: 0.8,
        metalness: 0.5,
        roughness: 0.5,
        envMapIntensity: 1.0
      });
      const mesh = new THREE.Mesh(geometry, material);
      const linkName = `link_${this.links.size + 1}`;
      mesh.name = linkName;
      this.scene.add(mesh);
      this.links.set(linkName, { mesh, properties: { ...this.linkProperties } });
      this.selectObject(mesh);
    },
    
    createLinkGeometry() {
      const { x, y, z } = this.linkProperties.dimensions
      
      switch (this.linkProperties.type) {
        case 'box':
          return new THREE.BoxGeometry(x, y, z)
        case 'cylinder':
          return new THREE.CylinderGeometry(x/2, x/2, y, 32)
        case 'sphere':
          return new THREE.SphereGeometry(x/2, 32, 32)
        default:
          return new THREE.BoxGeometry(x, y, z)
      }
    },
    
    selectObject(object) {
      // 取消之前选中对象的高亮
      if (this.selectedObject) {
        if (this.selectedObject.startsWith('joint_')) {
          const prevJoint = this.joints.get(this.selectedObject)
          if (prevJoint && prevJoint.mesh) {
            prevJoint.mesh.material.emissive.setHex(0x000000)
            prevJoint.mesh.material.emissiveIntensity = 0
          }
        } else {
          const prevLink = this.links.get(this.selectedObject)
          if (prevLink && prevLink.mesh) {
            prevLink.mesh.material.emissive.setHex(0x000000)
            prevLink.mesh.material.emissiveIntensity = 0
          }
        }
      }
      
      // 高亮新选中的对象
      this.selectedObject = object.name
      if (object && object.material) {
        object.material.emissive.setHex(0x9f6bff)
        object.material.emissiveIntensity = 0.2
      }
      
      // 更新属性面板
      if (object.name.startsWith('joint_')) {
        if (this.joints.has(object.name)) {
          this.jointProperties = { ...this.joints.get(object.name).properties }
          this.showPropertyPanel = true
          this.isEditing = false
          this.isAddingJoint = false
        }
      } else if (this.links.has(object.name)) {
        this.linkProperties = { ...this.links.get(object.name).properties }
        this.showPropertyPanel = true
        this.isEditing = false
      }
    },
    
    deselectObject() {
      if (this.selectedObject) {
        if (this.selectedObject.startsWith('joint_')) {
          const joint = this.joints.get(this.selectedObject)
          if (joint && joint.mesh) {
            joint.mesh.material.emissive.setHex(0x000000)
            joint.mesh.material.emissiveIntensity = 0
          }
        } else {
          const link = this.links.get(this.selectedObject)
          if (link && link.mesh) {
            link.mesh.material.emissive.setHex(0x000000)
            link.mesh.material.emissiveIntensity = 0
          }
        }
        this.selectedObject = null
        this.showPropertyPanel = false
      }
    },

    deleteSelectedObject() {
      if (this.selectedObject) {
        if (this.selectedObject.startsWith('joint_')) {
          // 删除关节
          if (this.joints.has(this.selectedObject)) {
            const joint = this.joints.get(this.selectedObject)
            
            // 删除连接线
            if (joint.mesh.userData.connectionLine) {
              this.scene.remove(joint.mesh.userData.connectionLine)
              joint.mesh.userData.connectionLine.geometry.dispose()
              joint.mesh.userData.connectionLine.material.dispose()
            }
            
            // 从场景中移除
            this.scene.remove(joint.mesh)
            
            // 释放资源
            joint.mesh.geometry.dispose()
            joint.mesh.material.dispose()
            joint.mesh.children.forEach(child => {
              child.geometry.dispose()
              child.material.dispose()
            })
            
            // 从存储中移除
            this.joints.delete(this.selectedObject)
          }
        } else {
          // 删除连杆
          if (this.links.has(this.selectedObject)) {
            const link = this.links.get(this.selectedObject)
            
            // 从场景中移除
            this.scene.remove(link.mesh)
            
            // 释放资源
            link.mesh.geometry.dispose()
            link.mesh.material.dispose()
            link.mesh.children.forEach(child => {
              child.geometry.dispose()
              child.material.dispose()
            })
            
            // 从存储中移除
            this.links.delete(this.selectedObject)
          }
        }
        
        // 重置选中状态
        this.selectedObject = null
        this.showPropertyPanel = false
      }
    },
    
    updateLinkProperties() {
      if (!this.selectedObject || !this.links.has(this.selectedObject)) return
      
      const link = this.links.get(this.selectedObject)
      const oldMesh = link.mesh
      
      // 创建新的几何体
      const geometry = this.createLinkGeometry()
      const material = new THREE.MeshPhongMaterial({
        color: this.linkProperties.color,
        transparent: true,
        opacity: 0.8,
        metalness: 0.5,
        roughness: 0.5
      })
      
      // 创建新的网格
      const newMesh = new THREE.Mesh(geometry, material)
      
      // 复制位置和旋转
      newMesh.position.copy(oldMesh.position)
      newMesh.rotation.copy(oldMesh.rotation)
      
      // 添加线框
      const wireframe = new THREE.LineSegments(
        new THREE.WireframeGeometry(geometry),
        new THREE.LineBasicMaterial({
          color: 0x9f6bff,
          transparent: true,
          opacity: 0.3
        })
      )
      newMesh.add(wireframe)
      
      // 更新场景
      this.scene.remove(oldMesh)
      this.scene.add(newMesh)
      
      // 更新存储
      this.links.set(this.selectedObject, {
        mesh: newMesh,
        properties: { ...this.linkProperties }
      })
      
      // 重新选中
      this.selectObject(newMesh)
    },
    
    isValidProperties() {
      if (this.isAddingJoint) {
        return this.jointProperties.name.trim() !== '' &&
               this.jointProperties.parent !== '' &&
               this.jointProperties.child !== '';
      }
      return this.linkProperties.name.trim() !== '' &&
             this.linkProperties.dimensions.x > 0 &&
             this.linkProperties.dimensions.y > 0 &&
             this.linkProperties.dimensions.z > 0;
    },
    
    handleTextureUpload(event) {
      const file = event.target.files[0];
      if (file) {
        // 这里可以添加文件上传和处理的逻辑
        console.log('Texture file selected:', file.name);
      }
    },
    
    resetLinkProperties() {
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
      }
    },
    createJoint() {
      const geometry = new THREE.CylinderGeometry(0.1, 0.1, 0.2, 32)
      const material = new THREE.MeshPhongMaterial({ 
        color: 0xff6b6b,
        transparent: true,
        opacity: 0.8,
        metalness: 0.5,
        roughness: 0.5,
        envMapIntensity: 1.0
      })
      const mesh = new THREE.Mesh(geometry, material)
      const jointName = `joint_${this.joints.size + 1}`
      mesh.name = jointName
      this.scene.add(mesh)
      this.joints.set(jointName, { mesh, properties: { ...this.jointProperties } })
      this.selectObject(mesh)
    },
    saveProperties() {
      if (this.isAddingJoint) {
        // 创建新的关节
        this.createJoint()
      } else if (this.isEditing) {
        // 创建新的连杆
        this.createLink()
      } else if (this.selectedObject) {
        // 更新现有对象
        if (this.selectedObject.startsWith('joint_')) {
          this.updateJointProperties()
        } else {
          this.updateLinkProperties()
        }
      }
      
      // 关闭属性面板
      this.showPropertyPanel = false
      this.isEditing = false
      this.isAddingJoint = false
      this.resetLinkProperties()
      this.resetJointProperties()
    },
    cancelEdit() {
      this.showPropertyPanel = false
      this.isEditing = false
      this.isAddingJoint = false
      this.resetLinkProperties()
      this.resetJointProperties()
    },
    updateJointProperties() {
      if (!this.selectedObject || !this.joints.has(this.selectedObject)) return
      
      const joint = this.joints.get(this.selectedObject)
      const oldMesh = joint.mesh
      
      // 创建新的几何体
      const geometry = new THREE.CylinderGeometry(0.1, 0.1, 0.2, 32)
      const material = new THREE.MeshPhongMaterial({
        color: 0xff6b6b,
        transparent: true,
        opacity: 0.8,
        metalness: 0.5,
        roughness: 0.5
      })
      
      // 创建新的网格
      const newMesh = new THREE.Mesh(geometry, material)
      
      // 复制位置和旋转
      newMesh.position.copy(oldMesh.position)
      newMesh.rotation.copy(oldMesh.rotation)
      
      // 添加线框
      const wireframe = new THREE.LineSegments(
        new THREE.WireframeGeometry(geometry),
        new THREE.LineBasicMaterial({
          color: 0xff6b6b,
          transparent: true,
          opacity: 0.3
        })
      )
      newMesh.add(wireframe)
      
      // 添加旋转轴指示器
      const axisGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.5, 8)
      const axisMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        transparent: true,
        opacity: 0.5
      })
      const axisMesh = new THREE.Mesh(axisGeometry, axisMaterial)
      axisMesh.rotation.x = Math.PI / 2
      newMesh.add(axisMesh)
      
      // 更新场景
      this.scene.remove(oldMesh)
      this.scene.add(newMesh)
      
      // 更新存储
      this.joints.set(this.selectedObject, {
        mesh: newMesh,
        properties: { ...this.jointProperties }
      })
      
      // 重新选中
      this.selectObject(newMesh)
    },
    calculateJointProperties() {
      if (!this.jointProperties.parent || !this.jointProperties.child) return
      
      const parentLink = this.links.get(this.jointProperties.parent)
      const childLink = this.links.get(this.jointProperties.child)
      
      if (!parentLink || !childLink) return
      
      // 获取父连杆的末端位置
      const parentEnd = new THREE.Vector3()
      parentLink.mesh.getWorldPosition(parentEnd)
      
      // 获取子连杆的起始位置
      const childStart = new THREE.Vector3()
      childLink.mesh.getWorldPosition(childStart)
      
      // 计算连接方向向量
      const direction = new THREE.Vector3()
      direction.subVectors(childStart, parentEnd).normalize()
      
      // 设置关节位置为父连杆末端
      this.jointProperties.position = {
        x: parentEnd.x,
        y: parentEnd.y,
        z: parentEnd.z
      }
      
      // 根据关节类型设置旋转轴
      switch (this.jointProperties.type) {
        case 'revolute':
        case 'continuous':
          // 对于旋转关节，旋转轴应该垂直于连接方向
          // 这里我们使用一个简单的启发式方法：如果连接方向接近垂直，使用X轴；否则使用Y轴
          if (Math.abs(direction.y) > 0.9) {
            this.jointProperties.axis = { x: 1, y: 0, z: 0 }
          } else {
            this.jointProperties.axis = { x: 0, y: 1, z: 0 }
          }
          break
          
        case 'prismatic':
          // 对于移动关节，移动轴应该沿着连接方向
          this.jointProperties.axis = {
            x: direction.x,
            y: direction.y,
            z: direction.z
          }
          break
          
        case 'fixed':
          // 固定关节不需要设置旋转轴
          this.jointProperties.axis = { x: 0, y: 0, z: 0 }
          break
      }
      
      // 计算关节的旋转角度，使关节的Z轴与连接方向对齐
      const zAxis = new THREE.Vector3(0, 0, 1)
      const rotationAxis = new THREE.Vector3()
      rotationAxis.crossVectors(zAxis, direction).normalize()
      const angle = Math.acos(zAxis.dot(direction))
      
      // 将旋转角度转换为欧拉角
      const euler = new THREE.Euler()
      euler.setFromQuaternion(new THREE.Quaternion().setFromAxisAngle(rotationAxis, angle))
      
      this.jointProperties.rotation = {
        roll: THREE.MathUtils.radToDeg(euler.x),
        pitch: THREE.MathUtils.radToDeg(euler.y),
        yaw: THREE.MathUtils.radToDeg(euler.z)
      }
    },
    watch: {
      'jointProperties.parent': function() {
        if (this.jointProperties.parent && this.jointProperties.child) {
          this.calculateJointProperties()
        }
      },
      'jointProperties.child': function() {
        if (this.jointProperties.parent && this.jointProperties.child) {
          this.calculateJointProperties()
        }
      },
      'jointProperties.type': function() {
        if (this.jointProperties.parent && this.jointProperties.child) {
          this.calculateJointProperties()
        }
      }
    }
  },
  mounted() {
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId)
    }
    if (this.renderer) {
      this.renderer.dispose()
      this.renderer.forceContextLoss()
      this.renderer.domElement.remove()
    }
    if (this.controls) {
      this.controls.dispose()
    }
    if (this.scene) {
      this.scene.clear()
    }
    this.isModeling = false
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
}

.viewer {
  width: 100%;
  height: 100%;
}

.start-prompt {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(159, 107, 255, 0.05);
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

.properties-panel {
  width: 300px;
  background: rgba(10, 10, 26, 0.4);
  border: 1px solid rgba(159, 107, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(159, 107, 255, 0.1);
  backdrop-filter: blur(5px);
  animation: slideIn 0.3s ease-out;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
}

.panel-section {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
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
  background: rgba(10, 10, 26, 0.9);
  padding: 15px 20px;
  border-bottom: 1px solid rgba(159, 107, 255, 0.2);
  z-index: 1;
  backdrop-filter: blur(5px);
}

.button-group {
  position: sticky;
  bottom: 0;
  background: rgba(10, 10, 26, 0.9);
  padding: 15px 20px;
  border-top: 1px solid rgba(159, 107, 255, 0.2);
  z-index: 1;
  backdrop-filter: blur(5px);
}

.property-section {
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(159, 107, 255, 0.05);
  border-radius: 8px;
  position: relative;
}

.property-section:last-child {
  margin-bottom: 0;
}

.panel-section h3 {
  color: #d8b5ff;
  font-size: 16px;
  margin-bottom: 10px;
  font-family: 'Orbitron', sans-serif;
}

.property-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.property-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.property-item label {
  color: #d8b5ff;
  font-size: 14px;
}

.property-item input,
.property-item select {
  background: rgba(159, 107, 255, 0.1);
  border: 1px solid rgba(216, 181, 255, 0.3);
  border-radius: 4px;
  padding: 8px;
  color: #d8b5ff;
  font-size: 14px;
}

.property-item input:focus,
.property-item select:focus {
  outline: none;
  border-color: rgba(216, 181, 255, 0.8);
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
}

.dimension-inputs {
  display: flex;
  gap: 8px;
}

.dimension-inputs input {
  flex: 1;
  text-align: center;
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

.close-button {
  background: none;
  border: none;
  color: #d8b5ff;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: all 0.3s ease;
}

.close-button:hover {
  color: #9f6bff;
  transform: scale(1.1);
}

.save-button,
.cancel-button {
  flex: 1;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(216, 181, 255, 0.5);
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

.property-section h4 {
  color: #d8b5ff;
  font-size: 14px;
  margin-bottom: 15px;
  font-family: 'Orbitron', sans-serif;
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
  gap: 8px;
}

.collision-properties {
  margin-top: 10px;
  padding: 10px;
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
</style> 