<template>
  <div class="rack-container">
    <div class="rack-title">
      <ops-icon
        :type="titleData.icon"
        class="rack-title-icon"
      />
      <span
        class="rack-title-text"
      >
        {{ $t(titleData.text) }}
      </span>
    </div>

    <RackHeader :viewType="viewType" />

    <div
      class="rack-container-main"
      :style="{
        flexDirection: viewType === 'front' ? 'row' : 'row-reverse'
      }"
    >
      <div class="rack-container-main-left">
        <div
          v-for="(item, index) in countList"
          :key="index"
          class="rack-container-main-left-count"
          :style="{
            backgroundColor: item % 2 === 0 ? '#3D4151' : '#5E6772',
            height: unitHeight + 'px',
            lineHeight: unitHeight + 'px'
          }"
        >
          {{ item }}
        </div>
      </div>

      <div class="rack-container-main-list">
        <draggable
          filter=".undraggable"
          :list="unitList"
          @start="handleDraggableStart"
          @end="handleDraggableEnd"
        >
          <div
            v-for="(item, index) in unitList"
            :key="item.key"
            :class="[item.type === 'gap' || item.abnormal ? 'undraggable' : '']"
          >
            <div
              v-if="item.type === 'device'"
              :class="['rack-container-main-list-device', item.abnormal ? '' : 'rack-container-main-list-device_normal']"
              :style="{
                height: unitHeight * item.unitCount + 'px'
              }"
              @click="clickDevice(item)"
            >
              <div
                v-if="viewType === 'front'"
                class="rack-container-main-list-device-action"
              >
                <div
                  class="rack-container-main-list-device-action-btn"
                  @click.stop="removeDevice(item)"
                >
                  {{ $t('cmdb.dcim.remove') }}
                </div>
                <div
                  class="rack-container-main-list-device-action-btn"
                  @click.stop="migrateDevice(item)"
                >
                  {{ $t('cmdb.dcim.migrate') }}
                </div>
              </div>

              <div
                v-if="item.abnormal"
                class="rack-container-main-list-device-abnormal"
              >
                <span
                  class="rack-container-main-list-device-abnormal-text"
                >
                  {{ $t('cmdb.dcim.unitAbnormal') }}
                </span>
                <a-icon
                  type="right"
                  class="rack-container-main-list-device-abnormal-icon"
                />
              </div>

              <div class="rack-container-main-list-device-header"></div>
              <img
                v-if="viewType === 'front'"
                :src="item.deviceImage[viewType]"
                class="rack-device-image"
                :style="{
                  height: (unitHeight * item.unitCount - 6) + 'px'
                }"
              />
              <div
                v-else
                class="rack-device-image-rear"
                :style="{
                  height: (unitHeight * item.unitCount - 6) + 'px'
                }"
              />

              <!-- 后视图：网口指示器 -->
              <div
                v-if="viewType === 'rear' && !isSwitchDevice(item) && getDeviceNetworkPorts(item._id).length > 0"
                class="rack-container-main-list-device-ports"
              >
                <a-popover
                  v-for="(port, portIndex) in getDeviceNetworkPorts(item._id)"
                  :key="portIndex"
                  trigger="hover"
                  placement="right"
                  :overlayStyle="{ maxWidth: '320px' }"
                >
                  <template slot="content">
                    <div class="port-popover">
                      <div class="port-popover-title">{{ $t('cmdb.dcim.networkPort') }}</div>
                      <div class="port-popover-table">
                        <div class="port-popover-row" v-if="port.peer_dev">
                          <span class="port-popover-label">{{ $t('cmdb.dcim.peerDev') }}</span>
                          <a
                            v-if="port.peer_dev_id && port.peer_dev_type"
                            :href="`/cmdb/cidetail/${port.peer_dev_type}/${port.peer_dev_id}`"
                            target="_blank"
                            class="port-popover-link"
                            @click.stop
                          >{{ $t('cmdb.dcim.peerDevVal') }}</a>
                          <span v-else class="port-popover-value">{{ port.peer_dev }}</span>
                        </div>
                        <div class="port-popover-row" v-if="port.local_dev_port">
                          <span class="port-popover-label">{{ $t('cmdb.dcim.peerDevPort') }}</span>
                          <span class="port-popover-value">{{ port.local_dev_port }}</span>
                        </div>
                        <div class="port-popover-row" v-if="port.peer_dev_port">
                          <span class="port-popover-label">{{ $t('cmdb.dcim.localDevPort') }}</span>
                          <span class="port-popover-value">{{ port.peer_dev_port }}</span>
                        </div>
                        <div class="port-popover-row" v-if="port.mac_address">
                          <span class="port-popover-label">{{ $t('cmdb.dcim.macAddress') }}</span>
                          <span class="port-popover-value">{{ port.mac_address }}</span>
                        </div>
                        <div class="port-popover-row" v-if="port.IP_ADDR">
                          <span class="port-popover-label">{{ $t('cmdb.dcim.ipAddress') }}</span>
                          <span class="port-popover-value">{{ port.IP_ADDR }}</span>
                        </div>
                        <div class="port-popover-row" v-if="port.interface_usage">
                          <span class="port-popover-label">{{ $t('cmdb.dcim.interfaceUsage') }}</span>
                          <span class="port-popover-value">{{ port.interface_usage }}</span>
                        </div>
                        <div class="port-popover-row" v-if="port.hd_speed">
                          <span class="port-popover-label">{{ $t('cmdb.dcim.interfaceSpeed') }}</span>
                          <span class="port-popover-value">{{ port.hd_speed }}</span>
                        </div>
                        <div class="port-popover-row" v-if="port.other_info">
                          <span class="port-popover-label">{{ $t('cmdb.dcim.remark') }}</span>
                          <span class="port-popover-value">{{ port.other_info }}</span>
                        </div>
                      </div>
                    </div>
                  </template>
                  <img
                    :src="netPortImage"
                    class="rack-container-main-list-device-port"
                    :style="getPortStyle(port, portIndex, item)"
                    :class="{ 'port-connected': port.peer_dev, 'port-disconnected': !port.peer_dev }"
                  />
                </a-popover>
              </div>

              <div
                class="rack-container-main-list-device-sider"
                :style="{
                  right: viewType === 'front' ? '-154px' : '-157px'
                }"
              >
                <div
                  v-for="(nameItem, nameIndex) in getNameList(item)"
                  :key="nameIndex"
                  class="rack-container-main-list-device-name"
                  @click.stop="openDeviceDetail(nameItem)"
                >
                  <CIIcon size="14" :icon="nameItem.icon" />
                  <span class="rack-container-main-list-device-name-text">{{ nameItem.name }}</span>
                </div>
              </div>
            </div>
            <div
              v-if="item.type === 'gap'"
              :class="['rack-container-main-list-gap', viewType === 'rear' ? 'rack-container-main-list-gap_rear' : '']"
              :style="{
                height: unitHeight + 'px'
              }"
              @click="addDevice(index)"
            >
              <a-icon
                type="plus-circle"
                class="rack-container-main-list-gap-icon"
              />
              <span
                class="rack-container-main-list-gap-text"
              >
                {{ $t('cmdb.dcim.addDevice') }}
              </span>
            </div>
          </div>
        </draggable>
      </div>

      <div class="rack-container-main-right">
        <div class="rack-container-main-right-part-1"></div>
        <div class="rack-container-main-right-part-2"></div>

        <img
          v-if="viewType === 'front'"
          :src="require(`@/modules/cmdb/assets/dcim/rack_front_part.png`)"
          class="rack-container-main-right-part-3"
        />
      </div>
    </div>

    <div class="rack-container-footer">
      <template v-if="viewType === 'front'">
        <div class="rack-container-footer-dot"></div>
        <div class="rack-container-footer-dot"></div>
      </template>
    </div>

    <AbnormalModal
      ref="abnormalModalRef"
      @ok="editDevice"
    />
    <DeleteDeviceModal
      ref="deleteDeviceModalRef"
      @ok="handleDeleteDevice"
    />
  </div>
