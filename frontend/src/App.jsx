import React, { useState } from 'react'

export default function App() {
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    setPreview(URL.createObjectURL(file))
    setResult(null)
  }

  const handleSubmit = async () => {
    const input = document.querySelector('input[type=file]')
    const file = input.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setLoading(true)
    const res = await fetch('/predict', {
      method: 'POST',
      body: formData
    })

    const blob = await res.blob()
    setResult(URL.createObjectURL(blob))
    setLoading(false)
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>YOLOv8 Обнаружение объектов</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <br />
      {preview && <img src={preview} alt="original" width="300" style={{ marginTop: 10 }} />}
      <br />
      <button onClick={handleSubmit} style={{ marginTop: 10 }}>
        Обработать
      </button>
      <br />
      {loading && <p>⏳ Обработка...</p>}
      {result && (
        <div style={{ marginTop: 10 }}>
          <h4>Результат:</h4>
          <img src={result} alt="result" width="300" />
        </div>
      )}
    </div>
  )
}
