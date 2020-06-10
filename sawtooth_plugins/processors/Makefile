build:
	docker build -t gcr.io/plasma-weft-162417/processors:latest -f Dockerfile .

push:
	gcloud docker -- push gcr.io/plasma-weft-162417/processors:latest

restart:
	bash restart.bash