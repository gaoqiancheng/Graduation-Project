<template>
  <div class="home">
    <!-- 背景装饰元素 -->
    <div class="cyber-circle"></div>
    <div class="cyber-circle"></div>
    
    <div class="tech-lines">
      <div class="tech-line"></div>
      <div class="tech-line"></div>
      <div class="tech-line-vertical"></div>
      <div class="tech-line-vertical"></div>
    </div>
    
    <div class="site-header">
      <h1 class="site-title">URDF Online</h1>
    </div>
    
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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

/* 全局背景样式 */
.home {
  padding: 20px;
  position: relative;
  height: 100vh;
  background-color: #0a0a1a;
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(159, 107, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 90% 80%, rgba(216, 181, 255, 0.1) 0%, transparent 40%),
    linear-gradient(135deg, rgba(10, 10, 26, 0.95) 0%, rgba(30, 15, 60, 0.95) 100%);
  overflow: hidden;
}

/* 添加机甲元素 - 背景网格 */
.home::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(to right, rgba(159, 107, 255, 0.05) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(159, 107, 255, 0.05) 1px, transparent 1px);
  background-size: 30px 30px;
  z-index: 0;
}

/* 添加霓虹元素 - 发光线条 */
.home::after {
  content: "";
  position: absolute;
  top: 50%;
  left: -10%;
  width: 120%;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(159, 107, 255, 0.2) 20%, 
    rgba(216, 181, 255, 0.8) 50%,
    rgba(159, 107, 255, 0.2) 80%, 
    transparent 100%);
  box-shadow: 
    0 0 15px rgba(159, 107, 255, 0.5),
    0 0 30px rgba(159, 107, 255, 0.3);
  animation: scanline 8s linear infinite;
  z-index: 1;
}

/* 机甲装饰元素 */
.cyber-circle {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(216, 181, 255, 0.3);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.2);
  pointer-events: none;
  z-index: 0;
}

.cyber-circle:nth-child(1) {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -100px;
}

.cyber-circle:nth-child(2) {
  width: 200px;
  height: 200px;
  bottom: 50px;
  left: -50px;
}

.tech-lines {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 0;
}

.tech-line {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(159, 107, 255, 0.2), transparent);
  height: 1px;
}

.tech-line:nth-child(1) {
  width: 60%;
  top: 20%;
  left: 20%;
  animation: pulse 4s infinite alternate;
}

.tech-line:nth-child(2) {
  width: 40%;
  top: 70%;
  left: 50%;
  animation: pulse 6s infinite alternate-reverse;
}

.tech-line-vertical {
  position: absolute;
  background: linear-gradient(180deg, transparent, rgba(159, 107, 255, 0.1), transparent);
  width: 1px;
}

.tech-line-vertical:nth-child(3) {
  height: 70%;
  top: 15%;
  left: 30%;
  animation: pulse 5s infinite alternate;
}

.tech-line-vertical:nth-child(4) {
  height: 50%;
  top: 25%;
  right: 20%;
  animation: pulse 7s infinite alternate-reverse;
}

/* 修改后的上传按钮样式 */
.upload-button {
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

.upload-button:hover {
  background-color: rgba(159, 107, 255, 0.25);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.5), 0 0 25px rgba(159, 107, 255, 0.3);
  transform: translateY(-2px);
  text-shadow: 0 0 8px #9f6bff, 0 0 15px rgba(159, 107, 255, 0.7);
}

.upload-button:active {
  transform: translateY(1px);
  box-shadow: 0 0 8px rgba(159, 107, 255, 0.4);
}

/* 上传按钮的霓虹效果 */
.upload-button::before {
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

.upload-button:hover::before {
  opacity: 0.3;
  animation: borderPulse 2s linear infinite;
}

.site-header {
  position: absolute;
  top: 20px;
  left: 30px;
  z-index: 10;
}

.site-title {
  color: #d8b5ff;
  font-size: 36px;
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 0 15px #9f6bff, 0 0 25px rgba(159, 107, 255, 0.5);
  letter-spacing: 2px;
  background: linear-gradient(to bottom, #d8b5ff, #9f6bff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.upload-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
}

input[type="file"] {
  display: none;
}

/* 动画效果 */
@keyframes pulse {
  0% { opacity: 0.3; }
  100% { opacity: 0.7; }
}

@keyframes scanline {
  0% { transform: translateY(0) scaleX(1); }
  50% { transform: translateY(25vh) scaleX(1.1); }
  100% { transform: translateY(50vh) scaleX(1); }
}

@keyframes borderPulse {
  0% { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(360deg); }
}
</style>