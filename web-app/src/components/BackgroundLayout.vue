<!-- BackgroundLayout.vue -->
<template>
    <div class="background-layout">
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
  
      <!-- 内容插槽 -->
      <slot></slot>
    </div>
  </template>
  
  <script>
  export default {
    name: 'BackgroundLayout'
  }
  </script>
  
  <style scoped>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
  
  .background-layout {
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
  
  .background-layout::before {
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
  
  .background-layout::after {
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
  
  /* 共享的装饰元素样式 */
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
  
  /* 动画需要全局定义 */
  @keyframes pulse {
    0% { opacity: 0.3; }
    100% { opacity: 0.7; }
  }
  
  @keyframes scanline {
    0% { transform: translateY(0) scaleX(1); }
    50% { transform: translateY(25vh) scaleX(1.1); }
    100% { transform: translateY(50vh) scaleX(1); }
  }
  </style>