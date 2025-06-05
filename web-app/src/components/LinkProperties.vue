<!-- LinkProperties.vue -->
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
          @input="handleInput('name', $event)"
        />
        <span class="error-message" v-if="!localProperties.name">名称不能为空</span>
      </div>
      <div class="property-item">
        <label>类型 <span class="required">*</span></label>
        <select 
          v-model="localProperties.type"
          @change="handleInput('type', $event)"
        >
          <option value="box">长方体</option>
          <option value="cylinder">圆柱体</option>
          <option value="sphere">球体</option>
        </select>
      </div>
    </div>

    <!-- 几何属性 -->
    <div class="property-section">
      <h4>几何属性</h4>
      <div class="property-item">
        <label>尺寸 <span class="required">*</span></label>
        <div class="dimension-inputs">
          <input 
            type="number" 
            v-model.number="localProperties.dimensions.x"
            step="0.1"
            min="0.1"
            :placeholder="localProperties.type === 'sphere' ? '直径' : 'X'"
            @input="handleInput('dimensions.x', $event)"
          />
          <input 
            type="number" 
            v-model.number="localProperties.dimensions.y"
            step="0.1"
            min="0.1"
            :placeholder="localProperties.type === 'sphere' ? '不使用' : 'Y'"
            :disabled="localProperties.type === 'sphere'"
            @input="handleInput('dimensions.y', $event)"
          />
          <input 
            type="number" 
            v-model.number="localProperties.dimensions.z"
            step="0.1"
            min="0.1"
            placeholder="Z"
            :disabled="localProperties.type === 'cylinder' || localProperties.type === 'sphere'"
            @input="handleInput('dimensions.z', $event)"
          />
        </div>
        <div class="dimension-labels">
          <span>{{ getDimensionLabel('x') }}</span>
          <span>{{ getDimensionLabel('y') }}</span>
          <span>{{ getDimensionLabel('z') }}</span>
        </div>
      </div>
      <div class="property-item">
        <label>位置</label>
        <div class="dimension-inputs">
          <input 
            type="number" 
            v-model.number="localProperties.position.x"
            step="0.1"
            placeholder="X"
            @input="updatePosition"
          />
          <input 
            type="number" 
            v-model.number="localProperties.position.y"
            step="0.1"
            placeholder="Y"
            @input="updatePosition"
          />
          <input 
            type="number" 
            v-model.number="localProperties.position.z"
            step="0.1"
            placeholder="Z"
            @input="updatePosition"
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

    <!-- 物理属性 -->
    <div class="property-section">
      <h4>物理属性</h4>
      <div class="property-item">
        <label>质量 (kg)</label>
        <input 
          type="number" 
          v-model.number="localProperties.mass"
          step="0.1"
          min="0"
        />
      </div>
      <div class="property-item">
        <label>惯性矩阵</label>
        <div class="inertia-inputs">
          <input 
            type="number" 
            v-model.number="localProperties.inertia.ixx"
            step="0.1"
            placeholder="Ixx"
          />
          <input 
            type="number" 
            v-model.number="localProperties.inertia.ixy"
            step="0.1"
            placeholder="Ixy"
          />
          <input 
            type="number" 
            v-model.number="localProperties.inertia.ixz"
            step="0.1"
            placeholder="Ixz"
          />
          <input 
            type="number" 
            v-model.number="localProperties.inertia.iyy"
            step="0.1"
            placeholder="Iyy"
          />
          <input 
            type="number" 
            v-model.number="localProperties.inertia.iyz"
            step="0.1"
            placeholder="Iyz"
          />
          <input 
            type="number" 
            v-model.number="localProperties.inertia.izz"
            step="0.1"
            placeholder="Izz"
          />
        </div>
      </div>
    </div>

    <!-- 碰撞属性 -->
    <div class="property-section">
      <h4>碰撞属性</h4>
      <div class="property-item">
        <label>启用碰撞检测</label>
        <input 
          type="checkbox" 
          v-model="localProperties.collision.enabled"
        />
      </div>
      <div v-if="localProperties.collision.enabled" class="collision-properties">
        <div class="property-item">
          <label>碰撞类型</label>
          <select v-model="localProperties.collision.type">
            <option value="box">长方体</option>
            <option value="cylinder">圆柱体</option>
            <option value="sphere">球体</option>
          </select>
        </div>
        <div class="property-item">
          <label>碰撞尺寸</label>
          <div class="dimension-inputs">
            <input 
              type="number" 
              v-model.number="localProperties.collision.dimensions.x"
              step="0.1"
              min="0.1"
              placeholder="X"
            />
            <input 
              type="number" 
              v-model.number="localProperties.collision.dimensions.y"
              step="0.1"
              min="0.1"
              placeholder="Y"
            />
            <input 
              type="number" 
              v-model.number="localProperties.collision.dimensions.z"
              step="0.1"
              min="0.1"
              placeholder="Z"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 材质属性 -->
    <div class="property-section">
      <h4>材质属性</h4>
      <div class="property-item">
        <label>颜色</label>
        <input 
          type="color" 
          :value="localProperties.color"
          @input="e => { 
            localProperties.color = e.target.value;
            $emit('update:properties', localProperties);
          }"
        />
      </div>
      <div class="property-item">
        <label>材质类型</label>
        <select 
          :value="localProperties.material.type"
          @change="e => updateMaterialType(e.target.value)"
        >
          <option value="default">默认</option>
          <option value="metal">金属</option>
          <option value="plastic">塑料</option>
          <option value="rubber">橡胶</option>
        </select>
      </div>
      <div class="property-item">
        <label>纹理图片</label>
        <input 
          type="file" 
          @change="handleTextureUpload"
          accept="image/*"
        />
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
  name: 'LinkProperties',
  props: {
    properties: {
      type: Object,
      required: true
    },
    isEditing: {
      type: Boolean,
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
      // 基本验证：名称不能为空
      if (this.localProperties.name.trim() === '') {
        return false;
      }

      // 根据几何体类型验证尺寸
      const dims = this.localProperties.dimensions;
      switch (this.localProperties.type) {
        case 'box':
          return dims.x > 0 && dims.y > 0 && dims.z > 0;
        case 'cylinder':
          return dims.x > 0 && dims.y > 0; // 只需要直径和高度
        case 'sphere':
          return dims.x > 0; // 只需要直径
        default:
          return false;
      }
    }
  },
  watch: {
    properties: {
      handler(newVal) {
        console.log('Step 2: Properties changed in LinkProperties');
        console.log('Received new properties:', JSON.stringify(newVal));
        
        // 避免直接修改 props，创建深拷贝
        const defaultProps = this.getDefaultProperties();
        const newProps = JSON.parse(JSON.stringify(newVal));
        
        // 合并属性，确保所有必要的属性都存在，但优先使用新值
        this.localProperties = {
          ...defaultProps,
          ...newProps,
          dimensions: {
            ...defaultProps.dimensions,
            ...newProps.dimensions
          },
          material: {
            ...defaultProps.material,
            ...(newProps.material || {})
          }
        };
        
        console.log('Updated local properties:', JSON.stringify(this.localProperties));
        console.log('Current validation state:', this.isValid);
      },
      deep: true,
      immediate: true
    },
    
    // 添加对本地属性的监听
    localProperties: {
      handler(newVal) {
        console.log('Step 2.1: Local properties changed:', JSON.stringify(newVal));
        console.log('Current validation state:', this.isValid);
      },
      deep: true
    },
    'localProperties.type': {
      handler(newType) {
        console.log('Type changed to:', newType);
        this.$emit('update:properties', this.localProperties);
      }
    }
  },
  methods: {
    getDefaultProperties() {
      return {
        name: '',
        type: 'box',
        dimensions: {
          x: 1,
          y: 1,
          z: 1
        },
        color: '#9f6bff',
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
        mass: 1,
        inertia: {
          ixx: 1,
          ixy: 0,
          ixz: 0,
          iyy: 1,
          iyz: 0,
          izz: 1
        },
        collision: {
          enabled: false,
          type: 'box',
          dimensions: {
            x: 1,
            y: 1,
            z: 1
          }
        },
        material: {
          type: 'default',
          texture: ''
        }
      }
    },
    handleTextureUpload(event) {
      const file = event.target.files[0]
      if (file) {
        // 这里可以添加文件上传和处理的逻辑
        console.log('Texture file selected:', file.name)
      }
    },
    updateMaterialType(type) {
      // 根据材质类型更新颜色
      let color = '#9f6bff'
      switch(type) {
        case 'metal':
          color = '#C0C0C0'
          break
        case 'plastic':
          color = '#9f6bff'
          break
        case 'rubber':
          color = '#303030'
          break
      }
      
      // 批量更新属性以避免多次触发更新
      this.localProperties = {
        ...this.localProperties,
        color,
        material: {
          ...this.localProperties.material,
          type
        }
      }
      
      // 通知父组件更新
      this.$emit('update:properties', this.localProperties)
    },
    saveProperties() {
      console.log('Step 4: Save button clicked');
      console.log('Current validation state:', this.isValid);
      console.log('Validation details:', {
        name: this.localProperties.name.trim() !== '',
        dimensions: {
          x: this.localProperties.dimensions.x > 0,
          y: this.localProperties.dimensions.y > 0,
          z: this.localProperties.dimensions.z > 0
        },
        type: this.localProperties.type
      });
      
      if (!this.isValid) {
        console.log('Save blocked - validation failed');
        return;
      }
      
      // 确保所有必要的属性都存在并且格式正确
      const properties = {
        ...this.localProperties,
        dimensions: {
          x: Number(this.localProperties.dimensions.x) || 1,
          y: Number(this.localProperties.dimensions.y) || 1,
          z: Number(this.localProperties.dimensions.z) || 1
        },
        material: {
          type: this.localProperties.material?.type || 'default',
          texture: this.localProperties.material?.texture || ''
        }
      };
      
      console.log('Emitting save with properties:', JSON.stringify(properties));
      this.$emit('save', properties);
    },
    getDimensionLabel(axis) {
      switch(this.localProperties.type) {
        case 'box':
          return {
            x: '长度',
            y: '宽度',
            z: '高度'
          }[axis];
        case 'cylinder':
          return {
            x: '直径',
            y: '高度',
            z: '不使用'
          }[axis];
        case 'sphere':
          return {
            x: '直径',
            y: '不使用',
            z: '不使用'
          }[axis];
        default:
          return axis.toUpperCase();
      }
    },
    updatePosition() {
      console.log('Position updated:', this.localProperties.position);
      // 确保发送更新事件
      this.$emit('update:properties', this.localProperties);
    },
    handleInput(field, event) {
      console.log(`Step 3: User input - ${field}:`, event.target.value);
      console.log('Current validation state:', this.isValid);
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

.property-item input:focus,
.property-item select:focus {
  outline: none;
  border-color: rgba(216, 181, 255, 0.8);
  box-shadow: 0 0 10px rgba(159, 107, 255, 0.3);
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

.inertia-inputs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  width: 100%;
}

.inertia-inputs input {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  text-align: center;
  padding: 4px;
  font-size: 12px;
  height: 26px;
}

.collision-properties {
  margin-top: 8px;
  padding: 8px;
  background: rgba(159, 107, 255, 0.1);
  border-radius: 6px;
}

.property-item input[type="color"] {
  height: 32px;
  padding: 2px;
}

.property-item input[type="checkbox"] {
  width: auto;
  height: auto;
  margin-right: 8px;
}

.button-group {
  display: flex;
  gap: 8px;
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

.property-item input[type="number"] {
  -moz-appearance: textfield;
}

.property-item input[type="number"]::-webkit-outer-spin-button,
.property-item input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.dimension-labels {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin-top: 4px;
}

.dimension-labels span {
  text-align: center;
  font-size: 11px;
  color: rgba(216, 181, 255, 0.6);
}
</style> 