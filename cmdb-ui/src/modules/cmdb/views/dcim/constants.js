export const DCIM_TYPE = {
  REGION: 'region',
  IDC: 'idc',
  SERVER_ROOM: 'server_room',
  RACK: 'rack'
}

export const DCIM_CITYPE_NAME = {
  REGION: 'dcim_region',
  IDC: 'dcim_idc',
  SERVER_ROOM: 'dcim_server_room',
  RACK: 'dcim_rack'
}

export const DEVICE_CITYPE_NAME = {
  SWITCH: 'switch',
  FC_SWITCH: 'fc_switch',
  F5: 'bigip',
  ROUTER: 'router',
  FIRE_WALL: 'firewall',
  SERVER: 'server',
  RAID: 'raid',
  STORAGE: 'storage'
}

export const DEVICE_CITYPE_MANUFACTURER2 = {
  '华为': 'huawei',
  'IBM': 'ibm',
  '华三': 'h3c',
  '戴尔': 'dell',
  '惠普': 'hp',
  '科达': 'kedacom',
  '思科': 'cisco',
  '联想': 'lenovo',
  'NetApp': 'netapp'
}

export const STORAGE_CITYPE_MANUFACTURER = {
  '宏杉': 'macrosan',
  'HPE': 'hpe3par',
  '惠普': 'hpe3par'
}

const createTypeNameMap = (typeObj, typeNameObj) => {
  const map = {}

  Object.keys(typeObj).forEach(key => {
    map[typeObj[key]] = typeNameObj[key]
    map[typeNameObj[key]] = typeObj[key]
  })

  return map
}

export const DCIM_TYPE_NAME_MAP = createTypeNameMap(DCIM_TYPE, DCIM_CITYPE_NAME)
