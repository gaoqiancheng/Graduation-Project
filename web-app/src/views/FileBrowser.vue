<!-- views/FileBrowser.vue -->
<template>
  <BackgroundLayout>
    <div class="file-browser">
      <button class="home-button" @click="goToHome">
        Back to Home
      </button>
      <div class="file-list">
        <div class="path-navigator">
          <button 
            class="path-item" 
            @click="navigateToRoot"
          >
            Root
          </button>
          <span v-for="(segment, index) in currentPathSegments" 
                :key="index" 
                class="path-separator"
          >
            /
            <button 
              class="path-item"
              @click="navigateToPath(index)"
            >
              {{ segment }}
            </button>
          </span>
        </div>
        <div class="files-container">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="error" class="error">{{ error }}</div>
          <div v-else-if="files.length === 0" class="no-files">暂无文件</div>
          <div v-else class="file-grid">
            <div 
              v-for="file in files" 
              :key="file.path" 
              class="file-item"
              :class="{ 'selected': selectedFile && selectedFile.path === file.path }"
              @click="handleFileClick(file)"
              @dblclick="handleFileDblClick(file)"
            >
              <div class="file-icon">
                {{ file.isDirectory ? '📁' : getFileIcon(file.name) }}
              </div>
              <div class="file-info">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-details" v-if="!file.isDirectory">
                  <span>{{ formatFileSize(file.size) }}</span>
                  <span>{{ formatDate(file.modified) }}</span>
                </div>
                <div class="file-details" v-else>
                  <span>文件夹</span>
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
              ref="urdfViewer"
              :urdfUrl="`http://localhost:5000/api/files/${selectedFile.path}`"
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
      currentPath: '',
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
      showUrdfViewer: false,
      showUploadDialog: false,
    }
  },
  computed: {
    currentPathSegments() {
      return this.currentPath ? this.currentPath.split('/').filter(Boolean) : [];
    }
  },
  methods: {
    async fetchFiles() {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetch(`http://localhost:5000/api/files/list?path=${encodeURIComponent(this.currentPath)}`);
        const data = await response.json();
        if (response.ok) {
          this.files = data.files;
          this.totalPages = data.total_pages;
        } else {
          this.error = data.error || '获取文件列表失败';
        }
      } catch (error) {
        this.error = '网络错误';
        console.error('Error fetching files:', error);
      } finally {
        this.loading = false;
      }
    },

    handleFileClick(file) {
      this.selectedFile = file;
      if (!file.isDirectory) {
        // 单击文件时只选中，不执行其他操作
        this.showUrdfViewer = false;
        this.isVisualizationRunning = false;
        this.visualizationStatus = null;
      }
    },

    async handleFileDblClick(file) {
      if (file.isDirectory) {
        // 如果是文件夹，进入该文件夹
        this.currentPath = file.path;
        this.selectedFile = null;
        this.showUrdfViewer = false;
        await this.fetchFiles();
      } else if (file.name.toLowerCase().endsWith('.urdf')) {
        // 如果是 URDF 文件，启动可视化
        await this.startVisualization(file);
      }
    },

    async startVisualization(file) {
      this.visualizationStatus = 'Loading URDF model...';
      this.isVisualizationRunning = true;
      
      try {
        // 获取处理后的URDF内容
        const response = await fetch(`http://localhost:5000/api/files/${file.path}/content`);
        const data = await response.json();
        
        if (response.ok) {
          // 直接显示URDFViewer组件，让它通过props加载URDF
          this.showUrdfViewer = true;
          this.visualizationStatus = 'URDF model loaded successfully';
        } else {
          this.visualizationStatus = `Error: ${data.error || 'Failed to load URDF model'}`;
          this.isVisualizationRunning = false;
          this.showUrdfViewer = false;
        }
      } catch (error) {
        this.visualizationStatus = 'Network error while loading URDF model';
        this.isVisualizationRunning = false;
        this.showUrdfViewer = false;
        console.error('Error loading URDF model:', error);
      }
    },

    navigateToRoot() {
      this.currentPath = '';
      this.selectedFile = null;
      this.fetchFiles();
    },

    navigateToPath(index) {
      this.currentPath = this.currentPathSegments.slice(0, index + 1).join('/');
      this.selectedFile = null;
      this.fetchFiles();
    },

    getFileIcon(filename) {
      if (filename.toLowerCase().endsWith('.urdf')) return '📄';
      if (filename.toLowerCase().endsWith('.stl')) return '🔷';
      if (filename.toLowerCase().endsWith('.dae')) return '🔶';
      return '📝';
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    formatDate(timestamp) {
      return new Date(timestamp * 1000).toLocaleString();
    },

    goToHome() {
      this.$router.push('/');
    },

    handleSingleFileUpload() {
      this.$refs.fileInput.click();
      this.showUploadDialog = false;
    },

    async onFileSelected(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:5000/api/files/upload', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          // 重新加载文件列表
          this.fetchFiles();
        } else {
          const error = await response.json();
          console.error('Upload failed:', error);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
      }

      // 清除文件输入
      event.target.value = null;
    },

    async stopVisualization() {
      try {
        // 调用URDFViewer的清理方法
        if (this.$refs.urdfViewer) {
          this.$refs.urdfViewer.cleanup();
        }

        const response = await fetch('http://localhost:5000/api/urdf/stop', {
          method: 'POST'
        });
        
        const data = await response.json();
        if (response.ok) {
          this.visualizationStatus = 'Visualization stopped successfully';
          this.isVisualizationRunning = false;
          this.showUrdfViewer = false;
          this.visualizationUrl = '';
        } else {
          this.visualizationStatus = `Error: ${data.error || 'Failed to stop visualization'}`;
        }
      } catch (error) {
        this.visualizationStatus = 'Network error while stopping visualization';
        console.error('Error stopping visualization:', error);
      }
    },

    changePage(page) {
      this.currentPage = page;
      this.fetchFiles();
    }
  },
  mounted() {
    this.fetchFiles();
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
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  padding: 10px;
}

