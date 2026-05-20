<template>
  <div class="app-container">
    <header class="navbar">
      <div class="nav-left">
        <span class="brand-title">ROBOT-VISION INTERFACE</span>
        <span class="status-badge">ONLINE</span>
      </div>
      <div class="nav-right">
        <span class="system-desc">多模态机器人视觉理解系统</span>
      </div>
    </header>

    <div class="workspace">
      <section class="console-panel">
        <div class="panel-header">
          <h2>01 / 二维图像语义理解 (SegFormer)</h2>
        </div>
        
        <div class="panel-control">
          <el-upload
            class="minimal-upload"
            action="#"
            :auto-upload="false"
            :on-change="handle2DFileChange"
            :show-file-list="false"
          >
            <el-button size="small" plain>选择输入图像...</el-button>
          </el-upload>
          <el-button type="primary" size="small" @click="run2DAnalysis" class="action-btn">
            RUN ENGINE
          </el-button>
        </div>

        <div class="display-area" v-loading="loading2D">
          <div v-if="!result2DUrl" class="empty-state">NO DATA</div>
          <img v-else :src="result2DUrl" class="panel-img" />
        </div>

        <div v-if="result2DUrl && detectedTargets.length > 0" class="meta-dashboard">
          <span class="meta-title">TARGETS_IDENTIFIED:</span>
          <div class="tag-group">
            <el-tag 
              v-for="target in detectedTargets" 
              :key="target.name" 
              class="industrial-tag"
              effect="plain"
              size="small"
            >
              <span class="color-dot" :style="{ backgroundColor: target.color }"></span>
              {{ target.name.toUpperCase() }}
            </el-tag>
          </div>
        </div>
      </section>

      <section class="console-panel">
        <div class="panel-header">
          <h2>02 / 三维点云空间解析 (LiDAR 3D Render)</h2>
        </div>
        
        <div class="panel-control">
          <el-upload
            class="minimal-upload"
            action="#"
            :auto-upload="false"
            :on-change="handle3DFileChange"
            :show-file-list="false"
            accept=".pcd,.bin,.ply"
          >
            <el-button size="small" plain>选择点云文件...</el-button>
          </el-upload>
          <el-button type="success" size="small" @click="run3DAnalysis" class="action-btn">
            RUN ENGINE
          </el-button>
        </div>

        <div class="display-area" v-loading="loading3D" ref="threeContainer">
          <div v-if="!has3DData" class="empty-state">NO 3D DATA (ROTATABLE)</div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js'

interface DetectedTarget {
  name: string
  color: string
}

const file2D = ref<File | null>(null)
const result2DUrl = ref('')
const loading2D = ref(false)
const detectedTargets = ref<DetectedTarget[]>([])

const handle2DFileChange = (uploadFile: any) => {
  file2D.value = uploadFile.raw
  ElMessage.success(`已载入图像: ${file2D.value?.name}`)
}

const run2DAnalysis = async () => {
  if (!file2D.value) return ElMessage.error('缺失输入数据')
  loading2D.value = true
  detectedTargets.value = [] 
  
  const formData = new FormData()
  formData.append('file', file2D.value)
  try {
    const res = await fetch('/api/analyze/2d', { method: 'POST', body: formData })
    const data = await res.json()
    if (data.status === 'success') {
      result2DUrl.value = data.result_url
      detectedTargets.value = data.targets 
    }
  } catch (err) {
    ElMessage.error('通信异常')
  } finally {
    loading2D.value = false
  }
}

// --- 3D 逻辑（重构：整合 Three.js） ---
const file3D = ref<File | null>(null)
const loading3D = ref(false)
const has3DData = ref(false)

// Three.js 全局变量引用
const threeContainer = ref<HTMLDivElement | null>(null)
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let controls: OrbitControls | null = null
let currentPoints: THREE.Points | null = null
let animationFrameId: number | null = null

const handle3DFileChange = (uploadFile: any) => {
  file3D.value = uploadFile.raw
  ElMessage.success(`已载入点云: ${file3D.value?.name}`)
}

// 初始化 Three.js 视口
const initThree = (container: HTMLDivElement) => {
  // 1. 创建场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color('#0b0c0d') // 对齐工业极简风底色

  // 2. 创建相机
  const width = container.clientWidth
  const height = container.clientHeight
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100)
  camera.position.set(0, 5, 10) // 俯视视角

  // 3. 创建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  container.appendChild(renderer.domElement)

  // 4. 创建鼠标轨道控制器 (允许拖拽、旋转、缩放)
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05

  // 5. 渲染循环
  const animate = () => {
    animationFrameId = requestAnimationFrame(animate)
    if (controls) controls.update()
    if (renderer && scene && camera) renderer.render(scene, camera)
  }
  animate()
}

