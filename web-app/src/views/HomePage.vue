<template>
  <div class="home">
    <div class="upload-container">
      <label for="file-upload" class="upload-button">
        上传文件
        <input id="file-upload" type="file" @change="handleFileUpload" />
      </label>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        console.log('选择了文件:', file.name);
        // 在这里处理文件上传逻辑
      }
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}

.upload-container {
  text-align: center;
}

.upload-button {
  display: inline-block;
  padding: 12px 24px;
  background-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-button:hover {
  background-color: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
}

input[type="file"] {
  display: none;
}
</style>