<!-- HomePage.vue -->
<template>
  <BackgroundLayout>
    <div class="upload-container">
      <div class="button-group">
        <button class="cyber-button" @click="showUploadDialog = true">
          Upload URDF
        </button>
        <button class="cyber-button" @click="handleFileBrowse">
          Browse Files
        </button>
        <button class="cyber-button" @click="handleCreateFile">
          Create File
        </button>
      </div>

      <!-- 上传模式选择对话框 -->
      <div v-if="showUploadDialog" class="dialog-overlay">
        <div class="dialog-content">
          <h3>Select Upload Mode</h3>
          <div class="upload-options">
            <div class="upload-option" @click="handleSingleFileUpload">
              <div class="option-icon">📄</div>
              <div class="option-content">
                <h4>Single File Mode</h4>
                <p>Upload a single URDF file</p>
              </div>
            </div>
            <div class="upload-option" @click="handleFolderUpload">
              <div class="option-icon">📁</div>
              <div class="option-content">
                <h4>Folder Mode</h4>
                <p>Upload a folder containing URDF and related files</p>
              </div>
            </div>
          </div>
          <button class="close-button" @click="showUploadDialog = false">Close</button>
        </div>
      </div>

      <!-- 隐藏的文件输入 -->
      <input
        id="file-upload"
        type="file"
        @change="handleFileUpload"
        accept=".urdf"
        ref="fileInput"
        style="display: none"
      />
      
      <!-- 隐藏的文件夹输入 -->
      <input
        id="folder-upload"
        type="file"
        @change="handleFolderUploadChange"
        webkitdirectory
        directory
        multiple
        ref="folderInput"
        style="display: none"
      />
    </div>

    <!-- 成功提示弹窗 -->
    <div v-if="showSuccess" class="success-notification">
      <div class="notification-content">
        <div class="notification-icon">✓</div>
        <div class="notification-message">{{ successMessage }}</div>
      </div>
    </div>
  </BackgroundLayout>
</template>

<script>
import BackgroundLayout from '@/components/BackgroundLayout.vue'
export default {
  name: 'HomePage',
  components: {
    BackgroundLayout
  },
  data() {
    return {
      showSuccess: false,
      showUploadDialog: false,
      successMessage: ''
    }
  },
  methods: {
    handleSingleFileUpload() {
      this.$refs.fileInput.click();
      this.showUploadDialog = false;
    },

    handleFolderUpload() {
      this.$refs.folderInput.click();
      this.showUploadDialog = false;
    },

    async handleFolderUploadChange(event) {
      const files = event.target.files;
      if (!files.length) return;

      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i], files[i].webkitRelativePath);
      }

      try {
        const response = await fetch('http://localhost:5000/api/files/upload-folder', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();
        if (response.ok) {
          console.log('文件夹上传成功:', result);
          this.successMessage = '文件夹上传成功！';
          this.showSuccess = true;
          setTimeout(() => {
            this.showSuccess = false;
          }, 3000);
        } else {
          console.error('上传失败:', result.error);
          this.successMessage = `上传失败: ${result.error}`;
          this.showSuccess = true;
          setTimeout(() => {
            this.showSuccess = false;
          }, 3000);
        }
      } catch (error) {
        console.error('请求错误:', error);
        this.successMessage = `请求错误: ${error.message}`;
        this.showSuccess = true;
        setTimeout(() => {
          this.showSuccess = false;
        }, 3000);
      }

      event.target.value = null;
    },

    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:5000/api/files/upload', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();
        if (response.ok) {
          console.log('上传成功:', result);
          this.successMessage = '文件上传成功！';
          this.showSuccess = true;
          setTimeout(() => {
            this.showSuccess = false;
          }, 3000);
        } else {
          console.error('上传失败:', result.error);
        }
      } catch (error) {
        console.error('请求错误:', error);
      }

      event.target.value = null;
    },
    handleFileBrowse() {
      this.$router.push('/browser')
    },
    handleCreateFile() {
      this.$router.push('/create')
    }
  }
}
</script>

