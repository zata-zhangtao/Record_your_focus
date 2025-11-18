import React, { useState, useRef, useCallback } from 'react'

function App() {
  const [stream, setStream] = useState(null)
  const [lastBlob, setLastBlob] = useState(null)
  const [lastObjectUrl, setLastObjectUrl] = useState(null)
  const [status, setStatus] = useState('就绪')
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000')

  const videoRef = useRef(null)
  const imgRef = useRef(null)
  const downloadLinkRef = useRef(null)

  const setStatusMessage = useCallback((msg) => {
    setStatus(msg)
  }, [])

  const startShare = useCallback(async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      setStatusMessage('当前浏览器不支持屏幕共享')
      return
    }

    try {
      const mediaStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          displaySurface: 'monitor',
          frameRate: 30
        },
        audio: false
      })

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }

      // 共享停止时自动清理
      const [track] = mediaStream.getVideoTracks()
      track.addEventListener('ended', stopShare)

      setStream(mediaStream)
      setStatusMessage('屏幕共享已开始')
    } catch (err) {
      console.error(err)
      setStatusMessage('用户取消或发生错误')
    }
  }, [setStatusMessage])

  const stopShare = useCallback(() => {
    if (stream) {
      for (const track of stream.getTracks()) track.stop()
      setStream(null)
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null
    }

    setStatusMessage('屏幕共享已停止')
  }, [stream, setStatusMessage])

  const canSnap = useCallback(() => {
    return !!(videoRef.current && videoRef.current.videoWidth && videoRef.current.videoHeight)
  }, [])

  const takeShot = useCallback(() => {
    if (!canSnap()) {
      setStatusMessage('视频未就绪，无法截图')
      return
    }

    const video = videoRef.current
    const w = video.videoWidth
    const h = video.videoHeight
    const canvas = document.createElement('canvas')
    canvas.width = w
    canvas.height = h
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, w, h)

    canvas.toBlob((blob) => {
      if (!blob) {
        setStatusMessage('截图失败')
        return
      }

      // 清理上一次 URL
      if (lastObjectUrl) URL.revokeObjectURL(lastObjectUrl)

      const objectUrl = URL.createObjectURL(blob)
      setLastBlob(blob)
      setLastObjectUrl(objectUrl)

      if (imgRef.current) {
        imgRef.current.src = objectUrl
      }

      if (downloadLinkRef.current) {
        downloadLinkRef.current.href = objectUrl
        downloadLinkRef.current.classList.remove('hidden')
      }

      setStatusMessage(`已生成截图：${(blob.size/1024).toFixed(1)} KB`)
    }, 'image/png')
  }, [canSnap, lastObjectUrl, setStatusMessage])

  const uploadLast = useCallback(async () => {
    if (!lastBlob) {
      setStatusMessage('没有可上传的截图')
      return
    }

    const url = backendUrl.replace(/\/$/, '') + '/api/screenshot'
    const fd = new FormData()
    fd.append('file', lastBlob, 'screenshot.png')

    try {
      const res = await fetch(url, { method: 'POST', body: fd })
      if (!res.ok) throw new Error('上传失败: ' + res.status)
      const data = await res.json()
      setStatusMessage(`上传完成：${data.filename || data.path || '已保存'}`)
    } catch (e) {
      console.error(e)
      setStatusMessage('上传失败：' + e.message)
    }
  }, [lastBlob, backendUrl, setStatusMessage])

  return (
    <>
      <header>
        <h1>屏幕共享与截图</h1>
      </header>

      <main>
        <section className="controls">
          <div className="row">
            <button
              onClick={startShare}
              disabled={!!stream}
            >
              开始共享屏幕
            </button>
            <button
              onClick={stopShare}
              disabled={!stream}
            >
              停止共享
            </button>
            <button
              onClick={takeShot}
              disabled={!stream}
            >
              截图
            </button>
          </div>

          <div className="row">
            <label>后端地址：</label>
            <input
              id="backendUrl"
              type="text"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
            />
            <button
              onClick={uploadLast}
              disabled={!lastBlob}
            >
              上传最后一张截图
            </button>
          </div>
          <p className="muted">{status}</p>
        </section>

        <section className="preview">
          <div className="col">
            <h2>屏幕预览</h2>
            <video
              ref={videoRef}
              autoPlay
              playsInline
            ></video>
          </div>

          <div className="col">
            <h2>截图结果</h2>
            <img
              ref={imgRef}
              alt="截图预览"
            />
            <div className="row">
              <a
                ref={downloadLinkRef}
                href="#"
                download="screenshot.png"
                className="hidden"
              >
                下载截图
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <small className="muted">提示：部分浏览器需要 https 或 localhost 才能进行屏幕共享。</small>
      </footer>
    </>
  )
}

export default App