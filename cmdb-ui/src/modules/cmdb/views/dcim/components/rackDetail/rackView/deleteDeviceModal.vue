<template>
  <a-modal
    :visible="visible"
    :title="$t('cmdb.dcim.removeDevice')"
    :width="500"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <a-form-model
      ref="formRef"
      :model="form"
      :label-col="{ span: 5 }"
      :wrapper-col="{ span: 19 }"
    >
      <a-alert
        :message="$t('cmdb.dcim.removeDeviceTip')"
        type="warning"
        show-icon
        style="margin-bottom: 16px;"
      />

      <a-form-model-item :label="$t('cmdb.dcim.deviceName')">
        <span>{{ currentDevice.name }}</span>
      </a-form-model-item>

      <a-form-model-item
        :label="$t('cmdb.dcim.operationReason')"
        prop="reason"
      >
        <a-textarea
          v-model="form.reason"
          :placeholder="$t('cmdb.dcim.reasonPlaceholder')"
          :rows="4"
          :maxLength="500"
          show-count
        />
      </a-form-model-item>
    </a-form-model>
  </a-modal>
</template>

<script>
export default {
  name: 'DeleteDeviceModal',
  data() {
    return {
      visible: false,
      currentDevice: {},
      form: {
        reason: ''
      }
    }
  },
  methods: {
    open(device) {
      this.visible = true
      this.currentDevice = device
      this.form.reason = ''
    },

    handleCancel() {
      this.visible = false
      this.form.reason = ''
      this.currentDevice = {}
    },

    handleOk() {
      // 返回设备信息和原因
      this.$emit('ok', {
        device: this.currentDevice,
        reason: this.form.reason
      })
      this.handleCancel()
    }
  }
}
</script>
