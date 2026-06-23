        let mapInstance = null;
        let currentLocation = null;
        let isWorkoutActive = false;
        let workoutInterval = null;
        let currentToken = null;
        let currentUser = null;
        let allPlaces = [];
        let currentCategory = 'all';
        let currentPlace = null;
        let proximityCheckInterval = null;
        let lastNearbyPlace = null;
        let guideMapInstance = null;
        const navChatHistory = [];

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');
            sidebar.classList.toggle('show');
            mainContent.classList.toggle('shifted');
        }

        function switchTab(tabId) {
            document.querySelectorAll('.sidebar .nav-item').forEach(item => {
                item.classList.toggle('active', item.dataset.tab === tabId);
            });

            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(c => c.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');

            if (tabId === 'home') {
                document.body.classList.add('page-home');
                document.body.classList.remove('page-app');
                window.scrollTo(0, 0);
            } else {
                document.body.classList.remove('page-home');
                document.body.classList.add('page-app');
                window.scrollTo(0, 0);
            }

            updateMontoniNav(tabId);

            const montoniNav = document.getElementById('montoniNav');
            if (montoniNav) montoniNav.classList.remove('open');

            if (tabId === 'guide') {
                initGuidePage();
            } else if (tabId === 'fitness') {
                loadFitnessStats();
            } else if (tabId === 'checkin') {
                loadCheckinStats();
            } else if (tabId === 'community') {
                loadCommunityFeed();
            } else if (tabId === 'profile') {
                checkAuth();
            }
        }

        function updateMontoniNav(tabId) {
            document.querySelectorAll('.montoni-nav a[data-nav]').forEach(a => {
                a.classList.toggle('active', a.dataset.nav === tabId);
            });

            const cta = document.getElementById('navProfileBtn');
            if (cta) {
                if (currentToken && currentUser) {
                    cta.textContent = currentUser.nickname || '我的账户';
                } else {
                    cta.textContent = '登录 / 注册';
                }
            }

            const header = document.getElementById('montoniHeader');
            if (header) {
                if (tabId === 'home') {
                    header.classList.toggle('scrolled', window.scrollY > 40);
                } else {
                    header.classList.add('scrolled');
                }
            }
        }

        let heroSlideIndex = 0;
        let heroSlideTimer = null;

        function goToHeroSlide(index) {
            const slides = document.querySelectorAll('.hero-slide');
            const indicators = document.querySelectorAll('.hero-indicator');
            if (!slides.length) return;

            heroSlideIndex = index;
            slides.forEach((s, i) => s.classList.toggle('active', i === index));
            indicators.forEach((ind, i) => ind.classList.toggle('active', i === index));
        }

        function nextHeroSlide() {
            const slides = document.querySelectorAll('.hero-slide');
            if (!slides.length) return;
            goToHeroSlide((heroSlideIndex + 1) % slides.length);
        }

        function initHomePage() {
            const heroVideo = document.getElementById('heroVideoBg');
            if (heroVideo) {
                heroVideo.play().catch(() => {
                    document.addEventListener('click', () => heroVideo.play(), { once: true });
                });
            }

            const indicators = document.querySelectorAll('.hero-indicator');
            indicators.forEach(ind => {
                ind.addEventListener('click', () => {
                    goToHeroSlide(parseInt(ind.dataset.slide, 10));
                    resetHeroTimer();
                });
            });

            if (heroSlideTimer) clearInterval(heroSlideTimer);
            heroSlideTimer = setInterval(nextHeroSlide, 6000);

            const header = document.getElementById('montoniHeader');
            if (header) {
                window.addEventListener('scroll', () => {
                    if (document.body.classList.contains('page-home')) {
                        header.classList.toggle('scrolled', window.scrollY > 40);
                    }
                }, { passive: true });
            }

            const menuToggle = document.getElementById('montoniMenuToggle');
            const nav = document.getElementById('montoniNav');
            if (menuToggle && nav) {
                menuToggle.addEventListener('click', () => nav.classList.toggle('open'));
            }
        }

        function resetHeroTimer() {
            if (heroSlideTimer) clearInterval(heroSlideTimer);
            heroSlideTimer = setInterval(nextHeroSlide, 6000);
        }

        function toggleChatPanel() {
            const panel = document.getElementById('floatingChatPanel');
            panel.classList.toggle('show');
        }

        let isDragging = false;
        let offsetX, offsetY;

        document.addEventListener('DOMContentLoaded', function() {
            initHomePage();

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && document.getElementById('imagePreviewOverlay').classList.contains('show')) {
                    closeImagePreview();
                }
            });

            const chatBtn = document.getElementById('floatingChatBtn');
            
            chatBtn.addEventListener('mousedown', function(e) {
                isDragging = true;
                chatBtn.classList.add('dragging');
                offsetX = e.clientX - chatBtn.getBoundingClientRect().left;
                offsetY = e.clientY - chatBtn.getBoundingClientRect().top;
                
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            });

            chatBtn.addEventListener('touchstart', function(e) {
                isDragging = true;
                chatBtn.classList.add('dragging');
                const touch = e.touches[0];
                offsetX = touch.clientX - chatBtn.getBoundingClientRect().left;
                offsetY = touch.clientY - chatBtn.getBoundingClientRect().top;
                
                document.addEventListener('touchmove', onTouchMove);
                document.addEventListener('touchend', onTouchEnd);
            });

            function onMouseMove(e) {
                if (!isDragging) return;
                
                const panel = document.getElementById('floatingChatPanel');
                if (panel.classList.contains('show')) {
                    panel.classList.remove('show');
                }

                let newX = e.clientX - offsetX;
                let newY = e.clientY - offsetY;
                
                const windowWidth = window.innerWidth;
                const windowHeight = window.innerHeight;
                const btnWidth = chatBtn.offsetWidth;
                const btnHeight = chatBtn.offsetHeight;
                
                newX = Math.max(10, Math.min(newX, windowWidth - btnWidth - 10));
                newY = Math.max(10, Math.min(newY, windowHeight - btnHeight - 10));
                
                chatBtn.style.left = newX + 'px';
                chatBtn.style.right = 'auto';
                chatBtn.style.top = newY + 'px';
                chatBtn.style.bottom = 'auto';
            }

            function onMouseUp() {
                isDragging = false;
                chatBtn.classList.remove('dragging');
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            }

            function onTouchMove(e) {
                if (!isDragging) return;
                
                const panel = document.getElementById('floatingChatPanel');
                if (panel.classList.contains('show')) {
                    panel.classList.remove('show');
                }

                const touch = e.touches[0];
                let newX = touch.clientX - offsetX;
                let newY = touch.clientY - offsetY;
                
                const windowWidth = window.innerWidth;
                const windowHeight = window.innerHeight;
                const btnWidth = chatBtn.offsetWidth;
                const btnHeight = chatBtn.offsetHeight;
                
                newX = Math.max(10, Math.min(newX, windowWidth - btnWidth - 10));
                newY = Math.max(10, Math.min(newY, windowHeight - btnHeight - 10));
                
                chatBtn.style.left = newX + 'px';
                chatBtn.style.right = 'auto';
                chatBtn.style.top = newY + 'px';
                chatBtn.style.bottom = 'auto';
            }

            function onTouchEnd() {
                isDragging = false;
                chatBtn.classList.remove('dragging');
                document.removeEventListener('touchmove', onTouchMove);
                document.removeEventListener('touchend', onTouchEnd);
            }
        });

        function getCurrentLocation() {
            return new Promise((resolve) => {
                if (!navigator.geolocation) {
                    useDefaultLocation();
                    resolve();
                    return;
                }

                const optionsHighAccuracy = {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 5000
                };

                const optionsLowAccuracy = {
                    enableHighAccuracy: false,
                    timeout: 10000,
                    maximumAge: 300000
                };

                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        handleLocationSuccess(position);
                        resolve();
                    },
                    (error) => {
                        console.warn('高精度定位失败，尝试低精度定位:', error.message);
                        navigator.geolocation.getCurrentPosition(
                            (position) => {
                                handleLocationSuccess(position);
                                resolve();
                            },
                            (secondError) => {
                                console.error('定位失败:', secondError.message);
                                showLocationError(secondError.code);
                                useDefaultLocation();
                                resolve();
                            },
                            optionsLowAccuracy
                        );
                    },
                    optionsHighAccuracy
                );
            });
        }

        function handleLocationSuccess(position) {
            currentLocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            };
            updateLocationIndicator('guideLocation', `${currentLocation.latitude.toFixed(4)}, ${currentLocation.longitude.toFixed(4)}`);
            updateLocationIndicator('checkinLocation', `${currentLocation.latitude.toFixed(4)}, ${currentLocation.longitude.toFixed(4)}`);
            checkNearbyPlaces().catch(console.error);
        }

        function useDefaultLocation() {
            currentLocation = { latitude: 30.5075, longitude: 114.3795 };
            updateLocationIndicator('guideLocation', '📍 使用默认位置（南湖校区）');
            updateLocationIndicator('checkinLocation', '📍 使用默认位置（南湖校区）');
        }

        function showLocationError(errorCode) {
            const errorMessages = {
                1: '用户拒绝了位置权限请求',
                2: '无法获取位置信息',
                3: '定位超时，请稍后重试',
                4: '未知错误'
            };
            const message = errorMessages[errorCode] || errorMessages[4];
            alert(`⚠️ 定位失败\n\n${message}\n\n将使用默认位置（南湖校区）`);
        }

        function updateLocationIndicator(elementId, message = '位置已更新') {
            const indicator = document.getElementById(elementId);
            if (indicator) {
                indicator.innerHTML = `<span>📍</span><span>${message}</span>`;
                indicator.classList.add('updated');
            }
        }

        async function initGuidePage() {
            await loadCategories();
            await loadAllPlaces();
            if (!currentLocation) {
                await getCurrentLocation();
            }
            startProximityCheck();
        }

        async function loadAllPlaces() {
            try {
                const response = await fetch('/api/places');
                allPlaces = await response.json();
                displayGuidePlaces();
            } catch (error) {
                console.error('加载场所失败:', error);
            }
        }

        function displayGuidePlaces() {
            const list = document.getElementById('placesList');
            const filteredPlaces = currentCategory === 'all'
                ? allPlaces
                : allPlaces.filter(p => p.category === currentCategory);

            if (filteredPlaces.length === 0) {
                list.innerHTML = '<div class="empty-state"><div class="empty-icon">🏛️</div><p>暂无景点</p></div>';
                return;
            }

            list.innerHTML = '';
            filteredPlaces.forEach(place => {
                const distance = currentLocation
                    ? calculateDistance(currentLocation.latitude, currentLocation.longitude, place.latitude, place.longitude)
                    : null;

                const item = document.createElement('div');
                item.className = 'list-item';
                item.onclick = () => showPlaceDetail(place);

                const icon = document.createElement('div');
                icon.className = 'list-icon';
                icon.style.background = distance && distance <= 50 ? 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)' : 'linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%)';
                icon.textContent = getPlaceIcon(place.category);

                const content = document.createElement('div');
                content.className = 'list-content';
                content.innerHTML = `
                    <div class="list-title">${place.name}</div>
                    <div class="list-subtitle">${place.category}${distance !== null ? ` · ${distance.toFixed(0)}米` : ''}</div>
                `;

                const actions = document.createElement('div');
                actions.style.display = 'flex';
                actions.style.gap = '10px';
                actions.innerHTML = `
                    <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); navigateToPlaceByName('${place.name}')">导航</button>
                    <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); speakPlace('${place.description.replace(/'/g, "\\'")}')">🔊</button>
                `;

                item.appendChild(icon);
                item.appendChild(content);
                item.appendChild(actions);
                list.appendChild(item);
            });
        }

        function calculateDistance(lat1, lng1, lat2, lng2) {
            const R = 6371000;
            const toRad = (deg) => deg * Math.PI / 180;
            const dLat = toRad(lat2 - lat1);
            const dLng = toRad(lng2 - lng1);
            const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
                      Math.sin(dLng / 2) * Math.sin(dLng / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return R * c;
        }

        async function checkNearbyPlaces() {
            if (!currentLocation) return;

            try {
                const response = await fetch(`/api/check_proximity?lat=${currentLocation.latitude}&lng=${currentLocation.longitude}`);
                const data = await response.json();

                if (data.nearby_found && data.place) {
                    if (lastNearbyPlace !== data.place.name) {
                        lastNearbyPlace = data.place.name;
                        showNearbyAlert(data.place);
                    }
                }
            } catch (error) {
                console.error('检查附近场所失败:', error);
            }
        }

        function showNearbyAlert(place) {
            const alert = document.getElementById('nearbyAlert');
            if (alert) {
                document.getElementById('nearbyPlaceName').textContent = place.name;
                document.getElementById('nearbyPlaceDesc').textContent = place.description.substring(0, 100) + '...';
                alert.style.display = 'block';
                currentPlace = place;
            }
        }

        function closeNearbyAlert() {
            const alert = document.getElementById('nearbyAlert');
            if (alert) {
                alert.style.display = 'none';
            }
        }

        function speakCurrentPlace() {
            if (currentPlace) {
                speakPlace(currentPlace.voice_description || currentPlace.description);
            }
        }

        function speakPlace(text) {
            if ('speechSynthesis' in window) {
                speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'zh-CN';
                utterance.rate = 1.0;
                speechSynthesis.speak(utterance);
            } else {
                alert('您的浏览器不支持语音合成');
            }
        }

        function startProximityCheck() {
            if (proximityCheckInterval) {
                clearInterval(proximityCheckInterval);
            }
            proximityCheckInterval = setInterval(() => {
                if (currentLocation) {
                    checkNearbyPlaces();
                    displayGuidePlaces();
                }
            }, 5000);
        }

        function showPlaceDetail(place) {
            currentPlace = place;
            document.getElementById('placeModalTitle').textContent = place.name;
            document.getElementById('placeDescription').textContent = place.description;
            document.getElementById('placeModal').style.display = 'flex';
        }

        function closePlaceModal() {
            document.getElementById('placeModal').style.display = 'none';
        }

        function speakIntroduction() {
            if (currentPlace) {
                speakPlace(currentPlace.voice_description || currentPlace.description);
            }
        }

        async function navigateToPlaceByName(placeName) {
            const place = allPlaces.find(p => p.name === placeName);
            if (place) {
                await openNavigation(place);
            }
        }

        async function openNavigation(place) {
            if (!currentLocation) {
                await getCurrentLocation();
            }

            const startLat = currentLocation ? currentLocation.latitude : 30.5075;
            const startLng = currentLocation ? currentLocation.longitude : 114.3795;

            showMapNavigation(startLat, startLng, place.latitude, place.longitude, place.name);
        }

        let currentNavData = null;

        function showMapNavigation(startLat, startLng, destLat, destLng, destName) {
            currentNavData = {
                startLat,
                startLng,
                destLat,
                destLng,
                destName
            };

            const mapWrapper = document.getElementById('mapWrapper');
            mapWrapper.classList.add('show');

            if (mapInstance) {
                mapInstance.destroy();
            }

            mapInstance = new AMap.Map('map', {
                center: [destLng, destLat],
                zoom: 17,
                mapStyle: 'amap://styles/normal',
                features: ['bg', 'road', 'building', 'point'],
                showIndoorMap: false
            });

            new AMap.Marker({
                position: [startLng, startLat],
                map: mapInstance,
                title: '当前位置',
                icon: new AMap.Icon({
                    size: new AMap.Size(32, 32),
                    image: 'https://webapi.amap.com/theme/v1.3/markers/n/start.png'
                })
            });

            new AMap.Marker({
                position: [destLng, destLat],
                map: mapInstance,
                title: destName,
                icon: new AMap.Icon({
                    size: new AMap.Size(32, 32),
                    image: 'https://webapi.amap.com/theme/v1.3/markers/n/end.png'
                })
            });
        }

        function openGaodeNavigation() {
            if (!currentNavData) return;
            
            const { startLat, startLng, destLat, destLng, destName } = currentNavData;
            
            const url = `https://uri.amap.com/navigation?from=${startLng},${startLat}&to=${destLng},${destLat}&toName=${encodeURIComponent(destName)}&mode=1&policy=1&callnative=1`;
            
            window.location.href = url;
            
            setTimeout(() => {
                const webUrl = `https://amap.com/navi?from=${startLng},${startLat}&to=${destLng},${destLat}&toName=${encodeURIComponent(destName)}&mode=1`;
                window.open(webUrl, '_blank');
            }, 3000);
        }

        function displayWalkingSteps(steps) {
            const navSteps = document.getElementById('navSteps');
            navSteps.innerHTML = '';

            steps.forEach((step, index) => {
                const stepDiv = document.createElement('div');
                stepDiv.className = 'nav-step';

                const numberDiv = document.createElement('div');
                numberDiv.className = 'step-number';
                numberDiv.textContent = index + 1;

                const contentDiv = document.createElement('div');
                contentDiv.className = 'step-content';
                contentDiv.innerHTML = `<div>${step.instruction}</div>`;
                if (step.distance) {
                    contentDiv.innerHTML += `<div class="step-distance">${step.distance}米</div>`;
                }

                stepDiv.appendChild(numberDiv);
                stepDiv.appendChild(contentDiv);
                navSteps.appendChild(stepDiv);
            });
        }

        function openGuideMap() {
            if (!currentLocation) {
                alert('请先获取位置');
                return;
            }

            const modal = document.getElementById('guideMapModal');
            modal.style.display = 'flex';

            setTimeout(() => {
                initGuideMap();
            }, 100);
        }

        function closeGuideMap() {
            document.getElementById('guideMapModal').style.display = 'none';
        }

        function initGuideMap() {
            if (guideMapInstance) {
                guideMapInstance.destroy();
            }

            guideMapInstance = new AMap.Map('guideMapContainer', {
                center: [currentLocation.longitude, currentLocation.latitude],
                zoom: 17,
                mapStyle: 'amap://styles/normal',
                features: ['bg', 'road', 'building', 'point'],
                showIndoorMap: false
            });

            guideMapInstance.add(new AMap.Circle({
                center: [currentLocation.longitude, currentLocation.latitude],
                radius: 500,
                strokeColor: '#1e3a5f',
                strokeOpacity: 0.5,
                strokeWeight: 2,
                strokeStyle: 'dashed',
                fillOpacity: 0
            }));

            new AMap.Marker({
                position: [currentLocation.longitude, currentLocation.latitude],
                map: guideMapInstance,
                title: '我的位置'
            });

            const nearbyPlaces = allPlaces.filter(place => {
                const distance = calculateDistance(currentLocation.latitude, currentLocation.longitude, place.latitude, place.longitude);
                return distance <= 500;
            });

            nearbyPlaces.forEach(place => {
                const distance = calculateDistance(currentLocation.latitude, currentLocation.longitude, place.latitude, place.longitude);

                const marker = new AMap.Marker({
                    position: [place.longitude, place.latitude],
                    map: guideMapInstance,
                    title: `${place.name} (${distance.toFixed(0)}米)`
                });

                marker.on('click', () => {
                    showPlaceDetail(place);
                    closeGuideMap();
                });
            });

            document.getElementById('guideMapInfo').textContent = `500米内场所: ${nearbyPlaces.length}个`;
        }

        async function sendNavMessage() {
            const input = document.getElementById('navInput');
            const query = input.value.trim();
            
            if (!query) return;

            const historyForApi = navChatHistory.slice(-6);
            addNavMessage('user', query);
            navChatHistory.push({ role: 'user', content: query });
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: query,
                        current_location: currentLocation,
                        conversation_history: historyForApi
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    const botText = data.message || '已收到您的请求';
                    if (data.route || data.total_distance) {
                        showNavigation(data);
                        if (botText) {
                            addNavMessage('bot', botText);
                            navChatHistory.push({ role: 'assistant', content: botText });
                        }
                    } else {
                        addNavMessage('bot', botText);
                        navChatHistory.push({ role: 'assistant', content: botText });
                    }
                } else {
                    const errMsg = data.message || '抱歉，我无法理解您的问题';
                    addNavMessage('bot', errMsg);
                    navChatHistory.push({ role: 'assistant', content: errMsg });
                }
            } catch (error) {
                console.error('请求失败:', error);
                const errMsg = '网络请求失败，请稍后重试';
                addNavMessage('bot', errMsg);
                navChatHistory.push({ role: 'assistant', content: errMsg });
            }
        }

        function handleNavKeydown(event) {
            if (event.key === 'Enter') {
                sendNavMessage();
            }
        }

        function addNavMessage(sender, content) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const avatar = document.createElement('div');
            avatar.className = `avatar ${sender}`;
            if (sender === 'user' && currentUser?.avatar && isImageAvatar(currentUser.avatar)) {
                avatar.classList.add('has-image');
                avatar.style.backgroundImage = `url(${currentUser.avatar})`;
                avatar.style.backgroundSize = 'cover';
                avatar.style.backgroundPosition = 'center';
            } else {
                avatar.textContent = sender === 'user' ? '👤' : '🤖';
            }
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(sender === 'user' ? contentDiv : avatar);
            messageDiv.appendChild(sender === 'user' ? avatar : contentDiv);
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showNavigation(data) {
            const mapWrapper = document.getElementById('mapWrapper');
            mapWrapper.classList.add('show');
            
            document.getElementById('navDistance').textContent = data.total_distance ? `距离：${data.total_distance}米` : '距离：--';
            document.getElementById('navDuration').textContent = data.total_duration ? `预计时间：${Math.floor(data.total_duration / 60)}分钟` : '预计时间：--';
            
            if (data.route && data.route.steps) {
                displayNavigationSteps(data.route.steps);
                if (data.route.start_location && data.route.destination_location) {
                    updateMap(
                        data.route.start_location.latitude,
                        data.route.start_location.longitude,
                        data.route.destination_location.latitude,
                        data.route.destination_location.longitude,
                        data.destination
                    );
                }
            }
        }

        function closeMap() {
            const mapWrapper = document.getElementById('mapWrapper');
            mapWrapper.classList.remove('show');
        }

        let mapInitialized = false;

        function initMapLazy() {
            if (mapInitialized) return;
            
            mapInstance = new AMap.Map('map', {
                center: [114.3795, 30.5075],
                zoom: 17,
                mapStyle: 'amap://styles/normal',
                features: ['bg', 'road', 'building', 'point'],
                showIndoorMap: false
            });
            
            mapInitialized = true;
        }

        function updateMap(startLat, startLng, destLat, destLng, destName) {
            if (!mapInstance) {
                initMapLazy();
            }
            
            mapInstance.clearMap();
            
            mapInstance.setCenter([(startLng + destLng) / 2, (startLat + destLat) / 2]);
            mapInstance.setZoom(17);
            
            new AMap.Marker({
                position: [startLng, startLat],
                map: mapInstance,
                title: '当前位置'
            });
            
            new AMap.Marker({
                position: [destLng, destLat],
                map: mapInstance,
                title: destName,
                icon: new AMap.Icon({
                    size: new AMap.Size(32, 32),
                    image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png'
                })
            });
            
            AMap.plugin('AMap.Walking', function() {
                const walking = new AMap.Walking({
                    map: mapInstance,
                    hideMarkers: false
                });
                
                walking.search([startLng, startLat], [destLng, destLat], function(status, result) {
                    if (status === 'complete') {
                        const path = result.routes[0].path;
                        const polyline = new AMap.Polyline({
                            path: path,
                            strokeColor: '#1e3a5f',
                            strokeWeight: 5,
                            strokeOpacity: 0.8
                        });
                        mapInstance.add(polyline);
                    }
                });
            });
        }

        function displayNavigationSteps(steps) {
            const navSteps = document.getElementById('navSteps');
            navSteps.innerHTML = '';
            
            steps.forEach((step, index) => {
                const stepDiv = document.createElement('div');
                stepDiv.className = 'nav-step';
                
                const numberDiv = document.createElement('div');
                numberDiv.className = 'step-number';
                numberDiv.textContent = index + 1;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'step-content';
                contentDiv.innerHTML = `<div>${step.instruction}</div>`;
                if (step.distance) {
                    contentDiv.innerHTML += `<div class="step-distance">${step.distance}米</div>`;
                }
                
                stepDiv.appendChild(numberDiv);
                stepDiv.appendChild(contentDiv);
                navSteps.appendChild(stepDiv);
            });
        }

        async function loadCategories() {
            try {
                const response = await fetch('/api/places/categories');
                const categories = await response.json();
                const tabs = document.getElementById('categoryTabs');
                tabs.innerHTML = '<button class="btn btn-primary btn-sm" onclick="currentCategory=\'all\'; displayGuidePlaces();">全部</button>';
                
                categories.forEach(cat => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-secondary btn-sm';
                    btn.textContent = cat;
                    btn.onclick = () => {
                        currentCategory = cat;
                        displayGuidePlaces();
                    };
                    tabs.appendChild(btn);
                });
            } catch (error) {
                console.error('加载类别失败:', error);
            }
        }

        function getPlaceIcon(category) {
            const icons = {
                '图书馆': '📚',
                '教学楼': '🏫',
                '体育馆': '🏟️',
                '食堂': '🍽️',
                '地标建筑': '🏛️',
                '办公楼': '🏢',
                '活动场所': '🎉'
            };
            return icons[category] || '🏠';
        }

        let workoutDistance = 0;
        let workoutDuration = 0;
        let workoutCalories = 0;

        async function toggleWorkout() {
            const button = document.getElementById('workoutButton');
            
            if (!isWorkoutActive) {
                const success = await startWorkout();
                if (success) {
                    button.textContent = '结束运动';
                    document.getElementById('workoutStatus').textContent = '🏃 运动中...';
                } else {
                    document.getElementById('workoutStatus').textContent = '❌ 运动开始失败';
                    setTimeout(() => {
                        document.getElementById('workoutStatus').textContent = '🏃 准备开始运动';
                    }, 2000);
                }
            } else {
                await endWorkout();
                button.textContent = '开始运动';
                document.getElementById('workoutStatus').textContent = '🏃 准备开始运动';
            }
        }

        async function startWorkout() {
            console.log('=== startWorkout 开始执行 ===');
            console.log('当前 currentLocation:', currentLocation);
            console.log('当前 isWorkoutActive:', isWorkoutActive);
            
            // 重置运动数据
            workoutDistance = 0;
            workoutDuration = 0;
            workoutCalories = 0;
            
            // 直接设置默认位置，避免 null 问题
            if (!currentLocation) {
                console.log('设置默认位置');
                currentLocation = { latitude: 30.5075, longitude: 114.3795 };
            }
            
            // 尝试获取位置，但不等待太久
            try {
                const locationPromise = getCurrentLocation();
                await Promise.race([
                    locationPromise,
                    new Promise(resolve => setTimeout(resolve, 5000))
                ]);
            } catch (e) {
                console.warn('获取位置超时，继续使用默认位置');
            }
            
            console.log('使用位置:', currentLocation);
            
            let startSuccess = false;
            
            try {
                console.log('开始调用 API');
                const response = await fetch(`/api/fitness/start?workout_type=walking&start_latitude=${currentLocation.latitude}&start_longitude=${currentLocation.longitude}`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('API 响应:', data);
                
                if (data.success && data.data && data.data.workout_id) {
                    window.workoutId = data.data.workout_id;
                    console.log('运动开始成功，ID:', window.workoutId);
                    
                    // 只有在API成功后才设置状态
                    isWorkoutActive = true;
                    
                    workoutInterval = setInterval(() => {
                        workoutDuration += 1;
                        workoutDistance += Math.random() * 2;
                        workoutCalories = Math.round(workoutDistance * 0.05);
                        
                        document.getElementById('workoutDistance').textContent = Math.round(workoutDistance);
                        document.getElementById('workoutDuration').textContent = workoutDuration;
                        document.getElementById('workoutCalories').textContent = workoutCalories;
                    }, 1000);
                    
                    startSuccess = true;
                } else {
                    console.warn('运动开始失败:', data.message);
                    startSuccess = false;
                }
            } catch (error) {
                console.error('开始运动失败:', error);
                startSuccess = false;
            }
            
            return startSuccess;
        }

        async function endWorkout() {
            console.log('=== endWorkout 开始执行 ===');
            console.log('当前 window.workoutId:', window.workoutId);
            console.log('当前 isWorkoutActive:', isWorkoutActive);
            
            // 停止计时器和状态
            isWorkoutActive = false;
            clearInterval(workoutInterval);
            
            if (!window.workoutId) {
                console.warn('未找到有效的运动ID，跳过结束运动请求');
            } else {
                try {
                    console.log('发送运动数据到后端...');
                    console.log('运动数据 - 距离:', workoutDistance, '时间:', workoutDuration, '卡路里:', workoutCalories);
                    
                    const response = await fetch(`/api/fitness/end?workout_id=${window.workoutId}&distance=${workoutDistance}&duration=${workoutDuration}&calories=${workoutCalories}`, {
                        method: 'POST',
                        headers: { Authorization: `Bearer ${currentToken}` }
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        console.log('运动结束成功:', data.data);
                    } else {
                        console.warn('结束运动失败:', data.message);
                    }
                } catch (error) {
                    console.error('结束运动失败:', error);
                } finally {
                    window.workoutId = null;
                }
            }
            
            // 重置UI显示
            document.getElementById('workoutDistance').textContent = 0;
            document.getElementById('workoutDuration').textContent = 0;
            document.getElementById('workoutCalories').textContent = 0;
            
            // 刷新统计数据
            await loadFitnessStats();
            console.log('运动统计已刷新');
        }

        async function loadFitnessStats() {
            console.log('开始加载运动统计...');
            
            try {
                const response = await fetch('/api/fitness/statistics?period=week&_=' + Date.now(), {
                    headers: { Authorization: `Bearer ${currentToken}` },
                    cache: 'no-cache'
                });
                
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                
                const data = await response.json();
                console.log('周统计数据:', data);
                
                if (data.success && data.data) {
                    const stats = data.data;
                    document.getElementById('statDistance').textContent = Math.round(stats.total_distance || 0);
                    document.getElementById('statCalories').textContent = Math.round(stats.total_calories || 0);
                    document.getElementById('statWorkouts').textContent = stats.workout_count || 0;
                } else {
                    console.warn('周统计数据格式不正确:', data);
                }
            } catch (error) {
                console.error('加载运动统计失败:', error);
            }
            
            try {
                const response = await fetch('/api/fitness/statistics?period=all&_=' + Date.now(), {
                    headers: { Authorization: `Bearer ${currentToken}` },
                    cache: 'no-cache'
                });
                
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                
                const data = await response.json();
                console.log('累计统计数据:', data);
                
                if (data.success && data.data) {
                    const stats = data.data;
                    document.getElementById('statTotal').textContent = Math.round(stats.total_distance || 0);
                } else {
                    console.warn('累计统计数据格式不正确:', data);
                }
            } catch (error) {
                console.error('加载累计统计失败:', error);
            }
            
            try {
                const response = await fetch('/api/fitness/history?_=' + Date.now(), {
                    headers: { Authorization: `Bearer ${currentToken}` },
                    cache: 'no-cache'
                });
                
                if (!response.ok) {
                    throw new Error('HTTP error ' + response.status);
                }
                
                const data = await response.json();
                console.log('运动历史数据:', data);
                
                if (data.success && data.data) {
                    if (data.data.length > 0) {
                        renderWorkoutHistory(data.data);
                    } else {
                        // 显示暂无运动记录
                        const container = document.getElementById('workoutHistory');
                        container.innerHTML = `
                            <div style="text-align: center; color: var(--text-secondary); padding: 40px;">
                                <div style="font-size: 48px; margin-bottom: 16px;">🏃</div>
                                <div>暂无运动记录</div>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('加载运动历史失败:', error);
            }
        }

        function renderWorkoutHistory(history) {
            const container = document.getElementById('workoutHistory');
            let html = '';
            
            history.forEach(workout => {
                const duration = formatDuration(workout.total_duration);
                const date = new Date(workout.created_at).toLocaleDateString('zh-CN');
                const type = workout.workout_type === 'walking' ? '🚶 步行' : 
                             workout.workout_type === 'running' ? '🏃 跑步' : '🚴 骑行';
                
                html += `
                    <div class="checkin-history-card">
                        <div class="checkin-history-icon">${workout.workout_type === 'walking' ? '🚶' : workout.workout_type === 'running' ? '🏃' : '🚴'}</div>
                        <div class="checkin-history-content">
                            <div class="checkin-history-place">${type}</div>
                            <div class="checkin-history-time">${date} · 距离: ${Math.round(workout.total_distance)}m · ${duration} · ${Math.round(workout.calories_burned)}卡路里</div>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }

        function formatDuration(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins}分${secs}秒`;
        }

        async function checkin() {
            const button = document.getElementById('checkinButton');
            
            try {
                const response = await fetch('/api/checkin', {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();
                
                if (data.success) {
                    let message = data.data.message || '✅ 打卡成功！';
                    
                    if (data.data.consecutive_days !== undefined && data.data.consecutive_days > 0) {
                        message += `\n🔥 连续打卡 ${data.data.consecutive_days} 天`;
                    }
                    
                    button.textContent = '✅ 打卡成功！';
                    button.classList.add('checkin-success');
                    
                    if (data.data.consecutive_days !== undefined && data.data.consecutive_days > 0) {
                        setTimeout(() => {
                            alert(`🔥 连续打卡 ${data.data.consecutive_days} 天`);
                        }, 100);
                    }
                    
                    if (data.data.new_achievements && data.data.new_achievements.length > 0) {
                        alert(`🎉 恭喜获得成就：${data.data.new_achievements.map(a => a.name).join('、')}`);
                    }
                    
                    loadCheckinStats();
                    
                    setTimeout(() => {
                        button.textContent = '🎯 点击打卡';
                        button.classList.remove('checkin-success');
                    }, 3000);
                    
                } else {
                    alert(data.message);
                }
                    
                loadCheckinStats();
            } catch (error) {
                console.error('打卡失败:', error);
                alert('打卡失败，请重试');
            }
        }

        const achievementsData = [
            {
                id: 'first_checkin',
                name: '初来乍到',
                desc: '完成第一次打卡',
                icon: '🎯',
                rarity: 'common',
                hidden: false,
                target: 1,
                type: 'checkin_count'
            },
            {
                id: 'checkin_10',
                name: '打卡达人',
                desc: '累计打卡10次',
                icon: '🏆',
                rarity: 'common',
                hidden: false,
                target: 10,
                type: 'checkin_count'
            },
            {
                id: 'checkin_50',
                name: '打卡大师',
                desc: '累计打卡50次',
                icon: '👑',
                rarity: 'rare',
                hidden: false,
                target: 50,
                type: 'checkin_count'
            },
            {
                id: 'checkin_100',
                name: '打卡传奇',
                desc: '累计打卡100次',
                icon: '🌟',
                rarity: 'epic',
                hidden: false,
                target: 100,
                type: 'checkin_count'
            },
            {
                id: 'streak_7',
                name: '坚持一周',
                desc: '连续打卡7天',
                icon: '📅',
                rarity: 'common',
                hidden: false,
                target: 7,
                type: 'streak_days'
            },
            {
                id: 'streak_30',
                name: '月度之星',
                desc: '连续打卡30天',
                icon: '🌙',
                rarity: 'rare',
                hidden: false,
                target: 30,
                type: 'streak_days'
            },
            {
                id: 'streak_100',
                name: '百日坚持',
                desc: '连续打卡100天',
                icon: '☀️',
                rarity: 'epic',
                hidden: false,
                target: 100,
                type: 'streak_days'
            },
            {
                id: 'explore_5',
                name: '校园探索者',
                desc: '在5个不同地点打卡',
                icon: '🗺️',
                rarity: 'common',
                hidden: false,
                target: 5,
                type: 'unique_places'
            },
            {
                id: 'explore_10',
                name: '校园旅行家',
                desc: '在10个不同地点打卡',
                icon: '🚀',
                rarity: 'rare',
                hidden: false,
                target: 10,
                type: 'unique_places'
            },
            {
                id: 'hidden_mystery',
                name: '???',
                desc: '???',
                icon: '❓',
                rarity: 'legendary',
                hidden: true,
                target: 1,
                type: 'hidden_condition',
                realName: '神秘探索者',
                realDesc: '在南湖、马房山、余家头三个校区都完成打卡'
            },
            {
                id: 'hidden_night',
                name: '???',
                desc: '???',
                icon: '🌙',
                rarity: 'legendary',
                hidden: true,
                target: 1,
                type: 'hidden_condition',
                realName: '夜行者',
                realDesc: '在晚上22:00-06:00之间完成打卡'
            },
            {
                id: 'hidden_early',
                name: '???',
                desc: '???',
                icon: '🌅',
                rarity: 'epic',
                hidden: true,
                target: 1,
                type: 'hidden_condition',
                realName: '早起达人',
                realDesc: '在早上06:00-08:00之间完成打卡'
            }
        ];

        let userAchievements = {};
        let currentAchievementFilter = 'all';

        async function loadCheckinStats() {
            try {
                const response = await fetch('/api/checkin/statistics', {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();
                if (data.success) {
                    const stats = data.data;
                    document.getElementById('checkinTotal').textContent = stats.total_checkins;
                    document.getElementById('checkinStreak').textContent = stats.consecutive_days;
                    
                    userAchievements = stats.achievements || {};
                    
                    renderActivities(stats.activities || [], stats.current_activity);
                    renderAchievements();
                    updateAchievementsHeader();
                }
            } catch (error) {
                console.error('加载打卡统计失败:', error);
                renderAchievements();
            }
            
            await loadCheckinHistory();
        }
        
        async function loadCheckinHistory() {
            try {
                const response = await fetch('/api/checkin/history', {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();
                if (data.success && data.data) {
                    renderCheckinHistory(data.data);
                }
            } catch (error) {
                console.error('加载打卡历史失败:', error);
            }
        }
        
        function renderCheckinHistory(history) {
            const container = document.getElementById('checkinHistory');
            
            if (!history || history.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">📝</div>
                        <p>暂无打卡记录</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = '';
            
            history.forEach(item => {
                const card = document.createElement('div');
                card.className = 'checkin-history-card';
                card.innerHTML = `
                    <div class="checkin-history-icon">✅</div>
                    <div class="checkin-history-content">
                        <div class="checkin-history-place">${item.place_name || '未知地点'}</div>
                        <div class="checkin-history-time">${formatDateTime(item.checkin_time)}</div>
                    </div>
                `;
                container.appendChild(card);
            });
        }
        
        function formatDateTime(dateTimeStr) {
            const date = new Date(dateTimeStr);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day} ${hours}:${minutes}`;
        }

        function renderActivities(activities, currentActivity) {
            const banner = document.getElementById('currentActivityBanner');
            const grid = document.getElementById('activitiesGrid');
            
            if (currentActivity && currentActivity.time_slots) {
                banner.style.display = 'flex';
                document.getElementById('currentActivityIcon').textContent = currentActivity.icon || '';
                document.getElementById('currentActivityName').textContent = currentActivity.name || '';
                document.getElementById('currentActivityTime').textContent = `⏰ ${currentActivity.time_slots.join(' / ')}`;
            } else {
                banner.style.display = 'none';
            }
            
            grid.innerHTML = '';
            
            activities.forEach(activity => {
                if (!activity || !activity.id) return;
                
                const isCompleted = (activity.progress || 0) >= 100;
                const isActive = activity.is_active || false;
                const timeSlots = activity.time_slots || [];
                
                const card = document.createElement('div');
                card.className = 'flip-card activity-flip-card';
                
                if (isActive) card.classList.add('active');
                if (isCompleted) card.classList.add('completed');
                
                const statusText = isCompleted ? '已完成' : (isActive ? '可打卡' : '进行中');
                
                card.innerHTML = `
                    <div class="flip-card-inner">
                        <div class="flip-card-front">
                            <div class="flip-card-visual">
                                <span class="flip-card-icon">${activity.icon || '🎯'}</span>
                            </div>
                            <div class="flip-card-label">
                                <span class="flip-card-name">${activity.name || '未知活动'}</span>
                                <span class="flip-card-meta">${statusText}</span>
                            </div>
                        </div>
                        <div class="flip-card-back">
                            <div class="flip-card-back-content">
                                <h4>${activity.name || '未知活动'}</h4>
                                <p class="flip-card-desc">${activity.description || '暂无描述'}</p>
                                <p class="flip-card-time">⏰ ${timeSlots.join(' / ') || '待定'}</p>
                                <div class="activity-progress">
                                    <div class="activity-progress-bar">
                                        <div class="activity-progress-fill" style="width: ${activity.progress || 0}%"></div>
                                    </div>
                                    <div class="activity-progress-text">
                                        <span>进度</span>
                                        <span>${activity.count || 0} / ${activity.required || 20}</span>
                                    </div>
                                </div>
                                <span class="activity-status-tag">${isCompleted ? '✓ 已完成' : (isActive ? '🔥 可打卡' : '⏳ 进行中')}</span>
                            </div>
                        </div>
                    </div>
                `;
                
                grid.appendChild(card);
            });
        }

        function renderAchievements() {
            const grid = document.getElementById('achievementsGrid');
            grid.innerHTML = '';
            
            achievementsData.forEach(achievement => {
                const isUnlocked = userAchievements[achievement.id]?.unlocked || false;
                const progress = userAchievements[achievement.id]?.progress || 0;
                const unlockTime = userAchievements[achievement.id]?.unlock_time || null;
                
                if (currentAchievementFilter === 'unlocked' && !isUnlocked) return;
                if (currentAchievementFilter === 'locked' && isUnlocked) return;
                if (currentAchievementFilter === 'hidden' && !achievement.hidden) return;
                
                const card = document.createElement('div');
                card.className = 'flip-card achievement-flip-card';
                card.classList.add(achievement.rarity);
                
                if (isUnlocked) {
                    card.classList.add('earned');
                } else {
                    card.classList.add('locked');
                }
                
                if (achievement.hidden && !isUnlocked) {
                    card.classList.add('hidden');
                }
                
                const displayIcon = achievement.hidden && !isUnlocked ? '❓' : achievement.icon;
                const displayName = achievement.hidden && !isUnlocked ? '???' : achievement.name;
                const displayDesc = achievement.hidden && !isUnlocked ? '完成隐藏条件后解锁' : achievement.desc;
                
                let progressPercent = 0;
                if (!isUnlocked && achievement.type !== 'hidden_condition') {
                    const currentValue = getAchievementCurrentValue(achievement.type);
                    progressPercent = Math.min(100, Math.round((currentValue / achievement.target) * 100));
                }
                
                card.innerHTML = `
                    <div class="flip-card-inner">
                        <div class="flip-card-front">
                            <div class="flip-card-visual">
                                <span class="flip-card-icon">${displayIcon}</span>
                            </div>
                            <div class="flip-card-label">
                                <span class="flip-card-name">${displayName}</span>
                                <span class="flip-card-meta">${getRarityText(achievement.rarity)}</span>
                            </div>
                        </div>
                        <div class="flip-card-back">
                            <div class="flip-card-back-content">
                                <h4>${displayName}</h4>
                                <span class="achievement-rarity-tag">${getRarityText(achievement.rarity)}</span>
                                <p class="flip-card-desc">${displayDesc}</p>
                                ${!isUnlocked && achievement.type !== 'hidden_condition' ? `
                                <div class="achievement-progress">
                                    <div class="achievement-progress-bar">
                                        <div class="achievement-progress-fill" style="width: ${progressPercent}%"></div>
                                    </div>
                                    <span class="achievement-progress-text">${progressPercent}% 完成</span>
                                </div>
                                ` : ''}
                                ${isUnlocked && unlockTime ? `
                                <div class="achievement-unlock-time">解锁于 ${formatUnlockTime(unlockTime)}</div>
                                ` : (isUnlocked ? '<div class="achievement-unlock-time">已解锁 ✓</div>' : '')}
                            </div>
                        </div>
                    </div>
                `;
                
                grid.appendChild(card);
            });
        }

        function getAchievementCurrentValue(type) {
            const totalCheckins = parseInt(document.getElementById('checkinTotal').textContent) || 0;
            const streak = parseInt(document.getElementById('checkinStreak').textContent) || 0;
            
            switch (type) {
                case 'checkin_count':
                    return totalCheckins;
                case 'streak_days':
                    return streak;
                case 'unique_places':
                    return userAchievements.unique_places_count || 0;
                default:
                    return 0;
            }
        }

        function getRarityText(rarity) {
            const rarityMap = {
                'common': '普通',
                'rare': '稀有',
                'epic': '史诗',
                'legendary': '传说'
            };
            return rarityMap[rarity] || '普通';
        }

        function formatUnlockTime(time) {
            if (!time) return '';
            const date = new Date(time);
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
        }

        function updateAchievementsHeader() {
            const unlockedCount = achievementsData.filter(a => userAchievements[a.id]?.unlocked).length;
            const totalCount = achievementsData.length;
            const percent = Math.round((unlockedCount / totalCount) * 100);
            
            document.getElementById('achievementsUnlocked').textContent = unlockedCount;
            document.getElementById('achievementsTotal').textContent = totalCount;
            document.getElementById('achievementsPercent').textContent = `${percent}%`;
        }

        function filterAchievements(filter) {
            currentAchievementFilter = filter;
            
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            renderAchievements();
        }

        async function loadCommunityFeed() {
            const feed = document.getElementById('communityFeed');
            feed.innerHTML = '<div class="loading"><div class="loading-spinner"></div></div>';
            
            try {
                const response = await fetch('/api/community/feed', {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();
                
                if (!data.success || !data.data || data.data.length === 0) {
                    feed.innerHTML = '<div class="empty-state"><div class="empty-icon">📱</div><p>暂无动态</p></div>';
                    return;
                }
                
                feed.innerHTML = '';
                data.data.forEach(post => {
                    const postCard = document.createElement('div');
                    postCard.className = 'post-card';
                    
                    postCard.innerHTML = `
                        <div class="post-header">
                            <div class="post-avatar">${post.user_nickname?.charAt(0) || '👤'}</div>
                            <div class="post-author">
                                <div class="post-author-name">${post.user_nickname || '匿名用户'}</div>
                                <div class="post-time">刚刚</div>
                            </div>
                        </div>
                        <div class="post-content">${post.content}</div>
                        <div class="post-actions">
                            <div class="post-action ${post.is_liked ? 'liked' : ''}" onclick="toggleLike(${post.id})">
                                <span>❤️</span>
                                <span>${post.likes_count || 0}</span>
                            </div>
                            <div class="post-action" onclick="showComments(${post.id})">
                                <span>💬</span>
                                <span>${post.comments_count || 0}</span>
                            </div>
                        </div>
                    `;
                    
                    feed.appendChild(postCard);
                });
            } catch (error) {
                console.error('加载社区动态失败:', error);
                feed.innerHTML = '<div class="empty-state"><div class="empty-icon">❌</div><p>加载失败</p></div>';
            }
        }

        async function createPost() {
            const content = document.getElementById('postContent').value.trim();
            if (!content) return;
            
            try {
                const response = await fetch(`/api/community/post?content=${encodeURIComponent(content)}`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('postContent').value = '';
                    loadCommunityFeed();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                console.error('发布失败:', error);
                alert('发布失败');
            }
        }

        async function toggleLike(postId) {
            try {
                await fetch(`/api/community/like?post_id=${postId}`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                loadCommunityFeed();
            } catch (error) {
                console.error('点赞失败:', error);
            }
        }

        function showComments(postId) {
            alert('评论功能开发中...');
        }

        async function login() {
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const rememberMe = document.getElementById('rememberMe').checked;
            
            if (!email || !password) {
                alert('请输入邮箱和密码');
                return;
            }
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password, remember_me: rememberMe })
                });
                const data = await response.json();
                
                console.log('登录响应:', data);
                
                if (data.access_token) {
                    currentToken = data.access_token;
                    currentUser = { 
                        id: data.user.id,
                        nickname: data.user.nickname, 
                        email: data.user.email 
                    };
                    
                    if (rememberMe) {
                        localStorage.setItem('wut_token', currentToken);
                        localStorage.setItem('wut_user', JSON.stringify(currentUser));
                    } else {
                        sessionStorage.setItem('wut_token', currentToken);
                        sessionStorage.setItem('wut_user', JSON.stringify(currentUser));
                    }
                    
                    showProfile();
                    alert('登录成功！');
                } else if (data.success === false) {
                    alert('登录失败：' + data.message);
                } else {
                    alert('登录失败：' + JSON.stringify(data));
                }
            } catch (error) {
                console.error('登录失败:', error);
                alert('登录失败：' + error);
            }
        }

        function showRegister() {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'block';
            document.getElementById('forgotPasswordForm').style.display = 'none';
            clearValidationMessages();
        }

        function showLogin() {
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('registerForm').style.display = 'none';
            document.getElementById('forgotPasswordForm').style.display = 'none';
            clearValidationMessages();
        }

        function showForgotPassword() {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'none';
            document.getElementById('forgotPasswordForm').style.display = 'block';
        }

        function clearValidationMessages() {
            document.getElementById('nicknameValidation').textContent = '';
            document.getElementById('emailValidation').textContent = '';
            document.getElementById('passwordValidation').textContent = '';
            document.getElementById('confirmPasswordValidation').textContent = '';
        }

        function validateNickname(nickname) {
            const regex = /^[\u4e00-\u9fa5a-zA-Z0-9_]{2,20}$/;
            if (!nickname) return '请输入昵称';
            if (!regex.test(nickname)) return '昵称需2-20个字符，允许中英文、数字和下划线';
            return '';
        }

        function validateEmail(email) {
            const regex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
            if (!email) return '请输入邮箱';
            if (!regex.test(email)) return '请输入有效的邮箱地址';
            return '';
        }

        function validatePassword(password) {
            if (!password) return '请输入密码';
            if (password.length < 8 || password.length > 20) return '密码长度需8-20位';
            
            const hasUpper = /[A-Z]/.test(password);
            const hasLower = /[a-z]/.test(password);
            const hasDigit = /[0-9]/.test(password);
            const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?`~]/.test(password);
            
            let count = 0;
            if (hasUpper) count++;
            if (hasLower) count++;
            if (hasDigit) count++;
            if (hasSpecial) count++;
            
            if (count < 2) return '密码需包含大小写字母、数字、特殊符号至少两种组合';
            return '';
        }

        async function register() {
            const nickname = document.getElementById('regNickname').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('regConfirmPassword').value;
            
            const nicknameError = validateNickname(nickname);
            const emailError = validateEmail(email);
            const passwordError = validatePassword(password);
            
            document.getElementById('nicknameValidation').textContent = nicknameError;
            document.getElementById('emailValidation').textContent = emailError;
            document.getElementById('passwordValidation').textContent = passwordError;
            
            if (password !== confirmPassword) {
                document.getElementById('confirmPasswordValidation').textContent = '两次输入的密码不一致';
                return;
            }
            document.getElementById('confirmPasswordValidation').textContent = '';
            
            if (nicknameError || emailError || passwordError) {
                return;
            }
            
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nickname, email, password, confirm_password: confirmPassword })
                });
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message + '\n\n请前往邮箱查看验证链接激活账号');
                    showLogin();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                console.error('注册失败:', error);
                alert('注册失败');
            }
        }

        async function forgotPassword() {
            const email = document.getElementById('forgotEmail').value;
            
            if (!email) {
                alert('请输入邮箱地址');
                return;
            }
            
            try {
                const response = await fetch('/api/auth/forgot-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `email=${encodeURIComponent(email)}`
                });
                const data = await response.json();
                
                alert(data.message);
                showLogin();
            } catch (error) {
                console.error('发送失败:', error);
                alert('发送失败');
            }
        }

        function checkAuth() {
            if (currentToken) {
                showProfile();
            } else {
                document.getElementById('loginForm').style.display = 'block';
                document.getElementById('profileContent').style.display = 'none';
            }
        }

        function showProfile() {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'none';
            document.getElementById('forgotPasswordForm').style.display = 'none';
            document.getElementById('profileContent').style.display = 'block';
            document.getElementById('profileName').textContent = currentUser?.nickname || '用户';
            updateMontoniNav('profile');
            loadProfile();
        }

        function showEditProfile() {
            alert('编辑资料功能开发中...');
        }

        function logout() {
            currentToken = null;
            currentUser = null;
            localStorage.removeItem('wut_token');
            localStorage.removeItem('wut_user');
            sessionStorage.removeItem('wut_token');
            sessionStorage.removeItem('wut_user');
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('registerForm').style.display = 'none';
            document.getElementById('forgotPasswordForm').style.display = 'none';
            document.getElementById('profileContent').style.display = 'none';
            applyProfileBackground('');
            updateMontoniNav('profile');
        }

        let selectedAvatar = '';
        let selectedStatus = '';

        function isImageAvatar(avatar) {
            return avatar && (
                avatar.startsWith('data:image/') ||
                avatar.startsWith('/static/') ||
                avatar.startsWith('http')
            );
        }

        function renderUserAvatarHtml(avatar, nickname, className = 'post-avatar') {
            const name = nickname || '用户';
            if (isImageAvatar(avatar)) {
                const safeUrl = avatar.replace(/'/g, "\\'");
                return `<div class="${className} has-image" style="background-image:url('${safeUrl}')"></div>`;
            }
            const display = avatar || name.charAt(0) || '👤';
            return `<div class="${className}">${display}</div>`;
        }

        function applyAvatarToElement(element, avatar, fallback = '👤') {
            if (!element) return;
            if (isImageAvatar(avatar)) {
                element.style.backgroundImage = `url(${avatar})`;
                element.style.backgroundSize = 'cover';
                element.style.backgroundPosition = 'center';
                element.textContent = '';
                element.classList.add('has-image');
            } else {
                element.textContent = avatar || fallback;
                element.style.backgroundImage = '';
                element.style.backgroundSize = '';
                element.style.backgroundPosition = '';
                element.classList.remove('has-image');
            }
        }

        function applyProfileBackground(url) {
            const profileTab = document.getElementById('profile');
            const bgEl = document.getElementById('profileCustomBg');
            const resetBtn = document.getElementById('profileBgResetBtn');
            if (!profileTab || !bgEl) return;

            if (url) {
                bgEl.style.backgroundImage = `url(${url})`;
                profileTab.classList.add('has-custom-bg');
                if (resetBtn) resetBtn.style.display = 'inline-flex';
            } else {
                bgEl.style.backgroundImage = '';
                profileTab.classList.remove('has-custom-bg');
                if (resetBtn) resetBtn.style.display = 'none';
            }
        }

        async function handleProfileBgUpload(event) {
            const file = event.target.files[0];
            if (!file || !currentToken) return;

            if (file.size > 5 * 1024 * 1024) {
                alert('背景图片不能超过 5MB');
                event.target.value = '';
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/auth/profile/background', {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` },
                    body: formData
                });
                const data = await response.json();
                if (data.success && data.data?.url) {
                    applyProfileBackground(data.data.url);
                } else {
                    alert(data.message || '上传失败');
                }
            } catch (error) {
                console.error('上传背景失败:', error);
                alert('上传失败');
            }
            event.target.value = '';
        }

        async function resetProfileBackground() {
            if (!currentToken) return;
            if (!confirm('确定恢复默认背景？')) return;

            try {
                const response = await fetch('/api/auth/profile/background', {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();
                if (data.success) {
                    applyProfileBackground('');
                } else {
                    alert(data.message || '操作失败');
                }
            } catch (error) {
                console.error('清除背景失败:', error);
                alert('操作失败');
            }
        }

        async function loadProfile() {
            if (!currentToken) return;
            
            try {
                const response = await fetch('/api/auth/profile', {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();
                
                if (data.success && data.data) {
                    const profile = data.data;
                    document.getElementById('profileName').textContent = profile.nickname;
                    document.getElementById('profileEmail').textContent = profile.email;
                    
                    applyAvatarToElement(
                        document.getElementById('profileAvatar'),
                        profile.avatar,
                        '👤'
                    );
                    
                    document.getElementById('profileBio').textContent = profile.bio || '暂无签名';
                    document.getElementById('profileStatus').textContent = profile.status || '';
                    applyProfileBackground(profile.profile_background || '');
                }
            } catch (error) {
                console.error('加载个人信息失败:', error);
            }
            
            await loadProfileStats();
        }

        async function loadProfileStats() {
            if (!currentToken) return;
            
            try {
                const checkinResponse = await fetch('/api/checkin/statistics', {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const checkinData = await checkinResponse.json();
                
                if (checkinData.success && checkinData.data) {
                    document.getElementById('profileCheckins').textContent = checkinData.data.total_checkins || 0;
                }
                
                const fitnessResponse = await fetch('/api/fitness/statistics?period=all', {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const fitnessData = await fitnessResponse.json();
                
                if (fitnessData.success && fitnessData.data) {
                    document.getElementById('profileWorkouts').textContent = fitnessData.data.workout_count || 0;
                }
                
                const postsResponse = await fetch('/api/community/user-posts?page=1&page_size=1', {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const postsData = await postsResponse.json();
                
                if (postsData.success && postsData.data) {
                    document.getElementById('profilePosts').textContent = postsData.data.total || 0;
                }
                
            } catch (error) {
                console.error('加载个人统计数据失败:', error);
            }
        }

        function showEditProfile() {
            loadProfile();
            document.getElementById('editBio').value = document.getElementById('profileBio').textContent || '';
            document.getElementById('statusPreview').textContent = document.getElementById('profileStatus').textContent || '选择一个状态';
            selectedStatus = document.getElementById('profileStatus').textContent || '';
            document.querySelectorAll('.status-btn').forEach(btn => btn.classList.remove('selected'));
            document.querySelectorAll('.status-btn').forEach(btn => {
                if (btn.textContent === selectedStatus) {
                    btn.classList.add('selected');
                }
            });
            document.getElementById('editProfileModal').style.display = 'flex';
        }

        function closeEditProfile() {
            document.getElementById('editProfileModal').style.display = 'none';
            selectedStatus = '';
        }

        function selectStatus(status) {
            selectedStatus = status;
            document.getElementById('statusPreview').textContent = status;
            document.querySelectorAll('.status-btn').forEach(btn => btn.classList.remove('selected'));
            document.querySelectorAll('.status-btn').forEach(btn => {
                if (btn.textContent === status) {
                    btn.classList.add('selected');
                }
            });
        }

        async function saveProfile() {
            const bio = document.getElementById('editBio').value;
            
            const promises = [];
            
            if (bio) {
                promises.push(fetch('/api/auth/profile', {
                    method: 'PUT',
                    headers: { 
                        'Authorization': `Bearer ${currentToken}`,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `bio=${encodeURIComponent(bio)}`
                }));
            }
            
            if (selectedStatus) {
                promises.push(fetch('/api/auth/status', {
                    method: 'POST',
                    headers: { 
                        'Authorization': `Bearer ${currentToken}`,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `status=${encodeURIComponent(selectedStatus)}`
                }));
            }
            
            try {
                await Promise.all(promises);
                await loadProfile();
                closeEditProfile();
                alert('保存成功！');
            } catch (error) {
                console.error('保存失败:', error);
                alert('保存失败');
            }
        }

        function showAvatarPicker() {
            selectedAvatar = document.getElementById('profileAvatar').textContent;
            document.querySelectorAll('.avatar-option').forEach(btn => btn.classList.remove('selected'));
            document.querySelectorAll('.avatar-option').forEach(btn => {
                if (btn.textContent === selectedAvatar) {
                    btn.classList.add('selected');
                }
            });
            document.getElementById('avatarPickerModal').style.display = 'flex';
        }

        function closeAvatarPicker() {
            document.getElementById('avatarPickerModal').style.display = 'none';
            selectedAvatar = '';
        }

        let uploadedAvatarData = null;

        function handleAvatarUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                uploadedAvatarData = e.target.result;
                document.getElementById('previewImage').src = e.target.result;
                document.getElementById('uploadedAvatarPreview').style.display = 'block';
                selectedAvatar = '';
                document.querySelectorAll('.avatar-option').forEach(btn => btn.classList.remove('selected'));
            };
            reader.readAsDataURL(file);
        }

        function selectAvatar(avatar) {
            selectedAvatar = avatar;
            uploadedAvatarData = null;
            document.getElementById('uploadedAvatarPreview').style.display = 'none';
            document.querySelectorAll('.avatar-option').forEach(btn => btn.classList.remove('selected'));
            document.querySelectorAll('.avatar-option').forEach(btn => {
                if (btn.textContent === avatar) {
                    btn.classList.add('selected');
                }
            });
        }

        getCurrentLocation();
        
        window.addEventListener('load', function() {
            const savedToken = localStorage.getItem('wut_token') || sessionStorage.getItem('wut_token');
            const savedUser = localStorage.getItem('wut_user') || sessionStorage.getItem('wut_user');
            
            if (savedToken && savedUser) {
                currentToken = savedToken;
                currentUser = JSON.parse(savedUser);
            }
            
            checkAuth();
            updateMontoniNav(document.querySelector('.tab-content.active')?.id || 'home');
            
            setTimeout(() => {
                initMapLazy();
            }, 1000);
        });

        async function saveAvatar() {
            if (!selectedAvatar && !uploadedAvatarData) {
                alert('请先选择或上传头像');
                return;
            }
            
            if (!currentToken) {
                alert('请先登录');
                return;
            }
            
            try {
                const avatarData = uploadedAvatarData || selectedAvatar;
                
                const response = await fetch('/api/auth/profile', {
                    method: 'PUT',
                    headers: { 
                        'Authorization': `Bearer ${currentToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ avatar: avatarData })
                });
                const data = await response.json();
                
                if (data.success) {
                    if (uploadedAvatarData) {
                    applyAvatarToElement(document.getElementById('profileAvatar'), uploadedAvatarData);
                } else {
                    applyAvatarToElement(document.getElementById('profileAvatar'), selectedAvatar, '👤');
                }
                    closeAvatarPicker();
                    alert('头像保存成功！');
                } else {
                    alert(data.message || '保存失败');
                }
            } catch (error) {
                console.error('保存头像失败:', error);
                alert('保存失败：' + error.message);
            }
        }

        // 社区页面功能

        let uploadedImages = [];
        let currentPreviewIndex = 0;
        let previewImages = [];

        function triggerImageUpload() {
            document.getElementById('imageUploadInput').click();
        }

        function handleImageUpload(event) {
            const files = event.target.files;
            if (!files || files.length === 0) return;

            const remainingSlots = 9 - uploadedImages.length;
            const filesToProcess = Array.from(files).slice(0, remainingSlots);

            filesToProcess.forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const imageData = {
                        id: Date.now() + index,
                        file: file,
                        url: e.target.result,
                        progress: 0,
                        uploaded: false
                    };
                    uploadedImages.push(imageData);
                    renderUploadedImages();
                    
                    simulateUpload(imageData);
                };
                reader.readAsDataURL(file);
            });

            event.target.value = '';
        }

        function simulateUpload(imageData) {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    imageData.uploaded = true;
                }
                imageData.progress = progress;
                renderUploadedImages();
            }, 200);
        }

        function renderUploadedImages() {
            const grid = document.getElementById('uploadedImagesGrid');
            const container = document.getElementById('imageUploadContainer');
            const btn = document.getElementById('imageUploadBtn');

            if (uploadedImages.length > 0) {
                container.classList.add('has-images');
                btn.style.display = uploadedImages.length < 9 ? 'flex' : 'none';
            } else {
                container.classList.remove('has-images');
                btn.style.display = 'flex';
            }

            grid.innerHTML = uploadedImages.map((image, index) => `
                <div class="uploaded-image-item">
                    <img src="${image.url}" alt="图片${index + 1}">
                    <button class="image-delete-btn" onclick="removeUploadedImage(${image.id})">×</button>
                    ${!image.uploaded ? `
                    <div class="image-progress">
                        <div class="image-progress-fill" style="width: ${image.progress}%"></div>
                    </div>
                    ` : ''}
                </div>
            `).join('');
        }

        function removeUploadedImage(id) {
            uploadedImages = uploadedImages.filter(img => img.id !== id);
            renderUploadedImages();
        }

        function getPostLocation() {
            if (!navigator.geolocation) {
                alert('您的浏览器不支持位置获取');
                return;
            }

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    await fetchLocationName(lat, lng);
                },
                (error) => {
                    console.error('获取位置失败:', error);
                    alert('获取位置失败，请重试');
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        }

        async function fetchLocationName(lat, lng) {
            try {
                const response = await fetch(`/api/community/reverse-geocode?lat=${lat}&lng=${lng}`);
                const data = await response.json();
                
                if (data.success && data.data) {
                    const address = data.data.place_name;
                    const campus = data.data.campus || '';
                    
                    document.getElementById('postLocationName').value = address;
                    document.getElementById('postCampus').value = campus;
                    document.getElementById('postLocationInfo').innerHTML = `
                        <div class="location-name">📍 ${address}</div>
                        ${campus ? `<div class="location-campus">🏛️ ${campus}</div>` : ''}
                    `;
                } else {
                    document.getElementById('postLocationInfo').innerHTML = '<div class="location-empty">无法获取位置信息</div>';
                }
            } catch (error) {
                console.error('获取位置名称失败:', error);
                document.getElementById('postLocationInfo').innerHTML = '<div class="location-empty">获取位置信息失败</div>';
            }
        }

        function identifyCampus(lat, lng) {
            const nanhu = { lat: 30.5075, lng: 114.3795, radius: 0.005 };
            const mfs = { lat: 30.5358, lng: 114.3645, radius: 0.005 };
            const yjt = { lat: 30.5735, lng: 114.3505, radius: 0.005 };

            const distanceToNanhu = calculateDistance(lat, lng, nanhu.lat, nanhu.lng) / 1000;
            const distanceToMfs = calculateDistance(lat, lng, mfs.lat, mfs.lng) / 1000;
            const distanceToYjt = calculateDistance(lat, lng, yjt.lat, yjt.lng) / 1000;

            if (distanceToNanhu < nanhu.radius) return '南湖校区';
            if (distanceToMfs < mfs.radius) return '马房山校区';
            if (distanceToYjt < yjt.radius) return '余家头校区';
            return '武汉理工大学';
        }

        async function createPost() {
            const content = document.getElementById('postContent').value.trim();
            const locationName = document.getElementById('postLocationName').value;
            const campus = document.getElementById('postCampus').value;

            if (!content && uploadedImages.length === 0) {
                alert('请输入内容或添加图片');
                return;
            }

            try {
                let imageUrls = [];
                if (uploadedImages.length > 0) {
                    const formData = new FormData();
                    uploadedImages.forEach(img => {
                        if (img.file) {
                            formData.append('files', img.file);
                        }
                    });

                    const uploadResponse = await fetch('/api/community/upload-images', {
                        method: 'POST',
                        headers: { Authorization: `Bearer ${currentToken}` },
                        body: formData
                    });
                    const uploadData = await uploadResponse.json();

                    if (uploadData.success && uploadData.data) {
                        imageUrls = uploadData.data.map(img => img.image_url);
                    } else {
                        alert(uploadData.message || '图片上传失败');
                        return;
                    }
                }

                const postFormData = new FormData();
                if (content) postFormData.append('content', content);
                if (locationName) postFormData.append('location_name', locationName);
                if (campus) postFormData.append('campus', campus);
                if (imageUrls.length > 0) {
                    postFormData.append('images', JSON.stringify(imageUrls));
                }

                const response = await fetch('/api/community/post', {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` },
                    body: postFormData
                });
                const data = await response.json();

                if (data.success) {
                    document.getElementById('postContent').value = '';
                    document.getElementById('postLocationName').value = '';
                    document.getElementById('postCampus').value = '';
                    document.getElementById('postLocationInfo').innerHTML = '<div class="location-empty">点击获取当前位置</div>';
                    uploadedImages = [];
                    renderUploadedImages();
                    loadCommunityFeed();
                } else {
                    alert(data.message || '发布失败');
                }
            } catch (error) {
                console.error('发布失败:', error);
                alert('发布失败：' + error.message);
            }
        }

        async function loadCommunityFeed() {
            const feed = document.getElementById('communityFeed');
            feed.innerHTML = '<div class="loading"><div class="loading-spinner"></div></div>';

            try {
                const response = await fetch('/api/community/feed', {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();

                if (!data.success || !data.data || data.data.length === 0) {
                    feed.innerHTML = '<div class="empty-state"><div class="empty-icon">📱</div><p>暂无动态</p></div>';
                    return;
                }

                feed.innerHTML = data.data.map(post => renderPost(post)).join('');
                initPostImageFans();
            } catch (error) {
                console.error('加载社区动态失败:', error);
                feed.innerHTML = '<div class="empty-state"><div class="empty-icon">❌</div><p>加载失败</p></div>';
            }
        }

        function buildFanImagesHtml(images) {
            if (!images || images.length === 0) return '';
            const urls = images.map(i => i.url);
            const count = images.length;
            const fanClass = count === 1 ? 'post-images-fan single' : 'post-images-fan';
            const center = (count - 1) / 2;

            const items = images.map((img, index) => {
                const offset = index - center;
                const rotate = offset * 8;
                const offsetAbs = Math.abs(Math.round(offset));
                return `
                    <div class="post-fan-item"
                         style="--offset: ${offset}; --rotate: ${rotate}deg; --offset-abs: ${offsetAbs};"
                         data-index="${index}"
                         title="双击查看原图">
                        <img src="${img.url}" alt="图片${index + 1}" loading="lazy" draggable="false">
                    </div>
                `;
            }).join('');

            return `<div class="${fanClass}" data-count="${count}" data-urls="${encodeURIComponent(JSON.stringify(urls))}">${items}</div>`;
        }

        function initPostImageFans() {
            document.querySelectorAll('.post-images-fan').forEach(fan => {
                if (fan.dataset.fanInit) return;
                fan.dataset.fanInit = '1';

                const items = fan.querySelectorAll('.post-fan-item');
                const proximity = 140;

                fan.addEventListener('mousemove', (e) => {
                    const rect = fan.getBoundingClientRect();
                    const pad = 60;
                    const nearFan = e.clientX >= rect.left - pad && e.clientX <= rect.right + pad &&
                                    e.clientY >= rect.top - pad && e.clientY <= rect.bottom + pad;
                    fan.classList.toggle('is-expanded', nearFan);

                    items.forEach(item => {
                        const ir = item.getBoundingClientRect();
                        const d = Math.hypot(
                            e.clientX - (ir.left + ir.width / 2),
                            e.clientY - (ir.top + ir.height / 2)
                        );
                        item.classList.toggle('is-focused', nearFan && d < proximity);
                    });
                });

                fan.addEventListener('mouseleave', () => {
                    fan.classList.remove('is-expanded');
                    items.forEach(item => item.classList.remove('is-focused'));
                });

                fan.addEventListener('dblclick', (e) => {
                    const item = e.target.closest('.post-fan-item');
                    if (!item) return;
                    e.preventDefault();
                    e.stopPropagation();
                    try {
                        const urls = JSON.parse(decodeURIComponent(fan.dataset.urls || '%5B%5D'));
                        const index = parseInt(item.dataset.index, 10) || 0;
                        if (urls.length) openImagePreview(urls, index);
                    } catch (err) {
                        console.error('打开原图失败:', err);
                    }
                });
            });
        }

        function renderPost(post) {
            const imagesHtml = buildFanImagesHtml(post.images);

            const locationHtml = post.location ? `
                <div class="post-location">📍 ${post.location}</div>
            ` : '';
            
            const isAuthor = currentUser && post.user_id === currentUser.id;
            const deleteBtn = isAuthor ? `
                <button class="post-delete-btn" onclick="deletePost(${post.id})" title="删除">🗑️</button>
            ` : '';

            return `
                <div class="post-card">
                    <div class="post-header">
                        ${deleteBtn}
                        ${renderUserAvatarHtml(post.user_avatar, post.user_nickname)}
                        <div class="post-author">
                            <div class="post-author-name">${post.user_nickname || '匿名用户'}</div>
                            <div class="post-time">${formatPostTime(post.created_at)}</div>
                        </div>
                    </div>
                    <div class="post-content">${post.content}</div>
                    ${imagesHtml}
                    ${locationHtml}
                    <div class="post-actions">
                        <div class="post-action ${post.is_liked ? 'liked' : ''}" onclick="toggleLike(${post.id})">
                            <span>❤️</span>
                            <span>${post.likes_count || 0}</span>
                        </div>
                        <div class="post-action" onclick="toggleComments(${post.id})">
                            <span>💬</span>
                            <span>${post.comments_count || 0}</span>
                        </div>
                        <div class="post-action ${post.is_bookmarked ? 'bookmarked' : ''}" onclick="toggleBookmark(${post.id})">
                            <span>⭐</span>
                            <span>${post.bookmarks_count || 0}</span>
                        </div>
                    </div>
                    <div class="comments-section" id="comments-${post.id}">
                        <div class="comments-list" id="comments-list-${post.id}"></div>
                        <div class="comment-input">
                            <input type="text" class="input-field" id="comment-input-${post.id}" placeholder="写下你的评论..." onkeydown="handleCommentKeydown(event, ${post.id})">
                            <button class="btn btn-primary btn-sm" onclick="submitComment(${post.id})">发送</button>
                        </div>
                    </div>
                </div>
            `;
        }

        function getImageGridClass(count) {
            if (count === 1) return 'one-image';
            if (count === 2) return 'two-images';
            return 'multi-images';
        }

        function formatPostTime(timestamp) {
            if (!timestamp) return '刚刚';
            const now = new Date();
            const postTime = new Date(timestamp);
            const diff = now.getTime() - postTime.getTime();
            
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);

            if (minutes < 1) return '刚刚';
            if (minutes < 60) return `${minutes}分钟前`;
            if (hours < 24) return `${hours}小时前`;
            if (days < 7) return `${days}天前`;
            return postTime.toLocaleDateString('zh-CN');
        }

        async function toggleLike(postId) {
            try {
                await fetch(`/api/community/like?post_id=${postId}`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                loadCommunityFeed();
            } catch (error) {
                console.error('点赞失败:', error);
            }
        }

        async function deletePost(postId) {
            if (!confirm('确定要删除这条动态吗？')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/community/post/${postId}`, {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();
                
                if (data.success) {
                    alert('删除成功');
                    loadCommunityFeed();
                } else {
                    alert(data.message || '删除失败');
                }
            } catch (error) {
                console.error('删除失败:', error);
                alert('删除失败：' + error.message);
            }
        }

        async function toggleBookmark(postId) {
            try {
                await fetch(`/api/community/bookmark?post_id=${postId}`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                loadCommunityFeed();
            } catch (error) {
                console.error('收藏失败:', error);
            }
        }

        async function toggleComments(postId) {
            const section = document.getElementById(`comments-${postId}`);
            section.classList.toggle('show');

            if (section.classList.contains('show')) {
                await loadComments(postId);
            }
        }

        async function loadComments(postId) {
            try {
                const response = await fetch(`/api/community/comments?post_id=${postId}`, {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                const data = await response.json();

                if (data.success && data.data) {
                    const list = document.getElementById(`comments-list-${postId}`);
                    list.innerHTML = data.data.map(comment => renderComment(comment)).join('');
                }
            } catch (error) {
                console.error('加载评论失败:', error);
            }
        }

        function renderComment(comment) {
            const repliesHtml = comment.replies && comment.replies.length > 0 ? `
                <div class="comment-reply-section">
                    ${comment.replies.map(reply => `
                        <div class="comment-reply-item">
                            ${renderUserAvatarHtml(reply.user_avatar, reply.user_nickname, 'comment-reply-avatar')}
                            <div class="comment-reply-content">
                                <span class="comment-reply-author">${reply.user_nickname || '匿名用户'}</span>
                                <span class="comment-reply-text">${reply.content}</span>
                                <div class="comment-reply-time">${formatPostTime(reply.created_at)}</div>
                            </div>
                        </div>
                    `).join('')}
                    <div class="comment-input-reply">
                        <input type="text" class="input-field" placeholder="回复..." onkeydown="handleReplyKeydown(event, ${comment.id})">
                        <button class="btn btn-secondary btn-sm" onclick="submitReply(${comment.id})">回复</button>
                    </div>
                </div>
            ` : '';

            return `
                <div class="comment-item">
                    ${renderUserAvatarHtml(comment.user_avatar, comment.user_nickname, 'comment-avatar')}
                    <div class="comment-content">
                        <span class="comment-author">${comment.user_nickname || '匿名用户'}</span>
                        <span class="comment-text">${comment.content}</span>
                        <div class="comment-time">${formatPostTime(comment.created_at)}</div>
                    </div>
                </div>
                ${repliesHtml}
            `;
        }

        async function submitComment(postId) {
            const input = document.getElementById(`comment-input-${postId}`);
            const content = input.value.trim();
            if (!content) return;

            try {
                await fetch(`/api/community/comment?post_id=${postId}&content=${encodeURIComponent(content)}`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                input.value = '';
                await loadComments(postId);
            } catch (error) {
                console.error('评论失败:', error);
                alert('评论失败');
            }
        }

        function handleCommentKeydown(event, postId) {
            if (event.key === 'Enter') {
                submitComment(postId);
            }
        }

        async function submitReply(commentId) {
            const inputs = document.querySelectorAll(`.comment-input-reply input`);
            let content = '';
            let targetInput = null;
            
            inputs.forEach(input => {
                if (input.value.trim()) {
                    content = input.value.trim();
                    targetInput = input;
                }
            });

            if (!content) return;

            try {
                await fetch(`/api/community/reply?comment_id=${commentId}&content=${encodeURIComponent(content)}`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                if (targetInput) targetInput.value = '';
                
                const postId = getPostIdFromComment(commentId);
                if (postId) await loadComments(postId);
            } catch (error) {
                console.error('回复失败:', error);
                alert('回复失败');
            }
        }

        function handleReplyKeydown(event, commentId) {
            if (event.key === 'Enter') {
                submitReply(commentId);
            }
        }

        function getPostIdFromComment(commentId) {
            const commentsSections = document.querySelectorAll('.comments-section');
            for (const section of commentsSections) {
                const sectionId = section.id;
                if (sectionId.startsWith('comments-')) {
                    const postId = sectionId.replace('comments-', '');
                    const list = document.getElementById(`comments-list-${postId}`);
                    if (list && list.innerHTML.includes(`comment-${commentId}`)) {
                        return parseInt(postId);
                    }
                }
            }
            return null;
        }

        function openImagePreview(images, index) {
            previewImages = images;
            currentPreviewIndex = index;
            updateImagePreview();
            document.getElementById('imagePreviewOverlay').classList.add('show');
            document.body.style.overflow = 'hidden';
        }

        function closeImagePreview() {
            document.getElementById('imagePreviewOverlay').classList.remove('show');
            previewImages = [];
            currentPreviewIndex = 0;
            document.body.style.overflow = '';
        }

        function updateImagePreview() {
            if (previewImages.length === 0) return;
            
            const img = document.getElementById('communityPreviewImage');
            const counter = document.getElementById('imagePreviewCounter');
            
            img.src = previewImages[currentPreviewIndex];
            counter.textContent = `${currentPreviewIndex + 1}/${previewImages.length}`;
            
            document.querySelector('.image-preview-nav.prev').style.display = currentPreviewIndex > 0 ? 'flex' : 'none';
            document.querySelector('.image-preview-nav.next').style.display = currentPreviewIndex < previewImages.length - 1 ? 'flex' : 'none';
        }

        function prevImagePreview() {
            if (currentPreviewIndex > 0) {
                currentPreviewIndex--;
                updateImagePreview();
            }
        }

        function nextImagePreview() {
            if (currentPreviewIndex < previewImages.length - 1) {
                currentPreviewIndex++;
                updateImagePreview();
            }
        }
