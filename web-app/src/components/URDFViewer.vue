<!-- URDFViewer.vue -->
<template>
  <div class="urdf-viewer-container">
    <div ref="viewerContainer" class="viewer-container"></div>
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">Loading URDF Model...</div>
    </div>
    <div v-if="error" class="error-overlay">
      <div class="error-content">
        <div class="error-header">
          <i class="error-icon">!</i>
          <h3>URDF 文件错误</h3>
        </div>
        <div class="error-message">{{ error }}</div>
        <button class="close-button" @click="error = null">
          <span>关闭</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable no-undef */
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as THREE from 'three'
import URDFLoader from 'urdf-loader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import { ColladaLoader } from 'three/examples/jsm/loaders/ColladaLoader.js'

export default {
  name: 'URDFViewer',
  props: {
    urdfUrl: {
      type: String,
      default: null
    },
    urdfContent: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const viewerContainer = ref(null)
    const loading = ref(true)
    const error = ref(null)
    let scene, camera, renderer, controls, robot, animationId
    let frameCount = 0

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
      
      if (renderer && renderer.domElement) {
        try {
          if (renderer.domElement.parentNode === viewerContainer.value) {
            viewerContainer.value.removeChild(renderer.domElement)
          }
          renderer.dispose()
          renderer = null
        } catch (error) {
          console.warn('Error while cleaning up renderer:', error)
        }
      }

      if (animationId) {
        cancelAnimationFrame(animationId)
        animationId = null
      }

      if (scene) {
        scene.traverse(obj => {
          if (obj.geometry) obj.geometry.dispose()
          if (obj.material) {
            if (Array.isArray(obj.material)) {
              obj.material.forEach(m => m.dispose())
            } else {
              obj.material.dispose()
            }
          }
        })
        scene = null
      }

      if (controls) {
        controls.dispose()
        controls = null
      }

      camera = null

      if (viewerContainer.value) {
        viewerContainer.value.innerHTML = ''
      }
    }

    // 从 URL 加载 URDF
    const loadFromUrl = async (url) => {
      try {
        const response = await fetch(url + '/urdf')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        if (!data.content) {
          throw new Error('URDF content is empty')
        }
        return data.content
      } catch (err) {
        throw new Error(`Failed to load URDF from URL: ${err.message}`)
      }
    }

    // 修改初始化方法
    const initViewer = async () => {
      try {
        console.log('Starting URDF viewer initialization...')
        loading.value = true
        error.value = null
        
        if (scene) {
          clearScene()
        }

        scene = new THREE.Scene()
        scene.background = new THREE.Color(0x303030)
        console.log('Scene created')

        if (!viewerContainer.value) {
          throw new Error('Viewer container not mounted')
        }

        const containerWidth = viewerContainer.value.clientWidth
        const containerHeight = viewerContainer.value.clientHeight

        if (containerWidth === 0 || containerHeight === 0) {
          throw new Error('Container has zero dimensions')
        }

        camera = new THREE.PerspectiveCamera(
          75,
          containerWidth / containerHeight,
          0.1,
          1000
        )
        camera.position.set(2, 2, 2)
        camera.lookAt(0, 0, 0)
        console.log('Camera created with position:', camera.position.toArray())

        renderer = new THREE.WebGLRenderer({ 
          antialias: true,
          alpha: true
        })
        renderer.setSize(containerWidth, containerHeight)
        renderer.setPixelRatio(window.devicePixelRatio)
        viewerContainer.value.appendChild(renderer.domElement)
        console.log('Renderer created')

        controls = new OrbitControls(camera, renderer.domElement)
        controls.enableDamping = true
        controls.dampingFactor = 0.05
        controls.screenSpacePanning = true
        controls.minDistance = 1
        controls.maxDistance = 10
        controls.target.set(0, 1, 0)
        console.log('Controls created')

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7)
        scene.add(ambientLight)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0)
        directionalLight.position.set(5, 5, 5)
        scene.add(directionalLight)
        console.log('Lights added')

        const gridHelper = new THREE.GridHelper(10, 10, 0x888888, 0x444444)
        scene.add(gridHelper)
        const axesHelper = new THREE.AxesHelper(5)
        scene.add(axesHelper)
        console.log('Helpers added')

        const render = () => {
          animationId = requestAnimationFrame(render)
          if (controls) {
            controls.update()
          }
          if (renderer && scene && camera) {
            if (frameCount % 100 === 0) {
              console.log('Render state:', {
                cameraPosition: camera.position.toArray(),
                cameraRotation: camera.rotation.toArray(),
                robotVisible: robot ? robot.visible : 'no robot',
                sceneChildren: scene.children.length
              })
            }
            frameCount++
            renderer.render(scene, camera)
          }
        }

        render()
        console.log('Render loop started')

        viewerContainer.value.style.position = 'relative'
        viewerContainer.value.style.overflow = 'hidden'
        console.log('Container styles set')

        renderer.render(scene, camera)

        console.log('Starting URDF model loading...')
        const loader = new URDFLoader()
        console.log('URDFLoader instance created')
        
        // 获取 URDF 内容
        let urdfContent
        if (props.urdfContent) {
          urdfContent = props.urdfContent
        } else if (props.urdfUrl) {
          urdfContent = await loadFromUrl(props.urdfUrl)
        } else {
          throw new Error('Neither URDF content nor URL provided')
        }

        robot = await new Promise((resolve, reject) => {
          try {
            const blob = new Blob([urdfContent], { type: 'text/xml' })
            const blobUrl = URL.createObjectURL(blob)
            
            loader.packages = ''
            
            // 恢复mesh加载回调
            loader.loadMeshCb = (path, manager, done) => {
              console.log('Loading mesh:', path)
              
              let resourcePath = path
              
              if (resourcePath.startsWith('package://')) {
                resourcePath = resourcePath.replace(/^package:\/\/[^/]+\//, '')
              }
              
              const resourceMatch = resourcePath.match(/\/api\/files\/resource\/(.+)/)
              if (resourceMatch) {
                resourcePath = resourceMatch[1]
              }
              
              if (resourcePath.includes('blob:')) {
                const blobMatch = resourcePath.match(/\/\/[^/]*\/(.+)/)
                if (blobMatch) {
                  resourcePath = blobMatch[1]
                }
              }
              
              const meshUrl = `http://localhost:5000/api/files/resource/${resourcePath}`
              const fileExtension = resourcePath.split('.').pop().toLowerCase()
              
              if (fileExtension === 'dae') {
                const colladaLoader = new ColladaLoader(manager)
                colladaLoader.load(
                  meshUrl,
                  (collada) => {
                    const mesh = collada.scene
                    mesh.traverse((child) => {
                      if (child.isMesh) {
                        child.castShadow = true
                        child.receiveShadow = true
                      }
                    })
                    done(mesh)
                  },
                  undefined,
                  (error) => {
                    console.error('Collada加载错误:', error)
                    done(null, error)
                  }
                )
              } else if (fileExtension === 'stl') {
                const meshLoader = new STLLoader(manager)
                meshLoader.load(
                  meshUrl,
                  (geometry) => {
                    geometry.computeVertexNormals()
                    
                    const material = new THREE.MeshPhongMaterial({
                      color: 0x7a7a7a,
                      shininess: 100,
                      specular: 0x111111,
                      emissive: 0x000000,
                      flatShading: false
                    })
                    
                    const mesh = new THREE.Mesh(geometry, material)
                    mesh.castShadow = true
                    mesh.receiveShadow = true
                    
                    done(mesh)
                  },
                  undefined,
                  (error) => {
                    console.error('STL加载错误:', error)
                    done(null, error)
                  }
                )
              } else {
                done(null, new Error(`不支持的文件格式: ${fileExtension}`))
              }
            }
            
            loader.load(
              blobUrl,
              (robot) => {
                try {
                  scene.add(robot)
                  
                  // 调整相机视角
                  const box = new THREE.Box3().setFromObject(robot)
                  const size = box.getSize(new THREE.Vector3())
                  const center = box.getCenter(new THREE.Vector3())
                  
                  const maxDim = Math.max(size.x, size.y, size.z)
                  const fov = camera.fov * (Math.PI / 180)
                  const cameraZ = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5
                  
                  camera.position.set(cameraZ, cameraZ, cameraZ)
                  camera.lookAt(center)
                  
                  if (controls) {
                    controls.target.copy(center)
                    controls.update()
                  }

                  resolve(robot)
                } catch (err) {
                  reject(new Error(`模型加载后处理失败: ${err.message}`))
                } finally {
                  URL.revokeObjectURL(blobUrl)
                }
              },
              undefined,
              (err) => {
                URL.revokeObjectURL(blobUrl)
                reject(new Error(`URDF解析错误: ${err.message}`))
              }
            )
          } catch (err) {
            reject(new Error(`URDF加载失败: ${err.message}`))
          }
        })

        loading.value = false
        console.log('URDF loading completed')

      } catch (err) {
        console.error('Scene initialization failed:', err)
        error.value = `URDF文件错误:\n\n${err.message}\n\n请检查文件格式是否正确，以及是否包含所有必要的链接和关节定义。`
        loading.value = false
      }
    }

    // 监听属性变化
    watch([() => props.urdfContent, () => props.urdfUrl], ([newContent, newUrl]) => {
      if (!newContent && !newUrl) {
        clearScene()
      } else {
        error.value = null
        loading.value = true
        
        initViewer().catch(err => {
          console.error('Failed to initialize viewer:', err)
          error.value = `Failed to initialize viewer: ${err.message}`
          loading.value = false
        })
      }
    }, { immediate: true })

    onBeforeUnmount(() => {
      console.log('Component unmounting, cleaning up...')
      clearScene()
    })

    const cleanup = () => {
      clearScene()
    }

    const handleResize = () => {
      if (!viewerContainer.value || !camera || !renderer) return
      console.log('Handling resize')
      const width = viewerContainer.value.clientWidth
      const height = viewerContainer.value.clientHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }

    onMounted(() => {
      console.log('Component mounted')
      window.addEventListener('resize', handleResize)
      initViewer()
    })

    return {
      viewerContainer,
      loading,
      error,
      cleanup,
      scene,
      camera,
      controls
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

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(18, 18, 18, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.error-content {
  background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
  padding: 30px;
  border-radius: 16px;
  max-width: 80%;
  max-height: 80%;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(216, 181, 255, 0.1);
  animation: slideIn 0.3s ease-out;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(216, 181, 255, 0.1);
}

.error-icon {
  width: 32px;
  height: 32px;
  background: #d8b5ff;
  color: #1a1a1a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 20px;
}

.error-content h3 {
  color: #d8b5ff;
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.error-message {
  color: #e0e0e0;
  font-family: 'Consolas', monospace;
  white-space: pre-wrap;
  background: rgba(216, 181, 255, 0.05);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 25px;
  font-size: 14px;
  line-height: 1.6;
  border: 1px solid rgba(216, 181, 255, 0.1);
}

.close-button {
  display: block;
  width: 100%;
  padding: 12px;
  background: linear-gradient(145deg, #d8b5ff, #b392d8);
  color: #1a1a1a;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.close-button:hover {
  background: linear-gradient(145deg, #e0c3ff, #c9a8ef);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(216, 181, 255, 0.3);
}

.close-button:active {
  transform: translateY(1px);
}

.close-button span {
  position: relative;
  z-index: 1;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-content::-webkit-scrollbar {
  width: 8px;
}

.error-content::-webkit-scrollbar-track {
  background: rgba(216, 181, 255, 0.05);
  border-radius: 4px;
}

.error-content::-webkit-scrollbar-thumb {
  background: rgba(216, 181, 255, 0.2);
  border-radius: 4px;
}

.error-content::-webkit-scrollbar-thumb:hover {
  background: rgba(216, 181, 255, 0.3);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style> 