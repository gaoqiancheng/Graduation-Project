<!-- JointProperties.vue -->
<template>
  <div class="property-group">
    <!-- 基本属性 -->
    <div class="property-section">
      <h4>基本属性</h4>
      <div class="property-item">
        <label>名称 <span class="required">*</span></label>
        <input 
          type="text" 
          v-model="localProperties.name"
          placeholder="请输入名称"
          :class="{ 'error': !localProperties.name }"
        />
        <span class="error-message" v-if="!localProperties.name">名称不能为空</span>
      </div>
      <div class="property-item">
        <label>类型 <span class="required">*</span></label>
        <select v-model="localProperties.type">
          <option value="revolute">旋转关节</option>
          <option value="prismatic">移动关节</option>
          <option value="continuous">连续旋转关节</option>
          <option value="fixed">固定关节</option>
        </select>
      </div>
      <div class="property-item">
        <label>父连杆 <span class="required">*</span></label>
        <select v-model="localProperties.parent">
          <option value="">请选择父连杆</option>
          <option v-for="link in linkOptions" :key="link.name" :value="link.name">
            {{ link.displayName }}
          </option>
        </select>
      </div>
      <div class="property-item">
        <label>子连杆 <span class="required">*</span></label>
        <select v-model="localProperties.child">
          <option value="">请选择子连杆</option>
          <option v-for="link in linkOptions" :key="link.name" :value="link.name">
            {{ link.displayName }}
          </option>
        </select>
      </div>
    </div>

    <!-- 位置和旋转 -->
    <div class="property-section">
      <h4>位置和旋转</h4>
      <div class="property-item">
        <label>位置</label>
        <div class="dimension-inputs">
          <input 
            type="number" 
            v-model.number="localProperties.position.x"
            step="0.1"
            placeholder="X"
          />
          <input 
            type="number" 
            v-model.number="localProperties.position.y"
            step="0.1"
            placeholder="Y"
          />
          <input 
            type="number" 
            v-model.number="localProperties.position.z"
            step="0.1"
            placeholder="Z"
          />
        </div>
      </div>
      <div class="property-item">
        <label>旋转 (度)</label>
        <div class="dimension-inputs">
          <input 
            type="number" 
            v-model.number="localProperties.rotation.roll"
            step="1"
            placeholder="Roll"
          />
          <input 
            type="number" 
            v-model.number="localProperties.rotation.pitch"
            step="1"
            placeholder="Pitch"
          />
          <input 
            type="number" 
            v-model.number="localProperties.rotation.yaw"
            step="1"
            placeholder="Yaw"
          />
        </div>
      </div>
    </div>

    <!-- 运动属性 -->
    <div class="property-section">
      <h4>运动属性</h4>
      <div class="property-item">
        <label>旋转轴</label>
        <div class="dimension-inputs">
          <input 
            type="number" 
            v-model.number="localProperties.axis.x"
            step="0.1"
            placeholder="X"
          />
          <input 
            type="number" 
            v-model.number="localProperties.axis.y"
            step="0.1"
            placeholder="Y"
          />
          <input 
            type="number" 
            v-model.number="localProperties.axis.z"
            step="0.1"
            placeholder="Z"
          />
        </div>
      </div>
      <div class="property-item">
        <label>运动限制</label>
        <div class="limit-inputs">
          <div class="limit-item">
            <label>下限</label>
            <input 
              type="number" 
              v-model.number="localProperties.limits.lower"
              step="0.1"
            />
          </div>
          <div class="limit-item">
            <label>上限</label>
            <input 
              type="number" 
              v-model.number="localProperties.limits.upper"
              step="0.1"
            />
          </div>
          <div class="limit-item">
            <label>力矩</label>
            <input 
              type="number" 
              v-model.number="localProperties.limits.effort"
              step="1"
            />
          </div>
          <div class="limit-item">
            <label>速度</label>
            <input 
              type="number" 
              v-model.number="localProperties.limits.velocity"
              step="0.1"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 按钮组 -->
    <div class="button-group">
      <button 
        class="save-button" 
        @click="saveProperties"
        :disabled="!isValid"
      >
        保存
      </button>
      <button 
        v-if="!isEditing" 
        class="delete-button" 
        @click="$emit('delete')"
      >
        删除
      </button>
      <button class="cancel-button" @click="$emit('cancel')">
        取消
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'JointProperties',
  props: {
    properties: {
      type: Object,
      required: true
    },
    isEditing: {
      type: Boolean,
      required: true
    },
    links: {
      type: Map,
      required: true
    }
  },
  emits: ['update:properties', 'save', 'delete', 'cancel'],
  data() {
    return {
      localProperties: this.getDefaultProperties()
    }
  },
  computed: {
    isValid() {
      return this.localProperties.name.trim() !== '' &&
             this.localProperties.parent !== '' &&
             this.localProperties.child !== ''
    },
    linkOptions() {
      const options = [];
      if (this.links) {
        for (const [id, link] of this.links) {
          if (link && link.properties && link.properties.name) {
            options.push({
              name: id,
              displayName: link.properties.name || id
            });
          }
        }
      }
      return options;
    }
  },
  watch: {
    properties: {
      handler(newVal) {
        // 避免直接修改 props，创建深拷贝
        const defaultProps = this.getDefaultProperties()
        const newProps = JSON.parse(JSON.stringify(newVal))
        
        // 合并属性，确保所有必要的属性都存在
        this.localProperties = {
          ...defaultProps,
          ...newProps
        }
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    getDefaultProperties() {
      return {
        name: '',
        type: 'revolute',
        parent: '',
        child: '',
        position: {
          x: 0,
          y: 0,
          z: 0
        },
        rotation: {
          roll: 0,
          pitch: 0,
          yaw: 0
        },
        axis: {
          x: 0,
          y: 0,
          z: 1
        },
        limits: {
          lower: -3.14,
          upper: 3.14,
          effort: 100,
          velocity: 1
        }
      }
    },
    saveProperties() {
      console.log('JointProperties - Saving properties:', {
        name: this.localProperties.name,
        parent: this.localProperties.parent,
        child: this.localProperties.child,
        type: this.localProperties.type,
        position: this.localProperties.position,
        rotation: this.localProperties.rotation,
        axis: this.localProperties.axis,
        limits: this.localProperties.limits
      });
      this.$emit('save', this.localProperties)
    }
  }
}
</script>

<style scoped>
.property-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.property-section {
  margin-bottom: 12px;
  padding: 12px;
  background: rgba(159, 107, 255, 0.05);
  border-radius: 8px;
  position: relative;
}

.property-section h4 {
  color: #d8b5ff;
  font-size: 12px;
  margin-bottom: 10px;
  font-family: 'Orbitron', sans-serif;
}

.property-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.property-item:last-child {
  margin-bottom: 0;
}

.property-item label {
  color: #d8b5ff;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.property-item input,
.property-item select {
  background: rgba(159, 107, 255, 0.1);
  border: 1px solid rgba(216, 181, 255, 0.3);
  border-radius: 4px;
  padding: 6px;
  color: #d8b5ff;
  font-size: 12px;
  height: 28px;
  width: 100%;
  box-sizing: border-box;
}

.dimension-inputs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  width: 100%;
}

.dimension-inputs input {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  text-align: center;
  padding: 4px;
  font-size: 12px;
  height: 26px;
}

.limit-inputs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
  width: 100%;
}

