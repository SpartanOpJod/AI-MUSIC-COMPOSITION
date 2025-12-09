// src/components/Waveform.jsx
import React, { useEffect, useRef } from "react";

export default function Waveform({ audioUrl }) {
  const canvasRef = useRef();

  useEffect(() => {
    if (!audioUrl) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const audio = new Audio(audioUrl);
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaElementSource(audio);
    source.connect(analyser);
    analyser.connect(audioContext.destination);

    analyser.fftSize = 2048;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(dataArray);

      ctx.fillStyle = "#000";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.lineWidth = 2;
      ctx.strokeStyle = "#6C63FF";
      ctx.beginPath();

      const sliceWidth = (canvas.width * 1.0) / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);

        x += sliceWidth;
      }
      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };

    audio.play().catch(() => {}); // autoplay may fail, ignore
    draw();
  }, [audioUrl]);

  return <canvas ref={canvasRef} width={600} height={200} className="rounded bg-gray-800" />;
}
