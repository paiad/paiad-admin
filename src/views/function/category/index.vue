<template>
  <div class="category-list-container">
    <div class="toolbar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="类目编号">
          <el-input v-model="searchForm.id" placeholder="请输入类目编号" clearable></el-input>
        </el-form-item>
        <el-form-item label="类目名称">
          <el-input v-model="searchForm.name" placeholder="请输入类目名称" clearable></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      <el-button type="success" :icon="Plus" @click="handleAdd">添加类目</el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border style="width: 100%">
      <el-table-column prop="id" label="编号" width="80" align="center"></el-table-column>
      <el-table-column prop="name" label="类目名称" width="180"></el-table-column>
      <el-table-column label="类目图片" width="120" align="center">
        <template #default="scope">
          <el-image
            class="category-image"
            :src="scope.row.imageUrl"
            :preview-src-list="[scope.row.imageUrl]"
            fit="cover"
            hide-on-click-modal
            preview-teleported
          ></el-image>
        </template>
      </el-table-column>
      <el-table-column prop="sortOrder" label="排序" width="80" align="center"></el-table-column>
      <el-table-column prop="parentId" label="父类ID" width="100" align="center">
        <template #default="scope">
          {{ scope.row.parentId === 0 ? '顶级类目' : scope.row.parentId }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
            {{ scope.row.status === 1 ? '已上架' : '已下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" min-width="150" align="center">
        <template #default="scope">
          <el-button type="primary" link :icon="Edit" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="danger" link :icon="Delete" @click="handleDelete(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="pagination"
      :current-page="pagination.currentPage"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    ></el-pagination>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @close="resetForm">
      <el-form ref="categoryFormRef" :model="categoryForm" :rules="categoryFormRules" label-width="100px">
        <el-form-item label="类目名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入类目名称"></el-input>
        </el-form-item>
        <el-form-item label="父级类目" prop="parentId">
          <el-select v-model="categoryForm.parentId" placeholder="请选择父级类目">
            <el-option label="顶级类目" :value="0"></el-option>
            <el-option
              v-for="item in parentCategoryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number v-model="categoryForm.sortOrder" :min="0" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="categoryForm.status">
            <el-radio :label="1">上架</el-radio>
            <el-radio :label="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="类目图片" prop="imageUrl">
          <el-input v-model="categoryForm.imageUrl" placeholder="请输入图片URL"></el-input>
          <p class="tip">提示：实际项目中应使用 el-upload 组件上传图片。</p>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus';
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue';

// --- 数据模型定义 ---
interface Category {
  id: number;
  name: string;
  imageUrl: string;
  sortOrder: number;
  parentId: number;
  status: 0 | 1; // 0:下架, 1:上架
}

// --- 模拟后端数据库 ---
const allCategories = ref<Category[]>([
  { id: 1, name: '潮流服饰', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ce1.jpg', sortOrder: 1, parentId: 0, status: 1 },
  { id: 2, name: '数码家电', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ce2.png', sortOrder: 2, parentId: 0, status: 1 },
  { id: 3, name: '男士T恤', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ce3.png', sortOrder: 10, parentId: 1, status: 1 },
  { id: 4, name: '智能手机', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ce4.png', sortOrder: 5, parentId: 2, status: 1 },
  { id: 5, name: '女士裙装', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ce5.png', sortOrder: 12, parentId: 1, status: 0 },
  { id: 6, name: '笔记本电脑', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ce6.png', sortOrder: 8, parentId: 2, status: 1 },
]);

// --- 响应式状态 ---
const loading = ref(false);
const tableData = ref<Category[]>([]);
const searchForm = reactive({ id: '', name: '' });
const pagination = reactive({ currentPage: 1, pageSize: 10, total: 0 });

// --- 弹窗与表单 ---
const dialogVisible = ref(false);
const dialogTitle = ref('');
const categoryFormRef = ref<FormInstance>();
const categoryForm = reactive<Omit<Category, 'id'>>({
  name: '',
  imageUrl: '',
  sortOrder: 99,
  parentId: 0,
  status: 1,
});
// 存储当前编辑的ID，如果是null则为新增
let currentEditId: number | null = null;

const categoryFormRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入类目名称', trigger: 'blur' }],
  parentId: [{ required: true, message: '请选择父级类目', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
});

// 计算可作为父类的选项（所有顶级类目）
const parentCategoryOptions = computed(() =>
  allCategories.value.filter(cat => cat.parentId === 0)
);


// --- 方法 ---

// 模拟API获取数据
const fetchData = () => {
  loading.value = true;
  setTimeout(() => {
    let filteredData = allCategories.value;

    // 搜索过滤
    if (searchForm.id) {
      filteredData = filteredData.filter(item => item.id === Number(searchForm.id));
    }
    if (searchForm.name) {
      filteredData = filteredData.filter(item => item.name.includes(searchForm.name));
    }

    // 分页
    pagination.total = filteredData.length;
    const startIndex = (pagination.currentPage - 1) * pagination.pageSize;
    const endIndex = startIndex + pagination.pageSize;
    tableData.value = filteredData.slice(startIndex, endIndex);

    loading.value = false;
  }, 500);
};

// 页面加载时获取初始数据
onMounted(fetchData);

// 搜索
const handleSearch = () => {
  pagination.currentPage = 1;
  fetchData();
};

// 重置搜索
const handleReset = () => {
  searchForm.id = '';
  searchForm.name = '';
  handleSearch();
};

// 分页大小改变
const handleSizeChange = (val: number) => {
  pagination.pageSize = val;
  fetchData();
};

// 当前页改变
const handleCurrentChange = (val: number) => {
  pagination.currentPage = val;
  fetchData();
};

// 重置表单
const resetForm = () => {
  currentEditId = null;
  Object.assign(categoryForm, {
    name: '', imageUrl: '', sortOrder: 99, parentId: 0, status: 1
  });
  categoryFormRef.value?.clearValidate();
}

// 添加
const handleAdd = () => {
  resetForm();
  dialogTitle.value = '添加新类目';
  dialogVisible.value = true;
};

// 编辑
const handleEdit = (row: Category) => {
  resetForm();
  currentEditId = row.id;
  Object.assign(categoryForm, row);
  dialogTitle.value = `编辑类目 - ${row.name}`;
  dialogVisible.value = true;
};

// 删除
const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除这个类目吗？子类目不会被删除。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    // 模拟删除
    const index = allCategories.value.findIndex(item => item.id === id);
    if (index !== -1) {
      allCategories.value.splice(index, 1);
      ElMessage.success('删除成功');
      fetchData(); // 刷新表格
    }
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

// 提交表单（添加/编辑）
const submitForm = () => {
  categoryFormRef.value?.validate((valid) => {
    if (valid) {
      if (currentEditId === null) {
        // --- 新增逻辑 ---
        const newCategory: Category = {
          id: Math.max(...allCategories.value.map(c => c.id), 0) + 1, // 模拟自增ID
          ...categoryForm,
        };
        allCategories.value.unshift(newCategory); // 加到最前面
        ElMessage.success('添加成功');
      } else {
        // --- 编辑逻辑 ---
        const index = allCategories.value.findIndex(item => item.id === currentEditId);
        if (index !== -1) {
          allCategories.value[index] = { ...allCategories.value[index], ...categoryForm };
          ElMessage.success('编辑成功');
        }
      }
      dialogVisible.value = false;
      fetchData(); // 重新加载数据
    } else {
      ElMessage.error('请检查表单输入');
      return false;
    }
  });
};
</script>

<style lang="scss" scoped>
.category-list-container {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.category-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>
