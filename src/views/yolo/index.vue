<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import type { UploadFile, UploadInstance } from 'element-plus';
import { ElMessage } from 'element-plus';
import { $t } from '@/locales';

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

// 新增：模型选择与置信度阈值
const availableModels = [
  { label: 'yolo11n.pt', value: 'yolo11n.pt' },
  { label: 'yolo11s.pt', value: 'yolo11s.pt' },
  { label: 'yolo11m.pt', value: 'yolo11m.pt' },
  { label: 'yolo11l.pt', value: 'yolo11l.pt' },
  { label: 'yolo11x.pt', value: 'yolo11x.pt' },
];
const selectedModel = ref<string>(availableModels[0].value);
const confidence = ref<number>(0.25);

// 历史记录相关状态与方法
interface HistoryItem {
  file_id: string;
  file_name: string;
  upload_time?: string;
  width?: number;
  height?: number;
  file_type?: string;
  url: string;
}
const historyList = ref<HistoryItem[]>([]);
const historyLoading = ref(false);
const historyPage = ref(1);
const historyPageSize = ref(5);
const historyTotal = computed(() => historyList.value.length);
const sortOrder = ref<'asc' | 'desc'>('desc');
const sortedHistory = computed(() => {
  const list = [...historyList.value];
  list.sort((a, b) => {
    const atRaw = a.upload_time ? Date.parse(a.upload_time) : 0;
    const btRaw = b.upload_time ? Date.parse(b.upload_time) : 0;
    const at = isNaN(atRaw) ? 0 : atRaw;
    const bt = isNaN(btRaw) ? 0 : btRaw;
    return sortOrder.value === 'desc' ? bt - at : at - bt;
  });
  return list;
});
const pagedHistory = computed(() => {
  const start = (historyPage.value - 1) * historyPageSize.value;
  const end = start + historyPageSize.value;
  return sortedHistory.value.slice(start, end);
});
watch(sortOrder, () => {
  historyPage.value = 1;
});

const previewVisible = ref(false);
const previewItem = ref<HistoryItem | null>(null);

function openPreview(item: HistoryItem) {
  previewItem.value = item;
  previewVisible.value = true;
}

function formatTime(t: string) {
  try {
    return new Date(t).toLocaleString();
  } catch {
    return t;
  }
}

async function fetchHistory() {
  historyLoading.value = true;
  try {
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/history`);
    const data = await resp.json();
    if (resp.ok && data?.code === 200) {
      historyList.value = Array.isArray(data.data) ? data.data : [];
      const pageCount = Math.max(1, Math.ceil(historyTotal.value / historyPageSize.value));
      if (historyPage.value > pageCount) historyPage.value = pageCount;
    } else {
      throw new Error(data?.msg || $t('page.yolo.errors.fetchHistoryFail'));
    }
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.fetchHistoryFail'));
  } finally {
    historyLoading.value = false;
  }
}

async function deleteHistory(item: HistoryItem) {
  try {
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/history/${item.file_id}`, { method: 'DELETE' });
    const data = await resp.json();
    if (resp.ok && data?.code === 200) {
      historyList.value = historyList.value.filter(h => h.file_id !== item.file_id);
      ElMessage.success($t('common.deleteSuccess'));
      const pageCount = Math.max(1, Math.ceil(historyTotal.value / historyPageSize.value));
      if (historyPage.value > pageCount) historyPage.value = pageCount;
    } else {
      throw new Error(data?.msg || $t('page.yolo.errors.deleteFail'));
    }
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.deleteFail'));
  }
}

