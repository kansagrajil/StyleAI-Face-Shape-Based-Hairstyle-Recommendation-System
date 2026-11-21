/**
 * Profile Logic — Handles loading and updating user hair preferences.
 */

const AppProfile = (() => {
    async function loadProfile() {
        if (typeof AppAuth !== 'undefined' && !AppAuth.isLoggedIn()) {
            AppAuth.requireAuth();
            return;
        }

        try {
            const profile = await API.get('/auth/profile');
            const nameEl = document.getElementById('profileDisplayName');
            const emailEl = document.getElementById('profileDisplayEmail');
            if (nameEl) nameEl.textContent = profile.name || 'User Profile';
            if (emailEl) emailEl.textContent = profile.email || '';

            if (profile.gender) {
                const genderEl = document.getElementById('profGender');
                if (genderEl) genderEl.value = profile.gender;
            }

            if (profile.preferences) {
                if (profile.preferences.hair_type) {
                    const htEl = document.getElementById('profHairType');
                    if (htEl) htEl.value = profile.preferences.hair_type;
                }
                if (profile.preferences.hair_length) {
                    const hlEl = document.getElementById('profHairLength');
                    if (hlEl) hlEl.value = profile.preferences.hair_length;
                }
                if (profile.preferences.style_preference) {
                    const spEl = document.getElementById('profStylePref');
                    if (spEl) spEl.value = profile.preferences.style_preference;
                }
            }
        } catch (err) {
            console.error('Failed to load profile:', err);
        }
    }

    async function saveProfile(e) {
        e.preventDefault();
        const gender = document.getElementById('profGender').value;
        const hair_type = document.getElementById('profHairType').value;
        const hair_length = document.getElementById('profHairLength').value;
        const style_preference = document.getElementById('profStylePref').value.trim();
        const submitBtn = document.getElementById('profSaveBtn');

        if (submitBtn) submitBtn.disabled = true;

        try {
            await API.put('/auth/profile', {
                gender,
                preferences: { hair_type, hair_length, style_preference }
            });
            if (typeof AppToast !== 'undefined') {
                AppToast.success('Preferences updated successfully!');
            }
        } catch (err) {
            if (typeof AppToast !== 'undefined') {
                AppToast.error(err.message || 'Failed to update preferences.');
            }
        } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    }

    return { loadProfile, saveProfile };
})();

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('profileForm')) {
        AppProfile.loadProfile();
    }
});
