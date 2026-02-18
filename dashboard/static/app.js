// API Base URL
// ใช้ relative path เพื่อให้ทำงานผ่าน nginx reverse proxy
// ถ้าเข้าผ่าน nginx: /dashboard/api
// ถ้าเข้าผ่าน localhost:5000: /api
const API_BASE = window.location.pathname.startsWith('/dashboard') 
    ? '/dashboard/api' 
    : '/api';

// Current state
let currentServiceId = null;
let refreshInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadServices();
    startAutoRefresh();
    setupModalCloseHandlers();
});

// Setup modal close handlers
function setupModalCloseHandlers() {
    window.onclick = (event) => {
        const configModal = document.getElementById('config-modal');
        const storageModal = document.getElementById('storage-modal');
        const logsModal = document.getElementById('logs-modal');
        
        if (event.target === configModal) {
            closeConfigModal();
        }
        if (event.target === storageModal) {
            closeStorageModal();
        }
        if (event.target === logsModal) {
            closeLogsModal();
        }
    };
}

// Load all services
async function loadServices() {
    try {
        updateConnectionStatus('connecting');
        const response = await fetch(`${API_BASE}/services`);
        const data = await response.json();
        
        if (data.success) {
            updateConnectionStatus('connected');
            renderServices(data.services);
        } else {
            updateConnectionStatus('disconnected');
            showError('ไม่สามารถโหลดข้อมูล services ได้');
        }
    } catch (error) {
        updateConnectionStatus('disconnected');
        console.error('Error loading services:', error);
        showError('ไม่สามารถเชื่อมต่อกับ API ได้');
    }
}

// Render services
function renderServices(services) {
    const container = document.getElementById('services-container');
    container.innerHTML = '';
    
    services.forEach(service => {
        const card = createServiceCard(service);
        container.appendChild(card);
    });
}

// Create service card
function createServiceCard(service) {
    const card = document.createElement('div');
    card.className = 'service-card';
    
    // ตรวจสอบสถานะจาก active field และ state field
    const isActive = service.status.active === true || service.status.state === 'active';
    const statusClass = isActive ? 'active' : 'inactive';
    const statusText = isActive ? '🟢 ทำงาน' : '🔴 หยุดทำงาน';
    
    card.innerHTML = `
        <div class="service-header">
            <div class="service-title">${service.display_name}</div>
            <span class="service-status ${statusClass}">${statusText}</span>
        </div>
        <div class="service-info">
            <div class="service-info-item">
                <span class="service-info-label">ชื่อ Service:</span>
                <span class="service-info-value">${service.name}</span>
            </div>
            <div class="service-info-item">
                <span class="service-info-label">สถานะ:</span>
                <span class="service-info-value">${service.status.state} (${service.status.substate})</span>
            </div>
            ${service.port ? `
            <div class="service-info-item">
                <span class="service-info-label">พอร์ต:</span>
                <span class="service-info-value">${service.port}</span>
            </div>
            ` : ''}
            ${service.working_dir ? `
            <div class="service-info-item">
                <span class="service-info-label">Working Directory:</span>
                <span class="service-info-value">${service.working_dir}</span>
            </div>
            ` : ''}
            ${service.status.pid && service.status.pid !== '0' ? `
            <div class="service-info-item">
                <span class="service-info-label">Process ID:</span>
                <span class="service-info-value">${service.status.pid}</span>
            </div>
            ` : ''}
        </div>
        <div class="service-actions">
            ${isActive ? `
                <button class="btn btn-warning" onclick="restartService('${service.id}')">
                    🔄 รีสตาร์ท
                </button>
                <button class="btn btn-danger" onclick="stopService('${service.id}')">
                    ⏹ หยุด
                </button>
            ` : `
                <button class="btn btn-success" onclick="startService('${service.id}')">
                    ▶ เริ่ม
                </button>
                <button class="btn btn-secondary" disabled>
                    ⏹ หยุด
                </button>
            `}
            <button class="btn btn-secondary" onclick="viewConfig('${service.id}')">
                ⚙️ Config
            </button>
            <button class="btn btn-secondary" onclick="viewStoragePath('${service.id}')">
                📁 Storage
            </button>
            <button class="btn btn-secondary" onclick="viewLogs('${service.id}')">
                📋 Logs
            </button>
        </div>
    `;
    
    return card;
}

