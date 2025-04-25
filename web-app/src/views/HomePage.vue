<!-- HomePage.vue -->
<template>
  <BackgroundLayout>
    <div class="upload-container">
      <div class="button-group">
        <label for="file-upload" class="cyber-button">
          上传文件
          <input id="file-upload" type="file" @change="handleFileUpload" />
        </label>
        <button class="cyber-button" @click="handleFileBrowse">
          浏览文件
        </button>
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
  methods: {
    async handleFileUpload(event) {
      // 保持原有文件上传逻辑
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
        } else {
          console.error('上传失败:', result.error);
        }
      } catch (error) {
        console.error('请求错误:', error);
      }
    },
    handleFileBrowse() {
      this.$router.push('/browser')
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

@keyframes borderPulse {
  0% { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(360deg); }
}
</style>