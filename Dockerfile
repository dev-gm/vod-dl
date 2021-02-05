FROM python
COPY vod-dl.py /tmp/
RUN pip install twitch-dl
CMD ["python", "/tmp/vod-dl.py"]
