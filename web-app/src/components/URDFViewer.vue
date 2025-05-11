<!-- URDFViewer.vue -->
<template>
  <div class="urdf-viewer-container">
    <div ref="viewerContainer" class="viewer-container"></div>
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">Loading URDF Model...</div>
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
/* eslint-disable no-undef */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as THREE from 'three'
import URDFLoader from 'urdf-loader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export default {
  name: 'URDFViewer',
  props: {
    urdfUrl: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const viewerContainer = ref(null)
    const loading = ref(true)
    const error = ref(null)
    let scene, camera, renderer, controls, robot, animationId

    // 卸载旧模型
    const clearScene = () => {
      if (scene && robot) {
        scene.remove(robot)
        robot.traverse(obj => {
          if (obj.geometry) obj.geometry.dispose()
          if (obj.material) {
            if (Array.isArray(obj.material)) {
              obj.material.forEach(m => m.dispose())
            } else {
              obj.material.dispose()
            }
          }
        })
        robot = null
      }
      if (renderer && renderer.domElement && viewerContainer.value) {
        viewerContainer.value.removeChild(renderer.domElement)
      }
      if (animationId) {
        cancelAnimationFrame(animationId)
        animationId = null
      }
    }

    // 初始化Three.js场景和渲染
    const initViewer = async () => {
      try {
        console.log('Starting URDF viewer initialization...')
        loading.value = true
        error.value = null
        clearScene()

        console.log('Creating Three.js scene...')
        // 创建场景
        scene = new THREE.Scene()
        scene.background = new THREE.Color(0x2a2a2a)

        console.log('Setting up camera...')
        // 创建相机
        camera = new THREE.PerspectiveCamera(
          75,
          viewerContainer.value.clientWidth / viewerContainer.value.clientHeight,
          0.1,
          1000
        )
        camera.position.set(2, 2, 2)

        console.log('Initializing renderer...')
        // 创建渲染器
        renderer = new THREE.WebGLRenderer({ antialias: true })
        renderer.setSize(viewerContainer.value.clientWidth, viewerContainer.value.clientHeight)
        viewerContainer.value.appendChild(renderer.domElement)

        console.log('Setting up controls...')
        // 添加控制器
        controls = new OrbitControls(camera, renderer.domElement)
        controls.enableDamping = true
        controls.dampingFactor = 0.05

        console.log('Adding lights...')
        // 添加光源
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
        scene.add(ambientLight)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
        directionalLight.position.set(1, 1, 1)
        scene.add(directionalLight)

        console.log('Starting URDF model loading...')
        // 加载URDF模型
        const loader = new URDFLoader()
        console.log('URDFLoader instance created')
        
        robot = await new Promise((resolve, reject) => {
          const url = props.urdfUrl + '/content'
          console.log('Attempting to fetch URDF content from URL:', url)
          // 从后端获取 URDF 内容
          fetch(url)
            .then(response => {
              console.log('Received response:', response.status, response.statusText)
              if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
              }
              return response.json()
            })
            .then(data => {
              console.log('Successfully fetched URDF content from backend')
              console.log('URDF content length:', data.content.length)
              
              // 创建一个 Blob URL
              const blob = new Blob([data.content], { type: 'text/xml' })
              const blobUrl = URL.createObjectURL(blob)
              console.log('Created Blob URL:', blobUrl)
              
              // 使用 Blob URL 加载模型
              console.log('Starting URDF model parsing...')
              loader.load(
                blobUrl,
                (robot) => {
                  console.log('Successfully loaded URDF model')
                  // 清理 Blob URL
                  URL.revokeObjectURL(blobUrl)
                  resolve(robot)
                },
                undefined,
                (err) => {
                  console.error('Error loading URDF model:', err)
                  // 清理 Blob URL
                  URL.revokeObjectURL(blobUrl)
                  reject(err)
                }
              )
            })
            .catch(err => {
              console.error('Error fetching URDF content:', err)
              reject(err)
            })
        })
        console.log('Adding robot to scene...')
        scene.add(robot)

        // 设置相机位置
        console.log('Setting up camera position...')
        const box = new THREE.Box3().setFromObject(robot)
        const center = box.getCenter(new THREE.Vector3())
        const size = box.getSize(new THREE.Vector3())
        const maxDim = Math.max(size.x, size.y, size.z)
        const fov = camera.fov * (Math.PI / 180)
        let cameraZ = Math.abs(maxDim / Math.sin(fov / 2))
        camera.position.set(center.x + cameraZ, center.y + cameraZ, center.z + cameraZ)
        camera.lookAt(center)
        controls.target.copy(center)

        loading.value = false
        console.log('URDF viewer initialization completed')
        animate()
      } catch (err) {
        console.error('URDF viewer initialization failed:', err)
        error.value = `Error loading URDF model: ${err.message}`
        loading.value = false
      }
    }

    // 动画循环
    const animate = () => {
      animationId = requestAnimationFrame(animate)
      controls.update()
      renderer.render(scene, camera)
    }

    // 窗口自适应
    const handleResize = () => {
      if (!viewerContainer.value || !camera || !renderer) return
      const width = viewerContainer.value.clientWidth
      const height = viewerContainer.value.clientHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }

    onMounted(() => {
      initViewer()
      window.addEventListener('resize', handleResize)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
      clearScene()
      if (renderer) {
        renderer.dispose()
      }
      if (controls) {
        controls.dispose()
      }
    })

    // 监听urdfUrl变化，切换文件时重新加载
    watch(() => props.urdfUrl, () => {
      initViewer()
    })

    return {
      viewerContainer,
      loading,
      error
    }
  }
}
</script>

<style scoped>
.urdf-viewer-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.viewer-container {
  width: 100%;
  height: 100%;
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

.error-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ff6b6b;
  text-align: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style> 