(() => {
  const btnStart = document.getElementById('btnStart');
  const btnStop = document.getElementById('btnStop');
  const btnShot = document.getElementById('btnShot');
  const btnUpload = document.getElementById('btnUpload');
  const backendUrlInput = document.getElementById('backendUrl');
  const statusEl = document.getElementById('status');
  const videoEl = document.getElementById('screenVideo');
  const imgEl = document.getElementById('snapshot');
  const downloadLink = document.getElementById('downloadLink');

  /** @type {MediaStream|null} */
  let stream = null;
  /** @type {Blob|null} */
  let lastBlob = null;
  let lastObjectUrl = null;

  function setStatus(msg) {
    statusEl.textContent = msg;
  }

  async function startShare() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      setStatus('当前浏览器不支持屏幕共享');
      return;
    }
    try {
      stream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          displaySurface: 'monitor',
          frameRate: 30
        },
        audio: false
      });
      videoEl.srcObject = stream;

      // 共享停止时自动清理
      const [track] = stream.getVideoTracks();
      track.addEventListener('ended', stopShare);

      btnStart.disabled = true;
      btnStop.disabled = false;
      btnShot.disabled = false;
      setStatus('屏幕共享已开始');
    } catch (err) {
      console.error(err);
      setStatus('用户取消或发生错误');
    }
  }

  function stopShare() {
    if (stream) {
      for (const track of stream.getTracks()) track.stop();
      stream = null;
    }
    videoEl.srcObject = null;
    btnStart.disabled = false;
    btnStop.disabled = true;
    btnShot.disabled = true;
    setStatus('屏幕共享已停止');
  }

  function canSnap() {
    return !!(videoEl && videoEl.videoWidth && videoEl.videoHeight);
  }

  function takeShot() {
    if (!canSnap()) {
      setStatus('视频未就绪，无法截图');
      return;
    }
    const w = videoEl.videoWidth;
    const h = videoEl.videoHeight;
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoEl, 0, 0, w, h);

    canvas.toBlob((blob) => {
      if (!blob) {
        setStatus('截图失败');
        return;
      }
      // 清理上一次 URL
      if (lastObjectUrl) URL.revokeObjectURL(lastObjectUrl);
      lastBlob = blob;
      lastObjectUrl = URL.createObjectURL(blob);
      imgEl.src = lastObjectUrl;
      downloadLink.href = lastObjectUrl;
      downloadLink.classList.remove('hidden');
      btnUpload.disabled = false;
      setStatus(`已生成截图：${(blob.size/1024).toFixed(1)} KB`);
    }, 'image/png');
  }

  async function uploadLast() {
    if (!lastBlob) {
      setStatus('没有可上传的截图');
      return;
    }
    const url = backendUrlInput.value.replace(/\/$/, '') + '/api/screenshot';
    const fd = new FormData();
    fd.append('file', lastBlob, 'screenshot.png');
    try {
      const res = await fetch(url, { method: 'POST', body: fd });
      if (!res.ok) throw new Error('上传失败: ' + res.status);
      const data = await res.json();
      setStatus(`上传完成：${data.filename || data.path || '已保存'}`);
    } catch (e) {
      console.error(e);
      setStatus('上传失败：' + e.message);
    }
  }

  btnStart.addEventListener('click', startShare);
  btnStop.addEventListener('click', stopShare);
  btnShot.addEventListener('click', takeShot);
  btnUpload.addEventListener('click', uploadLast);
})();

