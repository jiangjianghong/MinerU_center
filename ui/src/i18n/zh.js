export default {
  common: {
    refresh: '刷新',
    config: '配置',
    cancel: '取消',
    save: '保存',
    add: '添加',
    remove: '移除',
    enable: '启用',
    disable: '禁用',
    connected: '已连接',
    disconnected: '已断开'
  },
  stats: {
    title: '统计概览',
    totalTasks: '总任务',
    pending: '排队中',
    running: '处理中',
    completed: '已完成',
    failed: '失败',
    idle: '空闲',
    busy: '忙碌',
    offline: '离线'
  },
  status: {
    pending: '排队中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    timeout: '超时',
    cancelled: '已取消'
  },
  instances: {
    title: '实例列表',
    add: '添加实例',
    name: '名称',
    url: '地址',
    status: '状态',
    currentTask: '当前任务',
    noInstances: '暂无实例',
    addSuccess: '实例添加成功',
    addFailed: '实例添加失败',
    removeSuccess: '实例移除成功',
    removeFailed: '实例移除失败',
    enableSuccess: '实例已启用',
    disableSuccess: '实例已禁用',
    updateFailed: '实例更新失败',
    fillAllFields: '请填写所有字段',
    cannotRemoveRunning: '无法移除正在运行任务的实例'
  },
  queue: {
    title: '任务队列',
    pending: '排队中',
    running: '运行中',
    empty: '队列为空',
    position: '位置',
    priority: '优先级',
    cancelTask: '取消任务',
    cancelSuccess: '任务已取消',
    cancelFailed: '取消失败'
  },
  config: {
    title: '系统配置',
    timeoutSettings: '超时设置',
    taskTimeout: '任务超时',
    queueTimeout: '排队超时',
    queueSettings: '队列设置',
    maxQueueSize: '最大队列长度',
    enablePriority: '启用优先级',
    retrySettings: '重试设置',
    maxRetries: '最大重试次数',
    retryDelay: '重试间隔',
    instanceSettings: '实例设置',
    healthCheckInterval: '健康检查间隔',
    instanceTimeout: '实例超时',
    saveSuccess: '配置保存成功',
    saveFailed: '配置保存失败',
    seconds: '秒',
    tasks: '个',
    times: '次'
  },
  time: {
    secondsAgo: '{n}秒前',
    minutesAgo: '{n}分钟前',
    hoursAgo: '{n}小时前'
  }
}
