<script setup lang="ts">
import { ref } from 'vue';
import type { UploadFile, UploadInstance } from 'element-plus';
import { ElMessage } from 'element-plus';

// 后端 YOLO 服务地址（开发通过前端代理，生产使用直连）
const YOLO_BASE_URL = import.meta.env.DEV ? '/proxy-yolo' : (import.meta.env.VITE_YOLO_BASE_URL ?? 'http://localhost:5000');

// UI 状态
const uploading = ref(false);
const uploadRef = ref<UploadInstance | null>(null);
const selectedFile = ref<UploadFile | null>(null);
const previewUrl = ref<string | null>(null);
const fileList = ref<UploadFile[]>([]);
const taskId = ref<string | null>(null);
const resultImage = ref<string | null>(null);
const detections = ref<Array<{ class: string; confidence: number; bbox: number[] }>>([]);

// 选择文件后生成本地预览
function handleFileChange(file: UploadFile) {
  // 清理上一次预览
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  selectedFile.value = file;
  fileList.value = [file];
  if (file?.raw) previewUrl.value = URL.createObjectURL(file.raw);
  // 清空上一次的检测结果
  taskId.value = null;
  resultImage.value = null;
  detections.value = [];
}

function handleFileRemove() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = null;
  selectedFile.value = null;
  fileList.value = [];
  taskId.value = null;
  resultImage.value = null;
  detections.value = [];
}

// 超出限制时，替换为新选择的文件
function handleExceed(files: File[]) {
  uploadRef.value?.clearFiles();
  fileList.value = [];
  const file = files?.[0];
  (uploadRef.value as any)?.handleStart?.(file);
}

// 手动点击“开始检测”时触发上传（后端接收即开始检测）
async function startDetect() {
  if (!selectedFile.value?.raw) {
    ElMessage.warning('请先选择图片');
    return;
  }
  uploading.value = true;
  try {
    const fd = new FormData();
    fd.append('image', selectedFile.value.raw);
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/upload`, {
      method: 'POST',
      body: fd,
    });
    const data = await resp.json();
    const code = data?.code;
    const tid = data?.data?.taskId as string | undefined;
    if (!resp.ok || code !== 200 || !tid) {
      throw new Error(data?.msg || '上传失败');
    }
    taskId.value = tid;
    await fetchResults(tid);
  } catch (error: any) {
    ElMessage.error(error.message || '检测失败，请重试');
  } finally {
    uploading.value = false;
  }
}

// 上传成功后，后端返回 { code: 200, data: { taskId } }
async function handleUploadSuccess(response: any, file: UploadFile) {
  try {
    const code = response?.code;
    const tid = response?.data?.taskId as string | undefined;
    if (code !== 200 || !tid) {
      throw new Error('上传成功但返回数据异常');
    }
    taskId.value = tid;
    // 上传完成后再获取检测结果
    await fetchResults(tid);
  } catch (error: any) {
    ElMessage.error(error.message || '解析上传结果失败');
  } finally {
    uploading.value = false;
  }
}

function handleUploadError() {
  uploading.value = false;
  ElMessage.error('上传失败，请重试');
}

function handleBeforeUpload() {
  // 清空上一次的检测结果
  taskId.value = null;
  resultImage.value = null;
  detections.value = [];
  return true;
}

// 获取检测结果
async function fetchResults(tid: string) {
  try {
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/results/${tid}`);
    const data = await resp.json();
    if (resp.ok && data?.code === 200) {
      const result = data.data;
      resultImage.value = result.resultImage;
      detections.value = Array.isArray(result.results) ? result.results : [];
    } else {
      const msg = data?.msg || '获取检测结果失败';
      throw new Error(msg);
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取检测结果失败');
  }
}
</script>

<template>
  <div class="p-24px">
    <ElCard class="yolo-card">
      <template #header>
        <div class="flex items-center gap-8px">
          <div class="text-20px font-700">YOLO 检测</div>
          <div class="text-14px color-gray-6">上传后可预览，点击“开始检测”再检测</div>
        </div>
      </template>

      <ElRow :gutter="16">
      <!-- 左侧：上传与预览区 -->
      <ElCol :span="10">
        <ElCard shadow="never" class="h-full">
          <div class="text-16px font-600 mb-12px">上传图片</div>
          <ElUpload
            ref="uploadRef"
            class="upload-area"
            drag
            :action="`${YOLO_BASE_URL}/yolo/upload`"
            name="image"
            :auto-upload="false"
            :limit="1"
            :file-list="fileList"
            :multiple="false"
            accept="image/*"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="handleBeforeUpload"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :on-exceed="handleExceed"
          >
            <div class="upload-inner">
              <template v-if="previewUrl">
                <div class="fixed-box small">
                  <ElImage :src="previewUrl" fit="contain" class="preview-image"/>
                </div>
                <div class="text-12px color-gray-6 mt-6px">已选择图片，点击或拖拽可更换</div>
              </template>
              <template v-else>
                <div class="fixed-box">
                  <div class="placeholder">
                    <div class="text-16px">点击或拖拽图片到此处</div>
                    <div class="text-12px color-gray-6 mt-6px">仅支持单张图片</div>
                  </div>
                </div>
              </template>
            </div>
          </ElUpload>

          <div class="mt-16px flex items-center gap-8px">
            <ElButton type="primary" :disabled="!selectedFile || uploading" @click="startDetect">
              {{ uploading ? '检测中...' : '开始检测' }}
            </ElButton>
            <ElButton :disabled="uploading" @click="handleFileRemove">清空</ElButton>
          </div>
        </ElCard>
      </ElCol>

      <!-- 右侧：检测结果（仅显示图片） -->
      <ElCol :span="14">
        <ElCard shadow="never" class="h-full">
          <div class="text-16px font-600 mb-12px">检测结果</div>
          <div v-if="!resultImage" class="color-gray-6">请先上传图片并点击“开始检测”</div>
          <div v-else class="result-area">
            <div class="fixed-box">
              <ElImage :src="resultImage" fit="contain" class="result-image"/>
            </div>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 底部全宽：检测详情 -->
    <div class="mt-16px">
      <ElCard shadow="never">
        <div class="text-16px font-600 mb-12px">检测详情</div>
        <ElTable :data="detections" size="small" border stripe v-if="detections.length">
          <ElTableColumn prop="class" label="类别" width="160" />
          <ElTableColumn prop="confidence" label="置信度" width="120" />
          <ElTableColumn prop="bbox" label="BBox(x1,y1,x2,y2)" />
        </ElTable>
        <div v-else class="text-13px color-gray-6">暂无数据</div>
      </ElCard>
    </div>
    </ElCard>
  </div>
</template>

<style scoped>
.yolo-card {
  min-height: 560px;
}
.upload-area {
  width: 100%;
}
.upload-inner {
  padding: 8px 0;
}
.fixed-box {
  width: 100%;
  aspect-ratio: 4 / 3;
  background: #f5f7fa;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  max-height: 360px;
}
.placeholder {
  text-align: center;
  color: #909399;
}
.fixed-box.large {
   height: 320px;
 }

 .preview-image,
 .result-image {
   width: 94%;
   height: 94%;
 }

.fixed-box.small {
  height: 200px;
}
</style>