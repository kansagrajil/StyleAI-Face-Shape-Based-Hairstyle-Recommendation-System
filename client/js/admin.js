/**
 * Admin Panel JavaScript Module.
 * Manages system analytics, user accounts, hairstyle catalog CRUD,
 * face shape categories, recommendation rules, and uploaded images.
 */

const Admin = (() => {
    let hsModal = null;

    /**
     * Initialize Admin Panel.
     */
    async function init() {
        if (!AppAuth.requireAuth()) return;

        // Initialize Bootstrap modal instance if on page
        const modalEl = document.getElementById('hairstyleModal');
        if (modalEl) hsModal = new bootstrap.Modal(modalEl);

        loadAllData();
    }

    /**
     * Load all administrative data across tabs.
     */
    function loadAllData() {
        loadAnalytics();
        loadUsers();
        loadHairstyles();
        loadFaceShapes();
        loadImages();
    }

    // ── 1. System Analytics ───────────────────────────────────

    async function loadAnalytics() {
        try {
            const data = await API.get('/admin/analytics');
            document.getElementById('statTotalUsers').textContent = data.total_users || 0;
            document.getElementById('statTotalScans').textContent = data.total_scans || 0;
            document.getElementById('statTotalTryons').textContent = data.total_tryons || 0;
            document.getElementById('statTotalHairstyles').textContent = data.total_hairstyles || 0;

            renderShapeDistribution(data.face_shape_distribution || {}, data.total_scans || 1);
            renderTopHairstyles(data.top_hairstyles || []);
        } catch (err) {
            console.error('Analytics load error:', err);
            if (err.message && err.message.includes('Admin privileges required')) {
                AppToast.error('Access Denied: Admin privileges required.');
                setTimeout(() => { window.location.href = '/pages/dashboard.html'; }, 1500);
            }
        }
    }

    function renderShapeDistribution(dist, totalScans) {
        const container = document.getElementById('shapeDistributionBars');
        if (!container) return;

        const emojis = { oval: '🥚', round: '🔴', square: '🟦', heart: '💜', diamond: '💎', oblong: '📏' };
        container.innerHTML = '';

        const maxCount = Math.max(1, ...Object.values(dist));

        Object.entries(dist).forEach(([shape, count]) => {
            const pct = totalScans > 0 ? Math.round((count / totalScans) * 100) : 0;
            const barWidth = Math.round((count / maxCount) * 100);

            const shapeImg = typeof FaceShapeHelper !== 'undefined' ? FaceShapeHelper.getImgTag(shape, 20, 'me-1') : (emojis[shape] || '');
            const row = document.createElement('div');
            row.className = 'mb-3';
            row.innerHTML = `
                <div class="d-flex align-items-center justify-content-between small text-muted mb-1">
                    <span class="d-inline-flex align-items-center gap-1">${shapeImg} <strong class="text-capitalize text-light">${shape}</strong></span>
                    <span>${count} scans (${pct}%)</span>
                </div>
                <div class="progress" style="height: 10px; background: rgba(255,255,255,0.08);">
                    <div class="progress-bar bg-gradient-primary rounded-pill" style="width: ${barWidth}%"></div>
                </div>
            `;
            container.appendChild(row);
        });
    }

    function renderTopHairstyles(topList) {
        const list = document.getElementById('topHairstylesList');
        if (!list) return;

        list.innerHTML = topList.map((hs, idx) => `
            <li class="list-group-item bg-transparent text-light border-white-10 py-2 d-flex align-items-center justify-content-between">
                <div>
                    <strong>#${idx + 1} ${hs.name}</strong>
                    <div class="small text-muted">⭐ ${hs.rating} rating</div>
                </div>
                <span class="badge bg-secondary-subtle text-light">${hs.views} views</span>
            </li>
        `).join('');
    }

    // ── 2. User Management ────────────────────────────────────

    async function loadUsers() {
        const tbody = document.querySelector('#usersTable tbody');
        if (!tbody) return;

        const search = document.getElementById('userSearchInput')?.value || '';
        const role = document.getElementById('userRoleFilter')?.value || '';

        try {
            const data = await API.get('/admin/users', { search, role });
            tbody.innerHTML = '';

            data.users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="fw-bold">${u.name}</td>
                    <td class="text-muted">${u.email}</td>
                    <td>
                        <span class="badge ${u.role === 'admin' ? 'bg-danger' : 'bg-primary'}">${u.role}</span>
                    </td>
                    <td>
                        <span class="badge ${u.is_active ? 'bg-success' : 'bg-secondary'}">${u.is_active ? 'Active' : 'Inactive'}</span>
                    </td>
                    <td class="small text-muted">${new Date(u.created_at).toLocaleDateString()}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-warning rounded-pill px-2 me-1" title="Toggle Admin Role" onclick="Admin.toggleUserRole('${u.user_id}', '${u.role}')">
                            <i class="bi bi-shield-lock"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger rounded-pill px-2" title="Delete User" onclick="Admin.deleteUser('${u.user_id}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error('Users load error:', err);
        }
    }

    async function toggleUserRole(userId, currentRole) {
        const newRole = currentRole === 'admin' ? 'user' : 'admin';
        if (!confirm(`Are you sure you want to change this user's role to '${newRole}'?`)) return;

        try {
            await API.patch(`/admin/users/${userId}`, { role: newRole });
            AppToast.success(`User role updated to ${newRole}.`);
            loadUsers();
            loadAnalytics();
        } catch (err) {
            AppToast.error(err.message || 'Failed to update role.');
        }
    }

    async function deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user account and all their data?')) return;

        try {
            await API.del(`/admin/users/${userId}`);
            AppToast.success('User account deleted.');
            loadUsers();
            loadAnalytics();
        } catch (err) {
            AppToast.error(err.message || 'Failed to delete user.');
        }
    }

    // ── 3. Hairstyle Catalog CRUD ──────────────────────────────

    async function loadHairstyles() {
        const tbody = document.querySelector('#hairstylesTable tbody');
        if (!tbody) return;

        try {
            const data = await API.get('/hairstyles', { limit: 50 });
            tbody.innerHTML = '';

            data.hairstyles.forEach(hs => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>
                        <img src="${hs.image_url}" alt="${hs.name}" class="rounded-3 object-cover" style="width: 40px; height: 40px;">
                    </td>
                    <td class="fw-bold">${hs.name}</td>
                    <td>${(hs.face_shapes || []).map(s => `<span class="badge bg-primary-subtle text-primary me-1">${s}</span>`).join('')}</td>
                    <td class="text-capitalize small">${hs.gender}</td>
                    <td class="text-capitalize small">${hs.hair_length || 'medium'}</td>
                    <td class="text-capitalize small">${hs.category || 'modern'}</td>
                    <td><span class="badge bg-success-subtle text-success">${hs.popularity || 85}</span></td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-info rounded-pill px-2 me-1" onclick="Admin.openEditHairstyleModal('${hs.id}')">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger rounded-pill px-2" onclick="Admin.deleteHairstyle('${hs.id}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error('Hairstyles load error:', err);
        }
    }

    function openAddHairstyleModal() {
        document.getElementById('hsModalTitle').textContent = 'Add New Hairstyle';
        document.getElementById('hsForm').reset();
        document.getElementById('hsId').value = '';
        if (hsModal) hsModal.show();
    }

    async function openEditHairstyleModal(hsId) {
        try {
            const hs = await API.get(`/hairstyles/${hsId}`);
            document.getElementById('hsModalTitle').textContent = 'Edit Hairstyle';
            document.getElementById('hsId').value = hs.id;
            document.getElementById('hsName').value = hs.name;
            document.getElementById('hsSlug').value = hs.slug;
            document.getElementById('hsGender').value = hs.gender;
            document.getElementById('hsLength').value = hs.hair_length || 'medium';
            document.getElementById('hsCategory').value = hs.category || 'modern';
            document.getElementById('hsPopularity').value = hs.popularity || 85;
            document.getElementById('hsFaceShapes').value = (hs.face_shapes || []).join(', ');
            document.getElementById('hsImageUrl').value = hs.image_url;
            document.getElementById('hsDescription').value = hs.description;

            if (hsModal) hsModal.show();
        } catch (err) {
            AppToast.error('Failed to load hairstyle details.');
        }
    }

    async function saveHairstyle(event) {
        event.preventDefault();
        const id = document.getElementById('hsId').value;
        const faceShapesArr = document.getElementById('hsFaceShapes').value
            .split(',')
            .map(s => s.trim().toLowerCase())
            .filter(s => s);

        const payload = {
            name: document.getElementById('hsName').value.trim(),
            slug: document.getElementById('hsSlug').value.trim(),
            gender: document.getElementById('hsGender').value,
            hair_length: document.getElementById('hsLength').value,
            category: document.getElementById('hsCategory').value,
            popularity: parseInt(document.getElementById('hsPopularity').value),
            face_shapes: faceShapesArr,
            image_url: document.getElementById('hsImageUrl').value.trim(),
            description: document.getElementById('hsDescription').value.trim()
        };

        try {
            if (id) {
                await API.put(`/admin/hairstyles/${id}`, payload);
                AppToast.success('Hairstyle updated successfully.');
            } else {
                await API.post('/admin/hairstyles', payload);
                AppToast.success('New hairstyle added successfully.');
            }

            if (hsModal) hsModal.hide();
            loadHairstyles();
            loadAnalytics();
        } catch (err) {
            AppToast.error(err.message || 'Failed to save hairstyle.');
        }
    }

    async function deleteHairstyle(hsId) {
        if (!confirm('Are you sure you want to delete this hairstyle entry?')) return;

        try {
            await API.del(`/admin/hairstyles/${hsId}`);
            AppToast.success('Hairstyle deleted.');
            loadHairstyles();
            loadAnalytics();
        } catch (err) {
            AppToast.error(err.message || 'Failed to delete hairstyle.');
        }
    }

    // ── 4. Face Shapes & Rules ───────────────────────────────

    async function loadFaceShapes() {
        const container = document.getElementById('faceShapeCategoryList');
        if (!container) return;

        try {
            const data = await API.get('/admin/face-shapes');
            container.innerHTML = data.face_shapes.map(s => `
                <div class="p-3 rounded-4 bg-dark bg-opacity-50 border border-white-10 mb-3">
                    <div class="d-flex align-items-center justify-content-between mb-1">
                        <strong class="text-primary fs-5 text-capitalize">${s.name} Shape</strong>
                        <span class="badge bg-secondary-subtle text-light">${s.ratio_bounds}</span>
                    </div>
                    <p class="small text-muted mb-0">${s.description}</p>
                </div>
            `).join('');
        } catch (err) {
            console.error('Face shapes load error:', err);
        }
    }

    // ── 5. Uploaded Storage ───────────────────────────────────

    async function loadImages() {
        const grid = document.getElementById('uploadedImagesGrid');
        if (!grid) return;

        try {
            const data = await API.get('/admin/images');
            grid.innerHTML = '';

            if (data.images.length === 0) {
                grid.innerHTML = '<div class="col-12 text-center text-muted py-4">No uploaded files in storage.</div>';
                return;
            }

            data.images.forEach(img => {
                const col = document.createElement('div');
                col.className = 'col-md-3 col-6';
                col.innerHTML = `
                    <div class="glass-card p-2 text-center h-100 border-white-10">
                        <img src="${img.rel_path}" alt="${img.filename}" class="w-100 rounded-3 object-cover mb-2" style="height: 120px;">
                        <div class="small text-truncate text-muted">${img.filename}</div>
                        <div class="small text-muted mb-2">${img.size_kb} KB</div>
                        <button class="btn btn-sm btn-outline-danger rounded-pill px-3" onclick="Admin.deleteImage('${img.filename}')">
                            <i class="bi bi-trash"></i> Delete
                        </button>
                    </div>
                `;
                grid.appendChild(col);
            });
        } catch (err) {
            console.error('Images load error:', err);
        }
    }

    async function deleteImage(filename) {
        if (!confirm(`Are you sure you want to delete file '${filename}'?`)) return;

        try {
            await API.del(`/admin/images/${filename}`);
            AppToast.success('File deleted.');
            loadImages();
        } catch (err) {
            AppToast.error(err.message || 'Failed to delete file.');
        }
    }

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);

    return {
        loadAllData, loadUsers, toggleUserRole, deleteUser,
        loadHairstyles, openAddHairstyleModal, openEditHairstyleModal, saveHairstyle, deleteHairstyle,
        deleteImage
    };
})();
