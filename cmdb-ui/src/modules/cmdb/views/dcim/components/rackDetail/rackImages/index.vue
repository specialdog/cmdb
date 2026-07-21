<template>
  <div class="rack-images">
    <!-- 上传区域 -->
    <div class="upload-section">
      <a-upload
        list-type="picture-card"
        class="rack-image-uploader"
        :before-upload="beforeUpload"
        :customRequest="customUpload"
        :show-upload-list="false"
        accept="image/*"
        :multiple="true"
        :max-count="6"
      >
        <div v-if="fileList.length < 6" class="upload-button">
          <a-icon type="plus" />
          <div class="ant-upload-text">{{ $t('cmdb.dcim.uploadImages') }}</div>
        </div>
      </a-upload>
      <!-- 上传提示 -->
      <div class="upload-tips">
        <a-icon type="info-circle" />
        <span>支持jpg、png、gif格式, 单张图片不超过30MB, 最多上传6张</span>
      </div>
    </div>

    <!-- 已上传图片区域 -->
    <div v-if="fileList.length > 0" class="preview-section">
      <h3 class="section-title">{{ $t('cmdb.dcim.uploadedImages') }}</h3>

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
                size="mini"
                @click="handlePreview(file)"
              >
                <a-icon type="eye" />原图</a-button>
              <a-button
                type="link"
                size="mini"
                danger
                @click="deleteImage(file)"
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
      @cancel="previewVisible = false"
      width="800px"
    >
      <img :src="previewImage" style="width: 100%"/>
    </a-modal>
  </div>
</template>

<script>
import { getRackImages, uploadRackImage, deleteRackImage } from '@/modules/cmdb/api/dcim.js'

export default {
  name: 'RackImages',
  props: {
    rackId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      fileList: [],
      previewVisible: false,
      previewImage: null,
      uploading: false
    }
  },
  mounted() {
    this.loadImages()
  },
  methods: {
    async loadImages() {
      try {
        const response = await getRackImages(this.rackId)
        this.fileList = (response.images || []).map((item, index) => ({
          uid: item.id || index,
          name: item.filename || `image_${index}`,
          status: 'done',
          url: item.base64
        }))
      } catch (error) {
        this.$message.error('加载图片失败')
      }
    },

    beforeUpload(file) {
      const isImage = file.type.startsWith('image/')
      if (!isImage) {
        this.$message.error('只能上传图片文件!')
        return false
      }

      const isLt30M = file.size / 1024 / 1024 < 30
      if (!isLt30M) {
        this.$message.error('图片大小不能超过 30MB!')
        return false
      }

      return true
    },

    customUpload(options) {
      const { file, onSuccess, onError } = options
      const formData = new FormData()
      formData.append('file', file)
      uploadRackImage(this.rackId, formData).then(response => {
        onSuccess(response, file)
        this.$message.success('图片上传成功')
        this.loadImages()
      }).catch(error => {
        onError(error)
        this.$message.error('图片上传失败')
      })
    },

    handlePreview(image) {
      this.previewImage = image.url
      this.previewVisible = true
    },

    async deleteImage(image) {
      this.$confirm({
        title: '确认删除',
        content: `确定要删除图片 "${image.name}" 吗？`,
        onOk: async () => {
          try {
            await deleteRackImage(this.rackId, { 'filename': image.name })
            this.$message.success('图片删除成功')
            this.loadImages()
          } catch (error) {
            this.$message.error('图片删除失败')
          }
        }
      })
    }
  }
}
</script>

<style lang="less" scoped>
.rack-images {
  padding: 20px;

  .upload-section {
    margin-bottom: 30px;

    h3 {
      margin-bottom: 16px;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .rack-image-uploader {
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

  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    color: @text-color_1;
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
        padding: 2px;
        display: flex;
        justify-content: space-around;
        gap: 6px;

        .ant-btn-link {
          padding: 0 2px;
          height: auto;
          line-height: 1.2;
          font-size: 12px;

          .anticon {
            margin-right: 1px;
          }
        }
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
}
</style>