const run3DAnalysis = async () => {
  if (!file3D.value) return ElMessage.error('缺失输入数据')
  loading3D.value = true
  const formData = new FormData()
  formData.append('file', file3D.value)
  
  try {
    const res = await fetch('/api/analyze/3d', { method: 'POST', body: formData })
    const data = await res.json()
    
    if (data.status === 'success' && threeContainer.value) {
      has3DData.value = true
      
      // 如果是第一次加载，初始化 Three.js 环境
      if (!scene) {
        initThree(threeContainer.value)
      }
      
      // 如果场景中已有上一次的点云，先将其移除释放内存
      if (currentPoints && scene) {
        scene.remove(currentPoints)
        currentPoints.geometry.dispose()
        if (Array.isArray(currentPoints.material)) {
          currentPoints.material.forEach(m => m.dispose())
        } else {
          currentPoints.material.dispose()
        }
      }

      // 使用 PLYLoader 异步加载后端传过来的 .ply 文件
      const loader = new PLYLoader()
      loader.load(data.result_url, (geometry) => {
        const material = new THREE.PointsMaterial({
          size: 0.05,             // 点的大小
          vertexColors: true,     // 启用顶点颜色绑定
          sizeAttenuation: true   // 随距离远近自动缩放点的大小
        })
        
        currentPoints = new THREE.Points(geometry, material)
        
      
        geometry.computeBoundingBox()
        if (geometry.boundingBox) {
          const center = new THREE.Vector3()
          geometry.boundingBox.getCenter(center)
          currentPoints.position.sub(center)
        }

        if (scene) scene.add(currentPoints)
        ElMessage.success('3D 空间交互渲染完成')
      }, 
      (xhr) => {
        console.log((xhr.loaded / xhr.total * 100) + '% loaded')
      }, 
      (err) => {
        ElMessage.error('点云解析渲染失败')
      })
    }
  } catch (err) {
    ElMessage.error('通信异常')
  } finally {
    loading3D.value = false
  }
}


onBeforeUnmount(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  if (renderer && renderer.domElement) {
    renderer.dispose()
    renderer.domElement.remove()
  }
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: #111214; 
  color: #a0a5ad;
  font-family: monospace, sans-serif; 
  padding: 0;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: #16171a;
  border-bottom: 1px solid #262930;
}

.brand-title {
  color: #fff;
  font-weight: bold;
  letter-spacing: 1px;
}

.status-badge {
  font-size: 11px;
  background: #243829;
  color: #4ade80;
  padding: 2px 6px;
  margin-left: 12px;
  border-radius: 3px;
}

.system-desc {
  font-size: 13px;
  color: #636873;
}

.workspace {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  padding: 30px;
}

.console-panel {
  background-color: #16171a;
  border: 1px solid #262930;
  border-radius: 4px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.panel-header h2 {
  font-size: 15px;
  font-weight: 500;
  color: #e2e4e9;
  margin: 0 0 15px 0;
}

.panel-control {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1c1d21;
  padding: 10px 15px;
  border: 1px solid #262930;
  margin-bottom: 15px;
}

.minimal-upload {
  display: inline-block;
}

:deep(.el-button--small) {
  border-radius: 2px;
  background-color: transparent;
  border-color: #3b3f4a;
  color: #a0a5ad;
}

:deep(.el-button--primary) {
  background-color: #3b3f4a !important; 
  border-color: #4e5361 !important;
  color: #fff;
}
:deep(.el-button--success) {
  background-color: #2e3b32 !important; 
  border-color: #3b4d41 !important;
  color: #4ade80;
}

.display-area {
  background-color: #0b0c0d;
  border: 1px solid #262930;
  height: 450px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  position: relative;
}

.empty-state {
  color: #3b3f4a;
  font-size: 14px;
  letter-spacing: 2px;
  pointer-events: none; /* 防止遮挡 canvas 的鼠标事件 */
  position: absolute;
  z-index: 10;
}

.panel-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

:deep(.el-loading-mask) {
  background-color: rgba(11, 12, 13, 0.85) !important;
}


:deep(canvas) {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

.meta-dashboard {
  background-color: #1c1d21;
  border: 1px solid #262930;
  border-top: none; 
  padding: 12px 15px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.meta-title {
  font-size: 11px;
  color: #636873;
  font-weight: bold;
  letter-spacing: 1px;
  white-space: nowrap;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}


.industrial-tag {
  display: inline-flex !important;
  align-items: center;
  gap: 6px;
  background-color: #111214 !important;
  border-color: #3b3f4a !important;
  color: #e2e4e9 !important;
  border-radius: 2px !important;
  font-family: monospace;
  font-size: 11px !important;
  letter-spacing: 0.5px;
}


.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 1px; 
  display: inline-block;
  flex-shrink: 0;
}
</style>