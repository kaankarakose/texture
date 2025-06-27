docker build -t qwen -f ./Dockerfile .
docker run -p 8187:8187 -v $(pwd):/app -v /mnt-persist/.cache_model:/cache --gpus all --name qwen qwen