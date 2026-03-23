---
title: DeepFace Detector
sdk: docker
app_port: 7860
---

# DeepFace Detection Platform
A real-time lightweight web application that detects faces and analyzes age, gender, and emotion securely in real time leveraging OpenCV and DeepFace. Built with a FastAPI websocket backend and vanilla JS.

https://ashfinashfi-deepface-detector.hf.space/

## Deployment to Hugging Face
To sync this repository with Hugging Face free-tier spaces, you can set it up as a remote locally:

```bash
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
git push --force huggingface main
```
