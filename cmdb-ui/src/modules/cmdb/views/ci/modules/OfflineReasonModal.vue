<template>
  <a-modal
    :visible="visible"
    :title="$t('cmdb.ci.offlineConfirmTitle')"
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
        :message="$t('cmdb.ci.offlineConfirmTip')"
        type="warning"
        show-icon
        style="margin-bottom: 16px;"
      />

      <a-form-model-item
        :label="$t('cmdb.ci.offlineReason')"
        prop="reason"
      >
        <a-textarea
          v-model="form.reason"
          :placeholder="$t('cmdb.ci.offlineReasonPlaceholder')"
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
  name: 'OfflineReasonModal',
  data() {
    return {
      visible: false,
      currentCI: {},
      ciDisplayName: '',
      form: {
        reason: ''
      }
    }
  },
  methods: {
    open(ci, ciName) {
      this.visible = true
      this.currentCI = ci || {}
      this.ciDisplayName = ciName || ci?.name || `CI #${ci?._id || ci?.ci_id || '?'}`
      this.form.reason = ''
    },

    handleCancel() {
      this.visible = false
      this.form.reason = ''
      this.currentCI = {}
      this.ciDisplayName = ''
    },

    handleOk() {
      this.$emit('ok', {
        ci: this.currentCI,
        reason: this.form.reason
      })
      this.handleCancel()
    }
  }
}
</script>