.limit-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.limit-item label {
  font-size: 11px;
  color: rgba(216, 181, 255, 0.8);
}

.limit-item input {
  width: 100%;
  box-sizing: border-box;
  text-align: center;
  padding: 4px;
  font-size: 12px;
  height: 26px;
}

.button-group {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  background: rgba(10, 10, 26, 0.6);
  border-top: 1px solid rgba(159, 107, 255, 0.2);
  position: sticky;
  bottom: 0;
  margin: 0 -12px -12px -12px;
  width: calc(100% + 24px);
  box-sizing: border-box;
}

.save-button,
.cancel-button,
.delete-button {
  flex: 1;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  height: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(216, 181, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-button {
  background: rgba(159, 107, 255, 0.2);
  color: #d8b5ff;
}

.save-button:hover:not(:disabled) {
  background: rgba(159, 107, 255, 0.3);
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(159, 107, 255, 0.1);
}

.cancel-button,
.delete-button {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
  border-color: rgba(255, 107, 107, 0.5);
}

.cancel-button:hover,
.delete-button:hover {
  background: rgba(255, 107, 107, 0.3);
  box-shadow: 0 0 10px rgba(255, 107, 107, 0.3);
}

.required {
  color: #ff6b6b;
  margin-left: 2px;
  font-size: 10px;
}

.error {
  border-color: #ff6b6b !important;
}

.error-message {
  color: #ff6b6b;
  font-size: 11px;
  margin-top: 2px;
}

.property-item input:disabled {
  background: rgba(159, 107, 255, 0.05);
  border-color: rgba(216, 181, 255, 0.2);
  color: rgba(216, 181, 255, 0.5);
  cursor: not-allowed;
}

.property-item input:disabled::placeholder {
  color: rgba(216, 181, 255, 0.3);
}

.property-item input:focus,
.property-item select:focus {
  outline: none;
  border-color: rgba(216, 181, 255, 0.8);
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
}
</style> 