<style scoped>
/* 按钮相关样式 */
.button-group {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.cyber-button {
  display: inline-block;
  padding: 12px 30px;
  background-color: rgba(159, 107, 255, 0.15);
  color: #d8b5ff;
  border: 2px solid rgba(216, 181, 255, 0.5);
  border-radius: 8px;
  font-size: 18px;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
  text-shadow: 0 0 5px #9f6bff;
  position: relative;
  overflow: hidden;
  z-index: 10;
}

.cyber-button:hover {
  background-color: rgba(159, 107, 255, 0.25);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.5), 0 0 25px rgba(159, 107, 255, 0.3);
  transform: translateY(-2px);
  text-shadow: 0 0 8px #9f6bff, 0 0 15px rgba(159, 107, 255, 0.7);
}

.cyber-button:active {
  transform: translateY(1px);
  box-shadow: 0 0 8px rgba(159, 107, 255, 0.4);
}

.cyber-button::before {
  content: "";
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #9f6bff, #d8b5ff, #9f6bff);
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 10px;
}

.cyber-button:hover::before {
  opacity: 0.3;
  animation: borderPulse 2s linear infinite;
}

.upload-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
  width: 100%;
}

input[type="file"] {
  display: none;
}

/* 添加成功提示弹窗样式 */
.success-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.notification-content {
  background: rgba(10, 10, 26, 0.9);
  border: 2px solid rgba(159, 107, 255, 0.5);
  border-radius: 8px;
  padding: 15px 25px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 0 20px rgba(159, 107, 255, 0.3);
  backdrop-filter: blur(5px);
}

.notification-icon {
  color: #9f6bff;
  font-size: 24px;
  text-shadow: 0 0 10px rgba(159, 107, 255, 0.7);
}

.notification-message {
  color: #d8b5ff;
  font-size: 16px;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 1px;
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

@keyframes borderPulse {
  0% { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(360deg); }
}

/* 添加对话框相关样式 */
.dialog-overlay {
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
  backdrop-filter: blur(5px);
}

.dialog-content {
  background: rgba(20, 20, 40, 0.95);
  border: 2px solid rgba(159, 107, 255, 0.3);
  border-radius: 12px;
  padding: 25px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 0 30px rgba(159, 107, 255, 0.2);
  animation: dialogFadeIn 0.3s ease-out;
}

.dialog-content h3 {
  color: #d8b5ff;
  text-align: center;
  margin-bottom: 25px;
  font-size: 1.4em;
  text-shadow: 0 0 10px rgba(159, 107, 255, 0.5);
}

.upload-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 25px;
}

.upload-option {
  background: rgba(159, 107, 255, 0.1);
  border: 2px solid rgba(159, 107, 255, 0.2);
  border-radius: 10px;
  padding: 20px;
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
  border-color: rgba(159, 107, 255, 0.4);
}

.upload-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

.option-icon {
  font-size: 28px;
  color: #d8b5ff;
  text-shadow: 0 0 10px rgba(159, 107, 255, 0.5);
}

.option-content h4 {
  color: #d8b5ff;
  margin: 0 0 8px 0;
  font-size: 1.1em;
  text-shadow: 0 0 5px rgba(159, 107, 255, 0.5);
}

.option-content p {
  color: rgba(216, 181, 255, 0.7);
  margin: 0;
  font-size: 0.9em;
}

.close-button {
  display: block;
  width: 100%;
  padding: 12px;
  background: rgba(159, 107, 255, 0.15);
  color: #d8b5ff;
  border: 2px solid rgba(159, 107, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Orbitron', sans-serif;
  font-size: 1em;
  letter-spacing: 1px;
}

.close-button:hover {
  background: rgba(159, 107, 255, 0.25);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.3);
}

@keyframes dialogFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>