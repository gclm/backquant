#!/usr/bin/env node
'use strict';

const os = require('os');

const originalNetworkInterfaces = os.networkInterfaces.bind(os);
os.networkInterfaces = function safeNetworkInterfaces() {
  try {
    const value = originalNetworkInterfaces();
    return value && typeof value === 'object' ? value : {};
  } catch (error) {
    return {};
  }
};

require('@vue/cli-service/bin/vue-cli-service');