</template>

<script>
import _ from 'lodash'
import { deleteDevice } from '@/modules/cmdb/api/dcim.js'
import netPortImage from '@/modules/cmdb/assets/dcim/net_port.png'

import RackHeader from './rackHeader/index.vue'
import draggable from 'vuedraggable'
import CIIcon from '@/modules/cmdb/components/ciIcon/index.vue'
import AbnormalModal from './abnormalModal.vue'
import DeleteDeviceModal from './deleteDeviceModal.vue'
import { DEVICE_CITYPE_NAME } from '../../../constants.js'

export default {
  name: 'RackUnitView',
  components: {
    RackHeader,
    draggable,
    CIIcon,
    AbnormalModal,
    DeleteDeviceModal
  },
  props: {
    viewType: {
      type: String,
      default: 'front'
    },
    countList: {
      type: Array,
      default: () => []
    },
    unitList: {
      type: Array,
      default: () => []
    },
    rackId: {
      type: Number,
      default: 0
    },
    networkInterfaceData: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      oldDraggableList: [],
      draggableDevice: {},
      netPortImage,
      unitHeight: 24
    }
  },
  computed: {
    titleData() {
      return {
        icon: this.viewType === 'front' ? 'veops-front' : 'veops-rear',
        text: this.viewType === 'front' ? 'cmdb.dcim.frontView' : 'cmdb.dcim.rearView'
      }
    }
  },
  methods: {
    addDevice(index) {
      const sliceUnitList = this.unitList.slice(0, index)
      const unitCount = sliceUnitList.reduce((acc, cur) => acc + cur.unitCount, 0)

      this.$emit('openDeviceForm', {
        unitStart: this.countList.length - unitCount
      })
    },

    editDevice(data) {
      this.$emit('openDeviceForm', {
        CITypeId: data?._type,
        deviceId: data?.id,
        unitStart: data?.u_start,
        unitCount: data?.u_count,
        name: data?.name
      })
    },

    handleDraggableStart(e) {
      this.oldDraggableList = _.cloneDeep(this.unitList)
      this.draggableDevice = this.oldDraggableList?.[e.oldIndex] || {}
    },

    handleDraggableEnd(e) {
      if (e.newIndex === e.oldIndex) {
        return
      }

      const sliceUnitList = this.unitList.slice(0, e.newIndex)
      const unitCount = sliceUnitList.reduce((acc, cur) => acc + cur.unitCount, 0)

      /**
       * 拖拽后的起始U位 = 总U数 - 该设备以上的U数 - 该设备U数 + 1
       */
      const startUnit = this.countList.length - unitCount - this.draggableDevice.unitCount + 1

      if (this?.draggableDevice?.id) {
        this.$emit('draggable', {
          startUnit,
          deviceId: this.draggableDevice.id,
          oldUnitList: this.oldDraggableList
        })
      }

      this.draggableDevice = {}
      this.oldDraggableList = []
    },

    getNameList(item) {
      const nameList = [item]

      if (item?.abnormalList?.length) {
        nameList.push(...item.abnormalList)
      }

      return nameList
    },

    clickDevice(data) {
      if (data.abnormal) {
        this.$refs.abnormalModalRef.open(data)
      }
    },

    removeDevice(item) {
      this.$refs.deleteDeviceModalRef.open(item)
    },

    async handleDeleteDevice({ device, reason }) {
      console.log(reason)
      try {
        await deleteDevice(this.rackId, device.id, { reason })
        this.$message.success(this.$t('deleteSuccess'))
        this.$emit('refreshRackAllData')
      } catch (error) {
        console.error('deleteDevice fail', error)
        this.$message.error(this.$t('deleteFailed'))
      }
    },

    migrateDevice(data) {
      this.$emit('migrateDevice', data.id)
    },

    openDeviceDetail(deviceData) {
      this.$emit('openDeviceDetail', deviceData)
    },

    isSwitchDevice(item) {
      // 交换机端口在前面板，后视图不展示网口；如需排除其他网络设备可在此扩展
      const networkTypes = [
        DEVICE_CITYPE_NAME.SWITCH,
        DEVICE_CITYPE_NAME.FC_SWITCH
      ]
      return networkTypes.includes(item?.CITypeNameEn)
    },

    getDeviceNetworkPorts(deviceId) {
      if (!deviceId) return []
      const deviceData = this.networkInterfaceData?.[String(deviceId)]
      return deviceData?.interfaces || []
    },

    getPortStyle(port, portIndex, deviceItem) {
      const totalPorts = this.getDeviceNetworkPorts(deviceItem._id).length
      const deviceHeight = this.unitHeight * deviceItem.unitCount - 6
      const portSize = Math.min(Math.max(deviceHeight / totalPorts - 2, 8), 16)

      return {
        width: portSize + 'px',
        height: portSize + 'px'
      }
    }
  }
}
</script>