// Service control functions
async function startService(serviceId) {
    if (!confirm(`ต้องการเริ่ม ${serviceId} service ใช่หรือไม่?`)) return;
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/services/${serviceId}/start`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`เริ่ม ${serviceId} service สำเร็จ`);
            setTimeout(() => loadServices(), 1000);
        } else {
            showError(`ไม่สามารถเริ่ม service ได้: ${data.error}`);
        }
    } catch (error) {
        showError('เกิดข้อผิดพลาดในการเริ่ม service');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

async function stopService(serviceId) {
    if (!confirm(`ต้องการหยุด ${serviceId} service ใช่หรือไม่?`)) return;
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/services/${serviceId}/stop`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`หยุด ${serviceId} service สำเร็จ`);
            setTimeout(() => loadServices(), 1000);
        } else {
            showError(`ไม่สามารถหยุด service ได้: ${data.error}`);
        }
    } catch (error) {
        showError('เกิดข้อผิดพลาดในการหยุด service');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

async function restartService(serviceId) {
    if (!confirm(`ต้องการรีสตาร์ท ${serviceId} service ใช่หรือไม่?`)) return;
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/services/${serviceId}/restart`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`รีสตาร์ท ${serviceId} service สำเร็จ`);
            setTimeout(() => loadServices(), 1000);
        } else {
            showError(`ไม่สามารถรีสตาร์ท service ได้: ${data.error}`);
        }
    } catch (error) {
        showError('เกิดข้อผิดพลาดในการรีสตาร์ท service');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// View and edit config
async function viewConfig(serviceId) {
    currentServiceId = serviceId;
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/services/${serviceId}/config`);
        const data = await response.json();
        
        if (data.success) {
            const serviceNames = {
                'websocket': 'WebSocket Service',
                'mqtt': 'MQTT Microservice',
                'aicamera-mqtt': 'AI Camera MQTT Broker'
            };
            
            document.getElementById('config-service-name').textContent = serviceNames[serviceId] || serviceId;
            document.getElementById('config-path').textContent = data.path;
            document.getElementById('config-content').value = data.config;
            
            // ถ้ามี additional config (mosquitto config)
            if (data.additional_config) {
                const content = document.getElementById('config-content').value;
                document.getElementById('config-content').value = 
                    `# Systemd Service Config\n${content}\n\n# Mosquitto Config\n${data.additional_config}`;
            }
            
            document.getElementById('config-modal').classList.add('show');
        } else {
            showError(`ไม่สามารถโหลด config ได้: ${data.error}`);
        }
    } catch (error) {
        showError('เกิดข้อผิดพลาดในการโหลด config');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function closeConfigModal() {
    document.getElementById('config-modal').classList.remove('show');
    currentServiceId = null;
}

async function saveConfig() {
    if (!currentServiceId) return;
    
    const configContent = document.getElementById('config-content').value;
    const restartAfterUpdate = document.getElementById('restart-after-update').checked;
    
    if (!confirm('ต้องการบันทึกการเปลี่ยนแปลงใช่หรือไม่?')) return;
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/services/${currentServiceId}/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                config: configContent,
                restart: restartAfterUpdate
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('บันทึก config สำเร็จ');
            closeConfigModal();
            setTimeout(() => loadServices(), 1000);
        } else {
            showError(`ไม่สามารถบันทึก config ได้: ${data.error}`);
        }
    } catch (error) {
        showError('เกิดข้อผิดพลาดในการบันทึก config');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// View and edit storage path
async function viewStoragePath(serviceId) {
    currentServiceId = serviceId;
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/services/${serviceId}/storage-path`);
        const data = await response.json();
        
        if (data.success) {
            const serviceNames = {
                'websocket': 'WebSocket Service',
                'mqtt': 'MQTT Microservice',
                'aicamera-mqtt': 'AI Camera MQTT Broker'
            };
            
            document.getElementById('storage-service-name').textContent = serviceNames[serviceId] || serviceId;
            
            // ใช้ default path หรือ path จาก storage_paths
            const defaultPath = data.storage_paths?.default || data.storage_paths?.STORAGE_PATH || data.working_dir || '';
            document.getElementById('storage-path-input').value = defaultPath;
            
            document.getElementById('storage-modal').classList.add('show');
        } else {
            showError(`ไม่สามารถโหลด storage path ได้: ${data.error}`);
        }
    } catch (error) {
        showError('เกิดข้อผิดพลาดในการโหลด storage path');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

function closeStorageModal() {
    document.getElementById('storage-modal').classList.remove('show');
    currentServiceId = null;
}

async function saveStoragePath() {
    if (!currentServiceId) return;
    
    const storagePath = document.getElementById('storage-path-input').value.trim();
    const restartAfterUpdate = document.getElementById('restart-after-storage-update').checked;
    
    if (!storagePath) {
        showError('กรุณาใส่ storage path');
        return;
    }
    
    if (!confirm(`ต้องการเปลี่ยน storage path เป็น "${storagePath}" ใช่หรือไม่?`)) return;
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/services/${currentServiceId}/storage-path`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: storagePath,
                restart: restartAfterUpdate
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('บันทึก storage path สำเร็จ');
            closeStorageModal();
            setTimeout(() => loadServices(), 1000);
        } else {
            showError(`ไม่สามารถบันทึก storage path ได้: ${data.error}`);
        }
    } catch (error) {
        showError('เกิดข้อผิดพลาดในการบันทึก storage path');
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// View logs
async function viewLogs(serviceId) {
    currentServiceId = serviceId;
    
    const serviceNames = {
        'websocket': 'WebSocket Service',
        'mqtt': 'MQTT Microservice',
        'aicamera-mqtt': 'AI Camera MQTT Broker'
    };
    
    document.getElementById('logs-service-name').textContent = serviceNames[serviceId] || serviceId;
    document.getElementById('logs-modal').classList.add('show');
    
    await loadLogs();
}

function closeLogsModal() {
    document.getElementById('logs-modal').classList.remove('show');
    currentServiceId = null;
}

async function loadLogs() {
    if (!currentServiceId) return;
    
    const lines = document.getElementById('logs-lines').value;
    
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/services/${currentServiceId}/logs?lines=${lines}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('logs-content').textContent = data.logs;
        } else {
            document.getElementById('logs-content').textContent = `Error: ${data.error}`;
        }
    } catch (error) {
        document.getElementById('logs-content').textContent = `Error loading logs: ${error.message}`;
        console.error(error);
    } finally {
        showLoading(false);
    }
}

// Utility functions
function refreshAll() {
    loadServices();
}

function startAutoRefresh() {
    // รีเฟรชทุก 5 วินาที
    refreshInterval = setInterval(() => {
        loadServices();
    }, 5000);
}

function updateConnectionStatus(status) {
    const indicator = document.getElementById('connection-status');
    const dot = indicator.querySelector('.status-dot');
    const text = indicator.querySelector('span:last-child');
    
    dot.className = 'status-dot';
    
    if (status === 'connected') {
        dot.classList.add('connected');
        text.textContent = 'เชื่อมต่อแล้ว';
    } else if (status === 'disconnected') {
        dot.classList.add('disconnected');
        text.textContent = 'ไม่สามารถเชื่อมต่อได้';
    } else {
        text.textContent = 'กำลังเชื่อมต่อ...';
    }
}

function showError(message) {
    alert(`❌ ${message}`);
}

function showSuccess(message) {
    alert(`✅ ${message}`);
}

function showLoading(show) {
    // สามารถเพิ่ม loading indicator ได้ที่นี่
    if (show) {
        console.log('Loading...');
    }
}

