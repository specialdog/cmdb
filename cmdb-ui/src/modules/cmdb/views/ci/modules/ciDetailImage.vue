<template>
  <div class="ci-detail-image">
    <div :style="{ padding: '24px', height: '100%' }">
      <div class="ci-detail-image-content">
        <!-- 上传区域 -->
        <div class="upload-section">
          <a-upload
            name="file"
            list-type="picture-card"
            class="ci-detail-image-uploader"
            :customRequest="customUpload"
            :before-upload="beforeUpload"
            accept="image/*"
            :multiple="true"
            :max-count="6"
            :showUploadList="false"
          >
            <div v-if="fileList.length < 6" class="upload-button">
              <a-icon type="plus" />
              <div class="ant-upload-text">上传图片</div>
            </div>
          </a-upload>

          <!-- 上传提示 -->
          <div class="upload-tips">
            <a-icon type="info-circle" />
            <span>支持jpg、png、gif格式, 单张图片不超过10MB, 最多上传6张</span>
          </div>
        </div>

        <!-- 图片预览区域 -->
        <div v-if="fileList.length > 0" class="preview-section">
          <h3 class="section-title">已上传图片</h3>

          <a-row :gutter="[16, 16]">
            <a-col
              v-for="(file, index) in fileList"
              :key="file.uid || index"
              :xs="12"
              :sm="8"
              :md="6"
              :lg="4"
            >
              <div class="image-card">
                <img
                  :src="file.url"
                  class="preview-image"
                />
                <div class="image-card-actions">
                  <a-button
                    type="link"
                    size="small"
                    @click="handlePreview(file)"
                  >
                    <a-icon type="eye"/>原图</a-button>
                  <a-button
                    type="link"
                    size="small"
                    danger
                    @click="handleRemove(file)"
                  >
                    <a-icon type="delete"/>删除</a-button>
                </div>
              </div>
            </a-col>
          </a-row>
        </div>

        <!-- 预览模态框 -->
        <a-modal
          :visible="previewVisible"
          :footer="null"
          :width="800"
          :title="previewTitle"
          @cancel="handlePreviewCancel"
        >
          <img style="width: 100%; height: auto;" :src="previewImage"/>
        </a-modal>

      </div>
    </div>
  </div>
</template>

<script>
import { message } from 'ant-design-vue'
import { getCIImage, deleteCIImage, uploadCIImage } from '@/modules/cmdb/api/ci'

export default {
  name: 'CiDetailImage',
  props: {
    ci: {
      type: Object,
      default: () => {}
    },
    ciId: {
      type: [String, Number],
      required: true
    },
    typeId: {
      type: [String, Number],
      required: true
    },
    attributeGroups: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      fileList: [],
      previewVisible: false,
      previewImage: '',
      previewTitle: '',
      zh2pinyin: {
        '202机房A': '202jifangA',
        '202机房B': '202jifangB',
        '202机房C': '202jifangC' }
    }
  },
  computed: {
    uploadUrl() {
      return `v0.1/citypes/${this.typeId}/devimg`
    },
    uploadData() {
      // 获取硬件组中的属性值
      const hardwareInfo = this.getHardwareInfo()
      return {
        server_room: this.zh2pinyin[hardwareInfo.server_room] || '',
        rack: hardwareInfo.rack || '',
        sn: hardwareInfo.sn || ''
      }
    }
  },
  mounted() {
    this.loadDeviceImages()
  },
  methods: {
    customUpload(options) {
      const { file, onSuccess, onError } = options
      const formData = new FormData()
      formData.append('file', file)
      // 添加设备信息
      const hardwareInfo = this.getHardwareInfo()
      formData.append('server_room', hardwareInfo.server_room || '')
      formData.append('rack', hardwareInfo.rack || '')
      formData.append('sn', hardwareInfo.sn || '')
      uploadCIImage(this.uploadUrl, formData).then(response => {
        onSuccess(response, file)
        message.success('上传成功')
        this.loadDeviceImages()
      }).catch(error => {
        onError(error)
        message.error('上传失败，请重试')
      })
    },

    getHardwareInfo() {
      const result = {
        server_room: this.zh2pinyin[this.ci['server_room']],
        rack: this.ci['rack'],
        sn: this.ci['sn']
      }
      return result
    },

    // 加载设备已有图片
    async loadDeviceImages() {
      try {
        const response = await getCIImage(this.uploadUrl, this.getHardwareInfo())
        this.fileList = (response.images || []).map((item, index) => ({
          uid: item.id || index,
          name: item.filename || `image_${index}`,
          status: 'done',
          url: item.base64
        }))
      } catch (error) {
        message.error('加载设备图片失败:', error)
      }
    },

    // 上传前检查
    beforeUpload(file) {
      const isImage = file.type.startsWith('image/')
      if (!isImage) {
        message.error('只能上传图片文件!')
        return false
      }

      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        message.error('图片大小不能超过10MB!')
        return false
      }

      // 检查必要的信息是否存在
      const hardwareInfo = this.getHardwareInfo()
      const keyInfo = ['server_room', 'rack', 'sn']
      keyInfo.forEach(item => {
        if (!hardwareInfo[item]) {
            message.error(`缺少设备${item}信息, 无法上传图片!`)
            return false
        }
      })

      return true
    },

    // 预览图片
    handlePreview(file) {
      this.previewImage = file.url
      this.previewVisible = true
    },

    // 关闭预览
    handlePreviewCancel() {
      this.previewVisible = false
    },

    // 删除图片
    handleRemove(file) {
      try {
        const deleteFileData = Object.assign({}, this.getHardwareInfo(), { 'filename': file.name })
        deleteCIImage(this.uploadUrl, deleteFileData).then(response => {
          this.loadDeviceImages()
          message.success('图片删除成功')
        })
      } catch (error) {
        message.error('删除图片失败')
      }
    }
  }
}
</script>

<style lang="less" scoped>
.ci-detail-image {
  height: 100%;

  &-content {
    max-width: 1200px;
  }

  .upload-section {
    margin-bottom: 32px;
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    color: @text-color_1;
  }

  .ci-detail-image-uploader {
    .upload-button {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 104px;
      color: @text-color_3;

      .anticon {
        font-size: 32px;
        margin-bottom: 8px;
      }
    }
  }

  .upload-tips {
    margin-top: 8px;
    color: @text-color_3;
    font-size: 12px;

    .anticon {
      margin-right: 4px;
    }
  }

  .preview-section {
    .image-card {
      border: 1px solid @border-color-base;
      border-radius: 6px;
      overflow: hidden;
      transition: all 0.3s;

      &:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }

      .preview-image {
        width: 100%;
        object-fit: cover;
      }

      &-actions {
        padding: 8px;
        display: flex;
        justify-content: space-around;
      }
    }
  }

  .preview-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    min-height: 200px; /* 避免图片未加载时容器过窄 */
  }

  .empty-state {
    text-align: center;
    padding: 40px 0;
  }
}

// 上传组件样式调整
:deep(.ant-upload-select-picture-card) {
  width: 104px;
  height: 104px;
}

:deep(.ant-upload-list-picture-card .ant-upload-list-item) {
  width: 104px;
  height: 104px;
}
</style>
