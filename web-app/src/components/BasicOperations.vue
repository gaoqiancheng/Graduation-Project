<!-- BasicOperations.vue -->
<template>
  <div class="tool-section">
    <h3>基本操作</h3>
    <button class="tool-button" @click="$emit('start-modeling')" v-if="!isModeling">
      <span class="icon">▶</span>
      开始建模
    </button>
    <template v-else>
      <button class="tool-button" @click="$emit('add-link')">
        <span class="icon">+</span>
        添加连杆
      </button>
      <button class="tool-button" @click="$emit('add-joint')">
        <span class="icon">+</span>
        添加关节
      </button>
    </template>
  </div>
</template>

<script>
export default {
  name: 'BasicOperations',
  props: {
    isModeling: {
      type: Boolean,
      required: true
    }
  },
  emits: ['start-modeling', 'add-link', 'add-joint']
}
</script>

<style scoped>
.tool-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-section h3 {
  color: #d8b5ff;
  font-size: 16px;
  margin-bottom: 10px;
  font-family: 'Orbitron', sans-serif;
}

.tool-button {
  background: rgba(159, 107, 255, 0.15);
  color: #d8b5ff;
  border: 2px solid rgba(216, 181, 255, 0.5);
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-button:hover {
  background: rgba(159, 107, 255, 0.25);
  box-shadow: 0 0 15px rgba(159, 107, 255, 0.5);
  transform: translateY(-2px);
}

.tool-button .icon {
  font-size: 18px;
}
</style> 