<style lang="less" scoped>
.rack-container {
  width: 236px;

  .rack-title {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;

    &-icon {
      font-size: 14px;
    }

    &-text {
      font-size: 14px;
      font-weight: 700;
      color: #4E5969;
      margin-left: 6px;
    }
  }

  &-main {
    display: flex;
    width: 100%;

    &-left {
      min-width: 17px;
      flex-shrink: 0;
      z-index: 2;

      &-count {
        width: 100%;
        border-bottom: solid 1px rgba(116, 138, 171, 0.25);
        text-align: center;
        font-size: 12px;
        font-weight: 400;
        color: #FFFFFF;
      }
    }

    &-list {
      width: 100%;

      &-device {
        background-color: #2C2D31;
        border-bottom: solid 1px rgba(116, 138, 171, 0.25);
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;

        &-header {
          width: 195px;
          height: 6px;
          clip-path: polygon(20px 0, 175px 0, 195px 100%, 0px 100%);
          background-color: #5D6271;
        }

        .rack-device-image {
          width: 195px;
          height: auto;
          max-height: calc(100% - 6px);
          object-fit: contain;
        }
        .rack-device-image-rear {
          width: 195px;
          background-color: #2C2D31;
        }
        /* 保持原有img样式用于其他可能的图片 */
        img:not(.rack-device-image) {
          width: 195px;
          height: 17px;
        }

        /* 网口指示器 */
        &-ports {
          position: absolute;
          left: 10%;
          bottom: 10px;
          display: flex;
          flex-direction: row;
          align-items: flex-end;
          gap: 6px;
          pointer-events: auto;
        }

        &-port {
          border-radius: 3px;
          cursor: pointer;
          transition: all 0.2s ease;

          &.port-connected {
            box-shadow: 0 0 4px 1px rgba(0, 180, 42, 0.55),
                        0 0 10px 3px rgba(0, 180, 42, 0.3);
          }

          &.port-disconnected {
            box-shadow: 0 0 4px 1px rgba(245, 63, 63, 0.55),
                        0 0 10px 3px rgba(245, 63, 63, 0.3);
          }

          &:hover {
            transform: scale(1.3);
            z-index: 10;
            box-shadow: 0 0 4px 1px rgba(16, 212, 255, 0.5),
                        0 0 10px 3px rgba(16, 212, 255, 0.3) !important;
          }
        }

        &-action {
          display: none;
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          border: 1px solid #10D4FF;
          background: linear-gradient(90deg, rgba(0, 0, 0, 0.80) 0%, rgba(102, 102, 102, 0.80) 100%);
          align-items: center;
          justify-content: center;

          &-btn {
            font-size: 14px;
            font-weight: 400;
            color: #FFFFFF;
            padding: 0 10px;
            cursor: pointer;

            &:not(:first-child) {
              border-left: solid 1px rgba(165, 169, 188, 0.44);
            }

            &:hover {
              color: #10D4FF;
            }
          }
        }

        &-abnormal {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          border: 1px solid #F00;
          background-color: rgba(128, 47, 47, 0.66);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;

          &-text {
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 700;
          }

          &-icon {
            color: #FFFFFF;
            font-size: 12px;
          }
        }

        &-name {
          display: flex;
          align-items: center;
          cursor: pointer;

          &-text {
            margin-left: 3px;
            font-size: 12px;
            font-weight: 400;
            color: #1D2129;

            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            text-wrap: nowrap;
          }

          &:hover {
            .rack-container-main-list-device-name-text {
              color: #3F75FF;
            }
          }
        }

        &-sider {
          position: absolute;
          top: 0;
          width: 140px;
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          row-gap: 6px;
          padding-left: 7px;

          &::after {
            content: "";
            position: absolute;
            top: 5%;
            left: 0;
            width: 4px;
            height: 90%;
            border: solid 1px #10D4FF;
            border-left: none;
          }
        }

        &_normal:hover {
          .rack-container-main-list-device-action {
            display: flex;
          }
        }
      }

      &-gap {
        width: 100%;
        border-bottom: solid 1px rgba(116, 138, 171, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        background-color: #EBEFF8;

        &-icon {
          font-size: 12px;
          display: none;
          color: @primary-color;
        }

        &-text {
          font-size: 12px;
          font-weight: 400;
          color: @primary-color;
          margin-left: 6px;
          display: none;
        }

        &_rear {
          background-color: #CACDD9;
          border-bottom: solid 1px #E4E7ED;
        }

        &:hover {
          background-color: @primary-color_4;

          .rack-container-main-list-gap-icon {
            display: inline-block;
          }

          .rack-container-main-list-gap-text {
            display: inline-block;
          }
        }
      }
    }

    &-right {
      flex-shrink: 0;
      display: flex;
      background-color: #86909C;
      position: relative;

      &-part-1 {
        width: 7px;
        height: 100%;
        border-right: solid 1px rgba(255, 255, 255, 0.33);
      }

      &-part-2 {
        width: 7px;
        height: 100%;
        background: linear-gradient(270deg, rgba(134, 144, 156, 0.00) 0%, rgba(69, 78, 89, 0.88) 100%);
        filter: blur(0.25px);
      }

      &-part-3 {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 21px;
        height: 57.6px;
        transform: translate(-50%, -50%);
      }
    }
  }

  &-footer {
    height: 12px;
    width: 100%;
    background-color: #86909C;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0px 14px;

    &-dot {
      width: 4px;
      height: 4px;
      border-radius: 4px;
      background-color: #E8EBEE;
      border: solid 1px #FFFFFF;
      box-shadow: 3px 3px 7px 0px rgba(136, 150, 163, 0.58) inset, -3px -3px 7px 0px #FFF inset;
    }
  }
}
</style>

<style lang="less">
/* 网口悬浮弹窗样式（非scoped，因为a-popover内容渲染在body下） */
.port-popover {
  font-size: 12px;

  &-title {
    font-size: 13px;
    font-weight: 700;
    color: #1D2129;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #E5E6EB;
  }

  &-table {
    display: flex;
    flex-direction: column;
    row-gap: 4px;
  }

  &-row {
    display: flex;
    align-items: flex-start;
    line-height: 20px;
  }

  &-label {
    color: #86909C;
    white-space: nowrap;
    min-width: 70px;
    flex-shrink: 0;

    &::after {
      content: ':';
    }
  }

  &-value {
    color: #1D2129;
    word-break: break-all;
  }
}

.port-popover-link {
  color: #2F54EB;
  word-break: break-all;

  &:hover {
    color: #3F75FF;
    text-decoration: underline;
  }
}
</style>