.file-item {
  background: rgba(159, 107, 255, 0.05);
  border: 1px solid rgba(216, 181, 255, 0.2);
  border-radius: 8px;
  padding: 12px 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100px;
  user-select: none;
}

.file-item:hover {
  background: rgba(159, 107, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(159, 107, 255, 0.2);
}

.file-item.selected {
  background: rgba(159, 107, 255, 0.15);
  border-color: rgba(216, 181, 255, 0.4);
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
}

.file-icon {
  font-size: 28px;
  margin-bottom: 8px;
  text-align: center;
  color: #d8b5ff;
}

.file-info {
  width: 100%;
  text-align: center;
}

.file-name {
  font-size: 13px;
  margin-bottom: 4px;
  word-break: break-word;
  line-height: 1.2;
  color: #d8b5ff;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-details {
  font-size: 11px;
  color: rgba(216, 181, 255, 0.7);
  display: flex;
  justify-content: center;
  gap: 8px;
}

.file-details span {
  white-space: nowrap;
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

.upload-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.upload-dialog {
  background: rgba(20, 20, 40, 0.95);
  border: 1px solid rgba(159, 107, 255, 0.3);
  border-radius: 12px;
  padding: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 0 20px rgba(159, 107, 255, 0.2);
}

.upload-dialog h3 {
  color: #d8b5ff;
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.2em;
}

.upload-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.upload-option {
  background: rgba(159, 107, 255, 0.1);
  border: 1px solid rgba(159, 107, 255, 0.2);
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 15px;
}

.upload-option:not(.disabled):hover {
  background: rgba(159, 107, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(159, 107, 255, 0.2);
}

.upload-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.option-icon {
  font-size: 24px;
  color: #d8b5ff;
}

.option-content h4 {
  color: #d8b5ff;
  margin: 0 0 5px 0;
  font-size: 1em;
}

.option-content p {
  color: rgba(216, 181, 255, 0.7);
  margin: 0;
  font-size: 0.9em;
}

.close-button {
  display: block;
  width: 100%;
  padding: 10px;
  background: rgba(159, 107, 255, 0.15);
  color: #d8b5ff;
  border: 1px solid rgba(159, 107, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: rgba(159, 107, 255, 0.25);
}

.upload-button {
  padding: 10px 20px;
  background: rgba(159, 107, 255, 0.15);
  color: #d8b5ff;
  border: 2px solid rgba(216, 181, 255, 0.5);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-button:hover {
  background: rgba(159, 107, 255, 0.25);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.5);
  transform: translateY(-2px);
}

.path-navigator {
  background: rgba(10, 10, 26, 0.6);
  padding: 10px;
  margin-bottom: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.path-item {
  background: none;
  border: none;
  color: #d8b5ff;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Orbitron', sans-serif;
  transition: all 0.3s ease;
}

.path-item:hover {
  background: rgba(159, 107, 255, 0.2);
}

.path-separator {
  color: rgba(216, 181, 255, 0.5);
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>