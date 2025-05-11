<!-- views/FileBrowser.vue -->
<template>
  <BackgroundLayout>
    <div class="file-browser">
      <button class="home-button" @click="goToHome">
        Back to Home
      </button>
      <div class="file-list">
        <div class="files-container">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="error" class="error">{{ error }}</div>
          <div v-else-if="files.length === 0" class="no-files">暂无文件</div>
          <div v-else class="file-grid">
            <div v-for="file in files" :key="file.name" class="file-item" @click="handleFileClick(file)">
              <div class="file-icon">📄</div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-details">
                  <span>{{ formatFileSize(file.size) }}</span>
                  <span>{{ formatDate(file.modified) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="pagination">
          <button 
            class="cyber-button" 
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            上一页
          </button>
          <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
          <button 
            class="cyber-button" 
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            下一页
          </button>
        </div>
      </div>
      <div class="divider"></div>
      <div class="content-area">
        <div v-if="selectedFile" class="file-preview">
          <h3>Selected File: {{ selectedFile.name }}</h3>
          <div v-if="visualizationStatus" class="status-message">
            {{ visualizationStatus }}
          </div>
          <div v-if="showUrdfViewer" class="visualization-container">
            <URDFViewer 
              :urdfUrl="`http://localhost:5000/api/files/${selectedFile.name}`"
            />
          </div>
          <button 
            v-if="isVisualizationRunning" 
            class="cyber-button stop-button" 
            @click="stopVisualization"
          >
            Stop Visualization
          </button>
        </div>
      </div>
    </div>
  </BackgroundLayout>
</template>

<script>
import BackgroundLayout from '@/components/BackgroundLayout.vue'
import URDFViewer from '@/components/URDFViewer.vue'

export default {
  name: 'FileBrowser',
  components: {
    BackgroundLayout,
    URDFViewer
  },
  data() {
    return {
      files: [],
      currentPage: 1,
      totalPages: 1,
      loading: false,
      error: null,
      selectedFile: null,
      visualizationStatus: null,
      isVisualizationRunning: false,
      visualizationUrl: 'http://127.0.0.1:7777',
      retryCount: 0,
      maxRetries: 5,
      showUrdfViewer: false
    }
  },
  methods: {
    async fetchFiles() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch(`http://localhost:5000/api/files/list?page=${this.currentPage}&per_page=20`)
        const data = await response.json()
        if (response.ok) {
          this.files = data.files
          this.totalPages = data.total_pages
        } else {
          this.error = data.error || '获取文件列表失败'
        }
      } catch (error) {
        this.error = '网络错误'
        console.error('Error fetching files:', error)
      } finally {
        this.loading = false
      }
    },
    async handleFileClick(file) {
      this.selectedFile = file
      this.showUrdfViewer = true
      this.visualizationStatus = 'Loading URDF model...'
      this.isVisualizationRunning = true
      
      try {
        console.log('Loading URDF model...')
        const response = await fetch(`http://localhost:5000/api/files/${file.name}/content`)
        const data = await response.json()
        
        if (response.ok) {
          this.visualizationStatus = 'URDF model loaded successfully'
          console.log('URDF model loaded successfully')
        } else {
          this.visualizationStatus = `Error: ${data.error || 'Failed to load URDF model'}`
          this.isVisualizationRunning = false
          this.showUrdfViewer = false
          console.error('Failed to load URDF model:', data.error)
        }
      } catch (error) {
        this.visualizationStatus = 'Network error while loading URDF model'
        this.isVisualizationRunning = false
        this.showUrdfViewer = false
        console.error('Error loading URDF model:', error)
      }
    },
    async stopVisualization() {
      try {
        const response = await fetch('http://localhost:5000/api/urdf/stop', {
          method: 'POST'
        })
        
        const data = await response.json()
        if (response.ok) {
          this.visualizationStatus = 'Visualization stopped successfully'
          this.isVisualizationRunning = false
          this.visualizationUrl = ''
        } else {
          this.visualizationStatus = `Error: ${data.error || 'Failed to stop visualization'}`
        }
      } catch (error) {
        this.visualizationStatus = 'Network error while stopping visualization'
        console.error('Error stopping visualization:', error)
      }
    },
    changePage(page) {
      this.currentPage = page
      this.fetchFiles()
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    formatDate(timestamp) {
      return new Date(timestamp * 1000).toLocaleString()
    },
    goToHome() {
      this.$router.push('/')
    }
  },
  mounted() {
    this.fetchFiles()
  }
}
</script>

<style scoped>
.file-browser {
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  justify-content: flex-start;
  padding-top: 100px;
  position: relative;
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

.file-list {
  width: 33.33%;
  margin-left: 20px;
  background: rgba(10, 10, 26, 0.4);
  border: 1px solid rgba(159, 107, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(159, 107, 255, 0.1);
  height: calc(100vh - 140px);
  overflow-y: auto;
  backdrop-filter: blur(5px);
  display: flex;
  flex-direction: column;
}

.divider {
  width: 2px;
  background: linear-gradient(to bottom, 
    transparent,
    rgba(159, 107, 255, 0.3),
    rgba(216, 181, 255, 0.5),
    rgba(159, 107, 255, 0.3),
    transparent
  );
  margin: 0 20px;
  height: calc(100vh - 140px);
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.2);
}

.content-area {
  flex: 1;
  background: rgba(10, 10, 26, 0.4);
  border: 1px solid rgba(159, 107, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 0 20px rgba(159, 107, 255, 0.1);
  height: calc(100vh - 140px);
  overflow-y: auto;
  backdrop-filter: blur(5px);
}

.files-container {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 15px;
  padding-right: 5px;
}

.files-container::-webkit-scrollbar {
  width: 6px;
}

.files-container::-webkit-scrollbar-track {
  background: rgba(159, 107, 255, 0.1);
  border-radius: 3px;
}

.files-container::-webkit-scrollbar-thumb {
  background: rgba(159, 107, 255, 0.3);
  border-radius: 3px;
}

.files-container::-webkit-scrollbar-thumb:hover {
  background: rgba(159, 107, 255, 0.4);
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 10px;
}

.file-item {
  background: rgba(159, 107, 255, 0.05);
  border: 1px solid rgba(216, 181, 255, 0.2);
  border-radius: 6px;
  padding: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  width: 100%;
}

.file-item:hover {
  background: rgba(159, 107, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(159, 107, 255, 0.2);
}

.file-icon {
  font-size: 16px;
  margin-bottom: 4px;
}

.file-info {
  color: #d8b5ff;
}

.file-name {
  font-size: 12px;
  margin-bottom: 2px;
  word-break: break-all;
  line-height: 1.2;
}

.file-details {
  font-size: 10px;
  color: rgba(216, 181, 255, 0.7);
  display: flex;
  justify-content: space-between;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 15px 0;
  background: rgba(10, 10, 26, 0.6);
  border-top: 1px solid rgba(159, 107, 255, 0.2);
  margin-top: auto;
}

.cyber-button {
  display: inline-block;
  padding: 8px 20px;
  background-color: rgba(159, 107, 255, 0.15);
  color: #d8b5ff;
  border: 2px solid rgba(216, 181, 255, 0.5);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
}

.cyber-button:hover:not(:disabled) {
  background-color: rgba(159, 107, 255, 0.25);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.5);
}

.cyber-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #d8b5ff;
  font-size: 14px;
  min-width: 120px;
  text-align: center;
}

.loading, .error, .no-files {
  text-align: center;
  color: #d8b5ff;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #ff6b6b;
}

.file-preview {
  padding: 20px;
  color: #d8b5ff;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.file-preview h3 {
  margin-bottom: 15px;
  color: #d8b5ff;
  font-size: 1.2em;
}

.status-message {
  margin-bottom: 15px;
  padding: 10px;
  background: rgba(159, 107, 255, 0.1);
  border: 1px solid rgba(216, 181, 255, 0.3);
  border-radius: 6px;
}

.stop-button {
  margin-top: 15px;
  align-self: flex-start;
}

.visualization-container {
  margin-top: 20px;
  width: 100%;
  height: calc(100vh - 300px);
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(159, 107, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.visualization-frame {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
}

.visualization-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  pointer-events: none;
  z-index: 1;
}
</style>