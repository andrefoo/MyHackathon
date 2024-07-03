import React, { useRef, useEffect } from 'react';
import '@tensorflow/tfjs-backend-cpu';
import '@tensorflow/tfjs-backend-webgl';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import * as tf from '@tensorflow/tfjs';

const VideoAnalyzer = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    let stream;

    const startVideo = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      } catch (err) {
        console.error('Error accessing camera: ', err);
      }
    };

    const loadModel = async () => {
      // Set up the backends
      await tf.setBackend('webgl');
      await tf.ready();

      try {
        const model = await cocoSsd.load();
        setInterval(() => detectFrame(model), 100);
      } catch (err) {
        console.error('Error loading model: ', err);
      }
    };

    const detectFrame = async (model) => {
      if (videoRef.current) {
        const predictions = await model.detect(videoRef.current);

        const ctx = canvasRef.current.getContext('2d');
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        ctx.drawImage(videoRef.current, 0, 0, ctx.canvas.width, ctx.canvas.height);

        predictions.forEach(prediction => {
          const [x, y, width, height] = prediction.bbox;
          ctx.strokeStyle = '#00FFFF';
          ctx.lineWidth = 2;
          ctx.strokeRect(x, y, width, height);
          ctx.fillStyle = '#00FFFF';
          ctx.font = '16px Arial';
          ctx.fillText(
            `${prediction.class} (${Math.round(prediction.score * 100)}%)`,
            x,
            y > 10 ? y - 5 : 10
          );
        });
      }
    };

    startVideo();
    loadModel();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div>
      <video ref={videoRef} width="600" height="400" />
      <canvas ref={canvasRef} width="600" height="400" />
    </div>
  );
};

export default VideoAnalyzer;
