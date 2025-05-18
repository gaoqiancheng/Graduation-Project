<!-- HomePage.vue -->
<template>
  <BackgroundLayout>
    <div class="upload-container">
      <div class="button-group">
        <label for="file-upload" class="cyber-button">
          Upload File
          <input id="file-upload" type="file" @change="handleFileUpload" />
        </label>
        <button class="cyber-button" @click="handleFileBrowse">
          Browse Files
        </button>
        <button class="cyber-button" @click="handleCreateFile">
          Create File
        </button>
      </div>
    </div>
    <!-- 添加成功提示弹窗 -->
    <div v-if="showSuccess" class="success-notification">
      <div class="notification-content">
        <div class="notification-icon">✓</div>
        <div class="notification-message">文件上传成功！</div>
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
      showSuccess: false
    }
  },
  methods: {
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
          this.showSuccess = true;
          // 3秒后自动隐藏提示
          setTimeout(() => {
            this.showSuccess = false;
          }, 3000);
        } else {
          console.error('上传失败:', result.error);
        }
      } catch (error) {
        console.error('请求错误:', error);
      }
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
</style>