onMounted(() => {
  fetchHistory();
});

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
    ElMessage.warning($t('page.yolo.errors.noFileSelected'));
    return;
  }
  uploading.value = true;
  try {
    const fd = new FormData();
    fd.append('image', selectedFile.value.raw);
    // 将模型名称与置信度作为查询参数传递
    const query = new URLSearchParams({
      model_name: selectedModel.value,
      conf: confidence.value.toString(),
    }).toString();
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/upload?${query}`, {
      method: 'POST',
      body: fd,
    });
    const data = await resp.json();
    const code = data?.code;
    const tid = data?.data?.taskId as string | undefined;
    if (!resp.ok || code !== 200 || !tid) {
      throw new Error(data?.msg || $t('page.yolo.errors.uploadFail'));
    }
    taskId.value = tid;
    await fetchResults(tid);
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.detectFail'));
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
      throw new Error($t('page.yolo.errors.uploadDataInvalid'));
    }
    taskId.value = tid;
    // 上传完成后再获取检测结果
    await fetchResults(tid);
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.parseUploadResultFail'));
  } finally {
    uploading.value = false;
  }
}

function handleUploadError() {
  uploading.value = false;
  ElMessage.error($t('page.yolo.errors.uploadFail'));
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
      await fetchHistory();
    } else {
      const msg = data?.msg || $t('page.yolo.errors.fetchResultFail');
      throw new Error(msg);
    }
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.fetchResultFail'));
  }
}
</script>

<template>
  <div class="p-24px">
    <ElCard class="yolo-card">
      <template #header>
        <div class="flex items-center gap-8px">
          <div class="text-20px font-700">{{ $t('page.yolo.title') }}</div>
          <div class="text-14px color-gray-6">{{ $t('page.yolo.subtitle') }}</div>
        </div>
      </template>

      <ElRow :gutter="16">
      <!-- 左侧：上传与预览区 -->
      <ElCol :span="10">
        <ElCard shadow="never" class="h-full">
          <div class="text-16px font-600 mb-12px">{{ $t('page.yolo.upload.title') }}</div>
          <!-- 新增：参数设置（模型与置信度） -->
          <div class="mb-12px flex items-center gap-12px">
            <div class="flex items-center gap-6px">
              <span class="text-12px color-gray-6">{{ $t('page.yolo.settings.model') }}</span>
              <ElSelect v-model="selectedModel" size="small" style="width: 100px">
                <ElOption v-for="m in availableModels" :key="m.value" :label="m.label" :value="m.value" />
              </ElSelect>
            </div>
            <div class="flex items-center gap-6px" style="flex:1">
              <span class="text-12px color-gray-6">{{ $t('page.yolo.settings.confidence') }}</span>
              <ElSlider v-model="confidence" :min="0" :max="1" :step="0.01" show-input size="small" style="width: 240px"/>
            </div>
          </div>

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
                <div class="text-12px color-gray-6 mt-6px">{{ $t('page.yolo.upload.selectedTips') }}</div>
              </template>
              <template v-else>
                <div class="fixed-box">
                  <div class="placeholder">
                    <div class="text-16px">{{ $t('page.yolo.upload.dropTips') }}</div>
                    <div class="text-12px color-gray-6 mt-6px">{{ $t('page.yolo.upload.singleOnly') }}</div>
                  </div>
                </div>
              </template>
            </div>
          </ElUpload>

          <div class="mt-16px flex items-center gap-8px">
            <ElButton type="primary" :disabled="!selectedFile || uploading" @click="startDetect">
              {{ uploading ? $t('page.yolo.buttons.detecting') : $t('page.yolo.buttons.startDetect') }}
            </ElButton>
            <ElButton :disabled="uploading" @click="handleFileRemove">{{ $t('common.reset') }}</ElButton>
          </div>
        </ElCard>
      </ElCol>

      <!-- 右侧：检测结果（仅显示图片） -->
      <ElCol :span="14">
        <ElCard shadow="never" class="h-full">
          <div class="text-16px font-600 mb-12px">{{ $t('page.yolo.result.title') }}</div>
          <div v-if="!resultImage" class="color-gray-6">{{ $t('page.yolo.result.emptyTips') }}</div>
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
        <div class="text-16px font-600 mb-12px">{{ $t('page.yolo.detail.title') }}</div>
        <ElTable :data="detections" size="small" border stripe v-if="detections.length">
          <ElTableColumn prop="class" :label="$t('page.yolo.detail.columns.class')" width="160">
            <template #default="{ row }">
              <ElTag type="primary">{{ row.class }}</ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="confidence" :label="$t('page.yolo.detail.columns.confidence')" width="160">
            <template #default="{ row }">
              <ElTag :type="row.confidence >= 0.8 ? 'success' : row.confidence >= 0.5 ? 'warning' : 'danger'">
                {{ (row.confidence * 100).toFixed(1) }}%
              </ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="bbox" :label="$t('page.yolo.detail.columns.bbox')">
            <template #default="{ row }">
              <span class="bbox-text">{{ Array.isArray(row.bbox) ? row.bbox.join(', ') : row.bbox }}</span>
            </template>
          </ElTableColumn>
        </ElTable>
        <div v-else class="text-13px color-gray-6">{{ $t('common.noData') }}</div>
      </ElCard>
    </div>

    <!-- 历史检测记录 -->
    <div class="mt-16px">
      <ElCard shadow="never">
        <div class="flex items-center justify-between mb-12px">
          <div class="text-16px font-600">{{ $t('page.yolo.history.title') }}</div>
          <div class="flex items-center gap-8px">
            <ElButton size="small" :loading="historyLoading" @click="fetchHistory">{{ $t('common.refresh') }}</ElButton>
            <div class="flex items-center gap-6px">
              <span class="text-12px color-gray-6">{{ $t('page.yolo.sortByTime.label') }}</span>
              <ElButtonGroup>
                <ElButton size="small" :type="sortOrder === 'desc' ? 'primary' : 'default'" @click="sortOrder = 'desc'">{{ $t('page.yolo.sortByTime.latestFirst') }}</ElButton>
                <ElButton size="small" :type="sortOrder === 'asc' ? 'primary' : 'default'" @click="sortOrder = 'asc'">{{ $t('page.yolo.sortByTime.oldestFirst') }}</ElButton>
              </ElButtonGroup>
            </div>
          </div>
        </div>
        <div v-if="historyLoading" class="text-13px color-gray-6">{{ $t('page.yolo.loading') }}</div>
        <template v-else>
          <div v-if="historyList.length" class="history-list">
            <div v-for="item in pagedHistory" :key="item.file_id" class="history-row">
              <div class="thumb-box-row" @click="openPreview(item)">
                <ElImage :src="item.url" fit="cover" class="thumb-image-row" />
              </div>
              <div class="row-content">
                <div class="row-title"><ElTag type="success" size="small" class="filename-tag ellipsis">{{ item.file_name }}</ElTag></div>
                <div class="row-meta text-12px color-gray-6">
                  <span v-if="item.width && item.height">{{ $t('page.yolo.meta.resolution') }} {{ item.width }} x {{ item.height }}</span>
                  <span v-if="item.file_type" class="ml-8px">{{ $t('page.yolo.meta.type') }} {{ item.file_type }}</span>
                  <ElTag v-if="item.upload_time" size="small" type="primary" class="ml-8px time-tag">{{ $t('page.yolo.meta.upload') }} {{ formatTime(item.upload_time) }}</ElTag>
                </div>
              </div>
              <div class="row-actions">
                <ElButton size="small" @click="openPreview(item)">{{ $t('page.yolo.actions.preview') }}</ElButton>
                <ElPopconfirm :title="$t('page.yolo.confirm.deleteHistory')" @confirm="deleteHistory(item)">
                  <template #reference>
                    <ElButton size="small" type="danger" plain>{{ $t('common.delete') }}</ElButton>
                  </template>
                </ElPopconfirm>
              </div>
            </div>
          </div>
          <div v-else class="text-13px color-gray-6">{{ $t('page.yolo.history.empty') }}</div>
          <div class="mt-12px flex justify-end" v-if="historyList.length">
            <ElPagination
              layout="prev, pager, next, jumper, sizes"
              :total="historyTotal"
              :page-size="historyPageSize"
              :current-page="historyPage"
              :page-sizes="[5, 10, 15, 20]"
              @size-change="val => historyPageSize = val"
              @current-change="val => historyPage = val"
            />
          </div>
        </template>
      </ElCard>
    </div>

    <!-- 预览弹窗 -->
    <ElDialog v-model="previewVisible" width="50%" :title="$t('page.yolo.previewDialog.title')">
      <div v-if="previewItem">
        <div class="fixed-box large" style="max-height: 480px">
          <ElImage :src="previewItem.url" fit="contain" class="result-image" />
        </div>
        <div class="mt-12px text-13px color-gray-7">
          <div>{{ $t('page.yolo.previewDialog.fileName') }} {{ previewItem.file_name }}</div>
          <div>{{ $t('page.yolo.previewDialog.resolution') }} {{ previewItem.width }} x {{ previewItem.height }}</div>
          <div>{{ $t('page.yolo.previewDialog.type') }} {{ previewItem.file_type }}</div>
          <div>{{ $t('page.yolo.previewDialog.uploadTime') }} {{ formatTime(previewItem.upload_time) }}</div>
          <div>{{ $t('page.yolo.previewDialog.url') }} {{ previewItem.url }}</div>
        </div>
      </div>
      <template #footer>
        <ElButton @click="previewVisible=false">{{ $t('common.close') }}</ElButton>
      </template>
    </ElDialog>

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
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.history-row {
  display: grid;
  grid-template-columns: 120px 1fr auto;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  padding: 8px;
}
.thumb-box-row {
  width: 120px;
  height: 90px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
}
.thumb-image-row {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.row-content {
  min-width: 0;
}
.row-title {
   font-size: 13px;
   color: var(--el-text-color-primary);
   display: flex;
   align-items: center;
   min-width: 0;
 }
 .filename-tag {
   max-width: 100%;
   display: inline-block;
   overflow: hidden;
   text-overflow: ellipsis;
   white-space: nowrap;
 }
 .row-meta span + span {
   margin-left: 8px;
 }
.row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ellipsis {
   overflow: hidden;
   text-overflow: ellipsis;
   white-space: nowrap;
 }
 .time-tag {
   font-weight: 600;
 }
</style>
